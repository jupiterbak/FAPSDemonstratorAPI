#!/usr/bin/env python

from __future__ import print_function

import datetime
import json
import logging
import os
import threading
import time

import numpy as np
from numpy.linalg import inv
import pika
import yaml
import cv2
from cv2.cv2 import *
from pip._vendor.retrying import retry

from FAPSDemonstratorAPI import Program, utils
from FAPSDemonstratorAPI.ApplicationConstants import *

logging.basicConfig(format='%(asctime)-15s [%(levelname)] [%(name)-12s] %(message)s', datefmt='%d-%b-%y %H:%M:%S')
logger = logging.getLogger('FAPS Image Stiching Service')
logger.setLevel(logging.DEBUG | logging.INFO | logging.WARNING | logging.ERROR | logging.CRITICAL)
DEMONSTRATOR_ENDPOINT = "cloud.faps.uni-erlangen.de"

TRANSFORMATION_MATRICE = {
    "CAMERA_PARAMETER": "TransformationMatrix/camera_parameter.yaml",
    "PRODUCT": "TransformationMatrix/Product_world3D.yaml",
    "MAGAZIN_0": "TransformationMatrix/Magazin_0_world3D.yaml",
    "MAGAZIN_1": "TransformationMatrix/Magazin_1_world3D.yaml",
    "MAGAZIN_2": "TransformationMatrix/Magazin_2_world3D.yaml",
    "MAGAZIN_3": "TransformationMatrix/Magazin_3_world3D.yaml",
    "MAGAZIN_4": "TransformationMatrix/Magazin_4_world3D.yaml"
}
IMG_W = 1024
IMG_H = 768


class Service:
    """This class is the class holdinfg the set of instruction that will be executed to the demonstrator."""

    def __init__(self, publish):
        self.order_queue = []
        self.image_marker_map = {}
        self.picture_to_process = []
        self.picture_marker_counter = 0
        self.target_position_counter = 0

        self.publish = publish
        self.connection = None
        self.channel = None

        self.exchange_order = None
        self.exchange_image_processing = None
        self.exchange_image_processing_pub = None
        self.exchange_order_processing_result_pub = None

        self.exchange_order_name = None
        self.exchange_image_processing_name = None
        self.exchange_image_processing_pub_name = None
        self.exchange_order_processing_result_pub_name = None

        self.exchange_conveyor_data = None
        self.exchange_conveyor_data_name = None
        self.exchange_conveyor_pub = None
        self.exchange_conveyor_pub_name = None

        self.exchange_energy_price_data = None
        self.exchange_energy_price_data_name = None

        self.queue_order = None
        self.queue_image_processing = None
        self.queue_image_processing_pub = None
        self.queue_order_processing_result_pub = None

        self.queue_conveyor_data = None
        self.queue_conveyor_pub = None

        self.queue_energy_price_data = None

        self.demonstrator_program = Program()

        # read the camera intrinsic parameters
        self.mtx = None
        self.dist = None
        self.newcameramtx = None
        self.roi = None

        # Syncho mit Conveyor
        self.Produkt_Band2_Bereit = False

        self.current_energy_price = 2.0

        # read the camera intrinsic parameters
        logger.info('Read the camera intrinsic parameters')
        with open(TRANSFORMATION_MATRICE["CAMERA_PARAMETER"]) as f:
            loadeddict = yaml.load(f, Loader=yaml.BaseLoader)
            self.mtx = loadeddict.get('camera_matrix')
            self.dist = loadeddict.get('dist_coeff')
            self.mtx = np.array(self.mtx, dtype=np.float)
            self.dist = np.array(self.dist, dtype=np.float)
            self.newcameramtx, self.roi = cv2.getOptimalNewCameraMatrix(self.mtx,
                                                                        self.dist,
                                                                        (IMG_W, IMG_H),
                                                                        1,
                                                                        (IMG_W, IMG_H))

        # Initialize the transformation matrices
        self.transformation_matrices = {
            "PRODUCT": self.get_transformation_matrix(TRANSFORMATION_MATRICE["PRODUCT"]),
            "MAGAZIN_0": self.get_transformation_matrix(TRANSFORMATION_MATRICE["MAGAZIN_0"]),
            "MAGAZIN_1": self.get_transformation_matrix(TRANSFORMATION_MATRICE["MAGAZIN_1"]),
            "MAGAZIN_2": self.get_transformation_matrix(TRANSFORMATION_MATRICE["MAGAZIN_2"]),
            "MAGAZIN_3": self.get_transformation_matrix(TRANSFORMATION_MATRICE["MAGAZIN_3"]),
            "MAGAZIN_4": self.get_transformation_matrix(TRANSFORMATION_MATRICE["MAGAZIN_4"])
        }

    def get_transformation_matrix(self, path):
        with open(path) as f:
            loadeddict = yaml.load(f, Loader=yaml.BaseLoader)
            camera_matrix = loadeddict.get('camera_matrix')
            dist_coeff = loadeddict.get('dist_coeff')
            rvect = loadeddict.get('rvect')
            tvec = loadeddict.get('tvec')
            return {
                "camera_matrix": np.array(camera_matrix, dtype=np.float),
                "dist_coeff": np.array(dist_coeff, dtype=np.float),
                "rvect": np.array(rvect, dtype=np.float),
                "tvec": np.array(tvec, dtype=np.float)
            }

    def incoming_picture_marker_callback(self, ch, method, properties, data):
        logger.info("Incoming picture markers")
        body = json.loads(data)
        if body["object"]:
            self.image_marker_map[body["object"]] = body
            self.picture_marker_counter = self.picture_marker_counter + 1

        # Check if we can process pick_and_place
        if len(self.picture_to_process) > 0 and self.picture_marker_counter >= self.picture_to_process[0]["marker_count"]:
            tmp = self.picture_to_process.pop(0)
            order = tmp["order"]
            self.picture_marker_counter = self.picture_marker_counter - tmp["marker_count"]
            self.process_order_pick_and_place(order, self.image_marker_map)

    def conveyor_data_callback(self, ch, method, properties, data):
        body = json.loads(data)
        _value = body['value']
        _DB = _value['DB33']
        self.Produkt_Band2_Bereit = _DB['Produkt_Band2_Bereit']

    def energy_price_data_callback(self, ch, method, properties, data):
        body = json.loads(data)
        _value = body['current_energy_price']
        self.current_energy_price = _value

    def incoming_order_signals_callback(self, ch, method, properties, data):
        logger.info("Incoming Order")
        body = json.loads(data)
        self.order_queue.append(body)
        self.set_conveyor_order_signal()
        if len(self.order_queue) > 0:
            current_order = self.order_queue.pop(0)
            # TODO: Add a separate process to do it
            # p_order_rslt = self.process_order_pick_and_place(current_order, self.image_marker_map)
            # if p_order_rslt is False:
            self.start_scanning_magazin(current_order)

    def connect_and_start_listening(self, _url, _port, _user, _passwd, _exchange_order, _queue_order,
                                    _exchange_image_processing,
                                    _queue_image_processing, _exchange_image_processing_pub,
                                    _queue_image_processing_pub, _exchange_order_processing_result_pub,
                                    _queue_order_processing_result_pub,
                                    _exchange_conveyor_data,
                                    _queue_conveyor_data,
                                    _exchange_energy_price_data,
                                    _queue_energy_price_data,
                                    _exchange_conveyor_pub,
                                    _queue_conveyor_pub,
                                    _callback_order,
                                    _callback_image_processing,
                                    _callback_conveyor_data,
                                    _callback_energy_price_data):
        """
            Connect the FAPSDemonstratorAPI to the demonstrator.
        :return true if the connect has been established or false otherwise.
        """
        while(True):
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(
                port=_port,
                host=_url,
                credentials=pika.PlainCredentials(_user, _passwd))
            )
            self.channel = self.connection.channel()

            self.exchange_order_name = _exchange_order
            self.exchange_order =self.channel.exchange_declare(
                exchange=_exchange_order,
                passive=False,
                durable=False,
                exchange_type='fanout'
            )

            self.exchange_image_processing_name = _exchange_image_processing
            self.exchange_image_processing = self.channel.exchange_declare(
                exchange=_exchange_image_processing,
                passive=False,
                durable=False,
                exchange_type='fanout'
            )

            self.exchange_image_processing_pub_name = _exchange_image_processing_pub
            self.exchange_image_processing = self.channel.exchange_declare(
                exchange=_exchange_image_processing_pub,
                passive=False,
                durable=False,
                exchange_type='fanout'
            )

            self.exchange_order_processing_result_pub_name = _exchange_order_processing_result_pub
            self.exchange_order_processing_result_pub = self.channel.exchange_declare(
                exchange=_exchange_order_processing_result_pub,
                passive=False,
                durable=False,
                exchange_type='fanout'
            )

            self.exchange_conveyor_data_name = _exchange_conveyor_data
            self.exchange_conveyor_data = self.channel.exchange_declare(
                exchange=_exchange_conveyor_data,
                passive=False,
                durable=False,
                exchange_type='fanout'
            )

            self.exchange_energy_price_data_name = _exchange_energy_price_data
            self.exchange_energy_price_data = self.channel.exchange_declare(
                exchange=_exchange_energy_price_data,
                passive=False,
                durable=False,
                exchange_type='fanout'
            )

            self.exchange_conveyor_pub_name = _exchange_conveyor_pub
            self.exchange_conveyor_pub = self.channel.exchange_declare(
                exchange=_exchange_conveyor_pub,
                passive=False,
                durable=False,
                exchange_type='fanout'
            )

            self.queue_order = self.channel.queue_declare(
                queue=_queue_order,
                durable=False,
                exclusive=False,
                auto_delete=True
            ).method.queue
            self.queue_image_processing = self.channel.queue_declare(
                queue=_queue_image_processing,
                durable=False,
                exclusive=False,
                auto_delete=True
            ).method.queue
            self.queue_image_processing_pub = self.channel.queue_declare(
                queue=_queue_image_processing_pub,
                durable=False,
                exclusive=False,
                auto_delete=True
            ).method.queue
            self.queue_order_processing_result_pub = self.channel.queue_declare(
                queue=_queue_order_processing_result_pub,
                durable=False,
                exclusive=False,
                auto_delete=True,
            ).method.queue

            self.queue_conveyor_data = self.channel.queue_declare(
                queue=_queue_conveyor_data,
                durable=False,
                exclusive=False,
                auto_delete=True,
            ).method.queue

            self.queue_energy_price_data = self.channel.queue_declare(
                queue=_queue_energy_price_data,
                durable=False,
                exclusive=False,
                auto_delete=True,
            ).method.queue

            self.queue_conveyor_pub = self.channel.queue_declare(
                queue=_queue_conveyor_pub,
                durable=False,
                exclusive=False,
                auto_delete=True,
            ).method.queue

            self.channel.queue_bind(exchange=_exchange_order, queue=self.queue_order, routing_key='')
            self.channel.queue_bind(exchange=_exchange_image_processing,
                                    queue=self.queue_image_processing, routing_key='')
            self.channel.queue_bind(exchange=_exchange_image_processing_pub,
                                    queue=self.queue_image_processing_pub, routing_key='')
            self.channel.queue_bind(exchange=_exchange_order_processing_result_pub,
                                    queue=self.queue_order_processing_result_pub, routing_key='')
            self.channel.queue_bind(exchange=_exchange_conveyor_data,
                                    queue=self.queue_conveyor_data, routing_key='')
            self.channel.queue_bind(exchange=_exchange_energy_price_data,
                                    queue=self.queue_energy_price_data, routing_key='')

            self.channel.queue_bind(exchange=_exchange_conveyor_pub,
                                     queue=self.queue_conveyor_pub, routing_key='')

            # bind the call back to the demonstrator FAPSDemonstratorAPI and start listening
            self.channel.basic_consume(on_message_callback=_callback_order, queue=self.queue_order, auto_ack=True)
            self.channel.basic_consume(on_message_callback=_callback_image_processing, queue=self.queue_image_processing,
                                       auto_ack=True)
            self.channel.basic_consume(on_message_callback=_callback_conveyor_data,
                                       queue=self.queue_conveyor_data,
                                       auto_ack=True)
            self.channel.basic_consume(on_message_callback=_callback_energy_price_data,
                                       queue=self.queue_energy_price_data,
                                       auto_ack=True)

            try:
                self.channel.start_consuming()
            except KeyboardInterrupt:
                self.channel.stop_consuming()
                self.connection.close()
                break
            except pika.exceptions.ConnectionClosedByBroker:
                # Uncomment this to make the example not attempt recovery
                # from server-initiated connection closure, including
                # when the node is stopped cleanly
                # except pika.exceptions.ConnectionClosedByBroker:
                #     pass
                continue
            except pika.exceptions.AMQPConnectionError:
                logger.warning("Connection was closed, retrying...")
                continue

            return self.connection, self.channel

    def start_scanning_magazin(self, order):
        if self.demonstrator_program.connect():
            self.demonstrator_program.reset()
            # Take pictures of the magazin and set the callbacks for pick_and_place
            # We have exactly 4 Magazin
            # Signal the calibration start
            for i, m in enumerate(MAGAZINS_NAMES):
                data = {
                    "time": datetime.datetime.now().timestamp(),
                    "start": True,
                    "object": m,
                    "order": order
                }
                self.channel.basic_publish(exchange=self.exchange_image_processing_pub_name,
                                      routing_key='',
                                      body=json.dumps(data))
                self.demonstrator_program.append_all_instructions(utils.take_picture_of_magazin(magazin_index=i,
                                                                                                execute=False))
                self.demonstrator_program.append_all_instructions(utils.wait(500, execute=False))

            # Prepare the callback for the marker
            self.picture_to_process.append({
                "order": order,
                "marker_count": len(MAGAZINS_NAMES)
            })

            #  Start the execution
            self.demonstrator_program.execute()
        else:
            logger.warning('Connection cannot be established to the Demonstrator')

    def search_product_and_pick_position(self, product):
        for key, val in self.image_marker_map.items():
            _ps = [s for s in val["class_name"] if s.lower() == product.lower()]
            if len(_ps) > 0:
                # get index
                index = val["class_name"].index(_ps[0])
                p_magazin = key
                p_name = val["class_name"].pop(index)
                p_class_id = val["class_ids"].pop(index)
                p_box = val["boxes"].pop(index)
                p_score = val["scores"].pop(index)
                return True, p_magazin, p_name, p_class_id, p_box, p_score

    def groundProjectPoint(self, image_point, camera_matrix, dist_coeffs, rvec, tvec, z=0.0):
        rotMat, _ = cv2.Rodrigues(rvec)
        camMat = np.asarray(camera_matrix)
        iRot = inv(rotMat)
        iCam = inv(camMat)

        uvPoint = np.ones((3, 1))

        # Image point
        uvPoint[0, 0] = image_point[0]
        uvPoint[1, 0] = image_point[1]

        tempMat = np.matmul(np.matmul(iRot, iCam), uvPoint)
        tempMat2 = np.matmul(iRot, tvec)

        s = (z + tempMat2[2, 0]) / tempMat[2, 0]
        wcPoint = np.matmul(iRot, (np.matmul(s * iCam, uvPoint) - tvec))

        # wcPoint[2] will not be exactly equal to z, but very close to it
        assert int(abs(wcPoint[2] - z) * (10 ** 8)) == 0
        wcPoint[2] = z
        return wcPoint

    def process_order_pick_and_place(self, order, image_marker_map):
        if self.demonstrator_program.connect():
            self.demonstrator_program.reset()
            pick_positions = []
            # Search for the magazin having the product to pack
            for p in order["list"]:
                try:
                    _status, p_magazin, p_name, p_class_id, p_box, p_score = self.search_product_and_pick_position(p)
                    if p_box is not None:
                        y1, x1, y2, x2 = p_box[0], p_box[1], p_box[2], p_box[3]
                        wcPoint = self.groundProjectPoint(image_point=[(x1 + x2)/2, (y1 + y2)/2],
                                                             camera_matrix=self.mtx,
                                                             dist_coeffs= self.dist,
                                                             rvec=self.transformation_matrices[p_magazin]["rvect"],
                                                             tvec=self.transformation_matrices[p_magazin]["tvec"],
                                                             z=-100.0
                                                          )
                        # pick_positions.append([wcPoint[0, 0], wcPoint[1, 0], wcPoint[2, 0]])
                        # TODO: remenber to update
                        pick_positions.append([wcPoint[0, 0], wcPoint[1, 0] + 5, wcPoint[2, 0]])
                    else:
                        logger.error("Product {} was not found".format(p))
                        print("Product {} was not found".format(p))
                        return False
                except:
                    logger.error("Product {} was not found".format(p))
                    print("Product {} was not found".format(p))
                    return False

            # Generate the program from the Pick positions
            # Add some tricks to simulate an AI Program
            _count_place = 0
            _time_to_wait = 5
            for wc in pick_positions:
                if self.current_energy_price <= 1.00:
                    self.demonstrator_program.append_all_instructions(
                        utils.set_velocity(
                            target_velocity=90,
                            execute=False
                        )
                    )
                    _time_to_wait = 5
                    self.demonstrator_program.append_all_instructions(utils.pick_and_place_object(
                        object_position=wc,
                        place_destination=PRODUCT_PLACE_POSITION_IN_BOX[self.target_position_counter])
                    )
                elif self.current_energy_price <= 2.00:
                    self.demonstrator_program.append_all_instructions(
                        utils.set_velocity(
                            target_velocity=70,
                            execute=False
                        )
                    )
                    _time_to_wait = 5
                    self.demonstrator_program.append_all_instructions(utils.pick_and_place_object(
                        object_position=wc,
                        place_destination=PRODUCT_PLACE_POSITION_IN_BOX[self.target_position_counter])
                    )
                elif self.current_energy_price <= 3.00:
                    self.demonstrator_program.append_all_instructions(
                        utils.set_velocity(
                            target_velocity=30,
                            execute=False
                        )
                    )
                    _time_to_wait = 10
                    self.demonstrator_program.append_all_instructions(utils.pick_and_place_object(
                        object_position=wc,
                        place_destination=PRODUCT_PLACE_POSITION_IN_BOX[self.target_position_counter])
                    )
                else:
                    self.demonstrator_program.append_all_instructions(
                        utils.set_velocity(
                            target_velocity=30,
                            execute=False
                        )
                    )
                    _time_to_wait = 10
                    self.demonstrator_program.append_all_instructions(utils.pick_and_place_object_only_one_axis(
                        object_position=wc,
                        place_destination=PRODUCT_PLACE_POSITION_IN_BOX[self.target_position_counter])
                    )

                self.target_position_counter = self.target_position_counter + 1
                _count_place = _count_place + 7
                if self.target_position_counter >= len(PRODUCT_PLACE_POSITION_IN_BOX):
                    self.target_position_counter = 0

            #  Start the execution
            while self.Produkt_Band2_Bereit is False:
                time.sleep(.300)

            self.demonstrator_program.execute()

            # Make the callback for the Conveyor
            threading.Timer(_count_place + _time_to_wait, self.set_conveyor_signal).start()

            return True
        else:
            logger.warning('Connection cannot be established to the Demonstrator')
            return False

    def set_conveyor_order_signal(self):
        data = {
            "START": 1,
        }
        self.channel.basic_publish(exchange=self.exchange_conveyor_pub_name,
                                   routing_key='',
                                   body=json.dumps(data))
        threading.Timer(3, self.reset_conveyor_order_signal).start()

    def reset_conveyor_order_signal(self):
        data = {
            "START": 0,
        }
        self.channel.basic_publish(exchange=self.exchange_conveyor_pub_name,
                                   routing_key='',
                                   body=json.dumps(data))

    def set_conveyor_signal(self):
        data = {
            "Linearachse_Fertig": 1,
        }
        self.channel.basic_publish(exchange=self.exchange_conveyor_pub_name,
                                   routing_key='',
                                   body=json.dumps(data))
        threading.Timer(3, self.reset_conveyor_signal).start()

    def reset_conveyor_signal(self):
        data = {
            "Linearachse_Fertig": 0,
        }
        self.channel.basic_publish(exchange=self.exchange_conveyor_pub_name,
                                   routing_key='',
                                   body=json.dumps(data))


if __name__ == '__main__':
    logger.info('Demonstrator Main Application Service using pika version: %s' % pika.__version__)
    service = Service(True)

    service.connect_and_start_listening(
        _url=DEMONSTRATOR_ENDPOINT,
        _port=5672,
        _user='esys',
        _passwd='esys',
        _exchange_order="FAPS_DEMONSTRATOR_OrderManagement_Orders",
        _queue_order="FAPS_DEMONSTRATOR_OrderManagement_Orders",
        _exchange_image_processing="FAPS_DEMONSTRATOR_ImageProcessing_ProcessingResults",
        _queue_image_processing="FAPS_DEMONSTRATOR_ImageProcessing_ProcessingResults",
        _exchange_image_processing_pub="FAPS_DEMONSTRATOR_ImageProcessing_ProcessingSignals",
        _queue_image_processing_pub="FAPS_DEMONSTRATOR_ImageProcessing_ProcessingSignals",
        _exchange_order_processing_result_pub="FAPS_DEMONSTRATOR_OrderProcessing_Results",
        _queue_order_processing_result_pub="FAPS_DEMONSTRATOR_OrderProcessing_Results",
        _exchange_conveyor_data="FAPS_DEMONSTRATOR_LiveStreamData_ConveyorData",
        _queue_conveyor_data="FAPS_DEMONSTRATOR_LiveStreamData_ConveyorData_API",
        _exchange_energy_price_data="FAPS_DEMONSTRATOR_CurrentEnergyPrice",
        _queue_energy_price_data="FAPS_DEMONSTRATOR_CurrentEnergyPrice",
        _exchange_conveyor_pub="FAPS_DEMONSTRATOR_Conveyor_DataFromCloud",
        _queue_conveyor_pub="FAPS_DEMONSTRATOR_Conveyor_DataFromCloud_API",
        _callback_order=service.incoming_order_signals_callback,
        _callback_image_processing=service.incoming_picture_marker_callback,
        _callback_conveyor_data=service.conveyor_data_callback,
        _callback_energy_price_data=service.energy_price_data_callback
    )
