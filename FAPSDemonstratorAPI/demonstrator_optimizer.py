import math
import numpy as np
import random

from deap import algorithms
from deap import base
from deap import creator
from deap import tools


class DemonstratorOptimizer:

    def __init__(self):
        self.stats = None
        self.toolbox = None
        self.weigth_matrix = [2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5]
        self.hof = None
        self.pop = None
        self.stat = None
        self.IND_SIZE = 16

    def initialize(self, seed, problem_size, population_size, weight_matrix):
        random.seed(seed)
        self.IND_SIZE = 16 if problem_size is None else problem_size
        self.weigth_matrix = [2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5] \
            if weight_matrix is None else weight_matrix
        creator.create("FitnessMulti", base.Fitness, weights=(-1.0, -1.0))
        creator.create("Individual", list, typecode='i', fitness=creator.FitnessMulti)

        self.toolbox = base.Toolbox()

        # Attribute generator
        self.toolbox.register("sources", random.sample, range(self.IND_SIZE), self.IND_SIZE)
        self.toolbox.register("targets", random.sample, range(self.IND_SIZE), self.IND_SIZE)
        # Structure initializers
        self.toolbox.register("individual", tools.initCycle,
                              creator.Individual, (self.toolbox.sources, self.toolbox.targets))
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)

        self.toolbox.register("mate", tools.cxTwoPoint)
        self.toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.05)
        self.toolbox.register("select", tools.selTournament, tournsize=3)
        self.toolbox.register("evaluate", self.eval_individual)

        self.stats = tools.Statistics(lambda ind: ind.fitness.values)
        self.stats.register("avg", np.mean)
        self.stats.register("std", np.std)
        self.stats.register("min", np.min)
        self.stats.register("max", np.max)
        self.pop = self.toolbox.population(n=300 if population_size is None else population_size)
        self.hof = tools.HallOfFame(1)

    @staticmethod
    def get_dist(indv_0, indv_1):
        gen_0 = np.array(indv_0)
        x_0 = np.remainder(gen_0, 4)
        y_0 = np.floor_divide(gen_0, 4)

        gen_1 = np.array(indv_1)
        x_1 = np.remainder(gen_1, 4)
        y_1 = np.floor_divide(gen_1, 4)

        dist_vect = np.sqrt(np.power((x_1 - x_0), 2) + np.power((y_1 - y_0), 2))
        return dist_vect

    def get_position_dist(self, pos_0, pos_1):
        x_0 = pos_0 % 4
        y_0 = pos_0 / 4

        x_1 = pos_1 % 4
        y_1 = pos_1 / 4

        dist = math.sqrt((x_1 - x_0) ** 2 + (y_1 - y_0) ** 2)
        return dist

    def eval_individual(self, individual):
        dist = self.get_dist(individual[0], individual[1])
        r_individual = np.roll(np.array(individual[0]), 1)
        dist_rol = self.get_dist(r_individual, individual[1])
        weigths = np.array(self.weigth_matrix)
        total_dist = np.sum((weigths + dist) + dist_rol)
        return total_dist,

    def optimize(self, generation_count=40, crossover_rate=0.7, mutatation_reate=0.2):
        algorithms.eaSimple(self.pop, self.toolbox,
                            crossover_rate, mutatation_reate, generation_count, stats=self.stats, halloffame=self.hof)
        return self.hof, self.stats
