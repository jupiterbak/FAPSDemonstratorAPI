#!/usr/bin/env python

from __future__ import print_function

import datetime
import json
import logging
import threading

import cv2
import numpy as np
import pika
from cv2.cv2 import *
from numpy.linalg import inv

from FAPSDemonstratorAPI import Program, MAGAZINS_NAMES, utils

logging.basicConfig(format='%(asctime)-15s [%(levelname)] [%(name)-12s] %(message)s', datefmt='%d-%b-%y %H:%M:%S')
logger = logging.getLogger('FAPS Image Stiching Service')
logger.setLevel(logging.DEBUG | logging.INFO | logging.WARNING | logging.ERROR | logging.CRITICAL)

class APIService:
    """This class is the class holdinfg the set of instruction that will be executed to the demonstrator."""

    def __init__(self, publish):
        self.image_marker_map = {}
        self.robot_data = {}
        self.conveyor_data = {}
        self.current_order = {}

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

        self.exchange_robot_data = None
        self.exchange_robot_data_name = None
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

        self.queue_robot_data = None
        self.queue_conveyor_data = None
        self.queue_conveyor_pub = None

        self.queue_energy_price_data = None

        self.demonstrator_program = Program()

        # read the camera intrinsic parameters
        self.mtx = None
        self.dist = None
        self.newcameramtx = None
        self.roi = None

        self.current_energy_price = 2.0

    def incoming_picture_marker_callback(self, ch, method, properties, data):
        logger.info("Incoming picture markers")
        body = json.loads(data)
        if body["object"]:
            self.image_marker_map[body["object"]] = body

    def robot_data_callback(self, ch, method, properties, data):
        body = json.loads(data)
        _value = body['value']
        self.robot_data = _value['data']

    def conveyor_data_callback(self, ch, method, properties, data):
        body = json.loads(data)
        _value = body['value']
        self.conveyor_data = _value['DB33']

    def energy_price_data_callback(self, ch, method, properties, data):
        body = json.loads(data)
        _value = body['current_energy_price']
        self.current_energy_price = _value

    def incoming_order_signals_callback(self, ch, method, properties, data):
        logger.info("Incoming Order")
        body = json.loads(data)
        self.current_order = body

    def connect_and_start_listening(self, _url, _port, _user, _passwd,
                                    _exchange_order,
                                    _queue_order,
                                    _exchange_image_processing,
                                    _queue_image_processing, _exchange_image_processing_pub,
                                    _queue_image_processing_pub, _exchange_order_processing_result_pub,
                                    _queue_order_processing_result_pub,
                                    _exchange_robot_data,
                                    _queue_robot_data,
                                    _exchange_conveyor_data,
                                    _queue_conveyor_data,
                                    _exchange_energy_price_data,
                                    _queue_energy_price_data,
                                    _exchange_conveyor_pub,
                                    _queue_conveyor_pub,
                                    _callback_order,
                                    _callback_image_processing,
                                    _callback_robot_data,
                                    _callback_conveyor_data,
                                    _callback_energy_price_data):
        """
            Connect the FAPSDemonstratorAPI to the demonstrator.
        :return true if the connect has been established or false otherwise.
        """

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

        self.exchange_robot_data_name = _exchange_robot_data
        self.exchange_robot_data = self.channel.exchange_declare(
            exchange=_exchange_robot_data,
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

        self.queue_robot_data = self.channel.queue_declare(
            queue=_queue_robot_data,
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
        self.channel.queue_bind(exchange=_exchange_robot_data,
                                queue=self.queue_robot_data, routing_key='')
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
        self.channel.basic_consume(on_message_callback=_callback_robot_data,
                                   queue=self.queue_robot_data,
                                   auto_ack=True)
        self.channel.basic_consume(on_message_callback=_callback_energy_price_data,
                                   queue=self.queue_energy_price_data,
                                   auto_ack=True)

        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.channel.stop_consuming()
            self.connection.close()
        except pika.connection.exceptions.ConnectionClosedByBroker:
            # Uncomment this to make the example not attempt recovery
            # from server-initiated connection closure, including
            # when the node is stopped cleanly
            # except pika.exceptions.ConnectionClosedByBroker:
            pass
        except pika.connection.exceptions.AMQPConnectionError:
            logger.warning("Connection was closed, retrying...")

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

    def ground_project_point(self, image_point, camera_matrix, dist_coeffs, rvec, tvec, z=0.0):
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

    def set_conveyor_signal_achse_fertig(self):
        data = {
            "Linearachse_Fertig": 1,
        }
        self.channel.basic_publish(exchange=self.exchange_conveyor_pub_name,
                                   routing_key='',
                                   body=json.dumps(data))
        threading.Timer(3, self.reset_conveyor_signal_achse_fertig).start()

    def reset_conveyor_signal_achse_fertig(self):
        data = {
            "Linearachse_Fertig": 0,
        }
        self.channel.basic_publish(exchange=self.exchange_conveyor_pub_name,
                                   routing_key='',
                                   body=json.dumps(data))
