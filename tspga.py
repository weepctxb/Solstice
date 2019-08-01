import numpy as np
import random
import operator
import pandas as pd
import matplotlib.pyplot as plt

import weight as wt

# https://towardsdatascience.com/evolution-of-a-salesman-a-complete-genetic-algorithm-tutorial-for-python-6fe5d2b3ca35

class Track:
    def __init__(self, id, bpm, kint, freq, slowestbpm, fastestbpm, name, key):
        self.id = id
        self.bpm = bpm
        self.kint = kint
        self.freq = freq
        self.slowestbpm = slowestbpm
        self.fastestbpm = fastestbpm
        self.name = name
        self.key = key

    def distance(self, nexttrack):
        # TODO CONVERT THIS TO DIFFERENT START AND END TRACKS
        # TODO INCREASE EMPHASIS ON INCREASING BPM
        # Combines compatibility of keys and compatibility of BPMs
        # using a Cobb-Douglas form with assigned weights
        firstbpm = self.bpm
        nextbpm = nexttrack.bpm
        firstkint = self.kint
        nextkint = nexttrack.kint
        firstfreq = self.freq
        nextfreq = nexttrack.freq
        slowestbpm = self.slowestbpm
        fastestbpm = self.fastestbpm
        bpmweight = 1. / 2.  # smaller weight, higher emphasis
        keyweight = 1. - bpmweight
        transitionscore = (wt.bpm_diff(firstbpm, nextbpm, slowestbpm, fastestbpm) ** keyweight) * \
                          (wt.key_diff(firstkint, nextkint, firstfreq, nextfreq) ** keyweight)
        return transitionscore

    def __repr__(self):
        return str(self.id) + ": " + self.name + " (" + str(self.bpm) + ", " + str(self.key) + ")" + "\n"

class Fitness:
    def __init__(self, route):
        self.route = route
        self.distance = 0.
        self.fitness = 0.0

    def routeDistance(self):
        if self.distance == 0:
            pathDistance = 0
            for i in range(0, len(self.route)):
                firsttrack = self.route[i]
                if i + 1 < len(self.route):
                    nexttrack = self.route[i + 1]
                else:
                    nexttrack = self.route[0]
                pathDistance += firsttrack.distance(nexttrack)
            self.distance = pathDistance
        return self.distance

    def routeFitness(self):
        if self.fitness == 0:
            self.fitness = 1. / self.routeDistance()
        return self.fitness

def createRoute(tracklist):
    route = random.sample(tracklist, len(tracklist))
    return route

def initialPopulation(popSize, tracklist):
    population = []

    for i in range(0, popSize):
        population.append(createRoute(tracklist))
    return population

def rankRoutes(population):
    fitnessResults = {}
    for i in range(0,len(population)):
        fitnessResults[i] = Fitness(population[i]).routeFitness()
    return sorted(fitnessResults.items(), key = operator.itemgetter(1), reverse = True)

def selection(popRanked, eliteSize):
    selectionResults = []
    df = pd.DataFrame(np.array(popRanked), columns=["Index", "Fitness"])
    df['cum_sum'] = df.Fitness.cumsum()
    df['cum_perc'] = 100 * df.cum_sum / df.Fitness.sum()

    for i in range(0, eliteSize):
        selectionResults.append(popRanked[i][0])
    for i in range(0, len(popRanked) - eliteSize):
        pick = 100 * random.random()
        for i in range(0, len(popRanked)):
            if pick <= df.iat[i, 3]:
                selectionResults.append(popRanked[i][0])
                break
    return selectionResults

def matingPool(population, selectionResults):
    matingpool = []
    for i in range(0, len(selectionResults)):
        index = selectionResults[i]
        matingpool.append(population[index])
    return matingpool


def breed(parent1, parent2):
    child = []
    childP1 = []
    childP2 = []

    geneA = int(random.random() * len(parent1))
    geneB = int(random.random() * len(parent1))

    startGene = min(geneA, geneB)
    endGene = max(geneA, geneB)

    for i in range(startGene, endGene):
        childP1.append(parent1[i])

    childP2 = [item for item in parent2 if item not in childP1]

    child = childP1 + childP2
    return child


def breedPopulation(matingpool, eliteSize):
    children = []
    length = len(matingpool) - eliteSize
    pool = random.sample(matingpool, len(matingpool))

    for i in range(0, eliteSize):
        children.append(matingpool[i])

    for i in range(0, length):
        child = breed(pool[i], pool[len(matingpool) - i - 1])
        children.append(child)
    return children


def mutate(individual, mutationRate):
    for swapped in range(len(individual)):
        if (random.random() < mutationRate):
            swapWith = int(random.random() * len(individual))

            track1 = individual[swapped]
            track2 = individual[swapWith]

            individual[swapped] = track2
            individual[swapWith] = track1
    return individual


def mutatePopulation(population, mutationRate):
    mutatedPop = []

    for ind in range(0, len(population)):
        mutatedInd = mutate(population[ind], mutationRate)
        mutatedPop.append(mutatedInd)
    return mutatedPop

def nextGeneration(currentGen, eliteSize, mutationRate):
    popRanked = rankRoutes(currentGen)
    selectionResults = selection(popRanked, eliteSize)
    matingpool = matingPool(currentGen, selectionResults)
    children = breedPopulation(matingpool, eliteSize)
    nextGeneration = mutatePopulation(children, mutationRate)
    return nextGeneration

def geneticAlgorithm(population, popSize, eliteSize, mutationRate, generations):
    pop = initialPopulation(popSize, population)
    print("Initial distance: " + str(1. / rankRoutes(pop)[0][1]))

    initRouteIndex = rankRoutes(pop)[0][0]
    initRoute = pop[initRouteIndex]
    print(initRoute)

    progress = []
    progress.append(1. / rankRoutes(pop)[0][1])

    for i in range(0, generations):
        pop = nextGeneration(pop, eliteSize, mutationRate)
        progress.append(1. / rankRoutes(pop)[0][1])

    print("Final distance: " + str(1. / rankRoutes(pop)[0][1]))
    bestRouteIndex = rankRoutes(pop)[0][0]
    bestRoute = pop[bestRouteIndex]

    print(bestRoute)

    plt.plot(progress)
    plt.ylabel('Distance')
    plt.xlabel('Generation')
    plt.show()

    return