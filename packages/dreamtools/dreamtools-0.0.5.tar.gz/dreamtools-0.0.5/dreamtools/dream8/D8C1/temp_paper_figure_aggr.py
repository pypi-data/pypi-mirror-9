from dreamtools.dream8.D8C1 import aggregation
from pylab import *
import numpy as np
import pickle


a = aggregation.SC1A_aggregation()
b = aggregation.SC1B_aggregation()
a.remove_correlated_submissions()
b.remove_correlated_submissions()


def create_sc1a():
    a.plot_aggr_best_score()
    title("")
    ylabel('mean AUROC')
    legend(['Individual teams', 'Aggregate submission network, using top N teams'], loc='lower left')
    savefig("sc1a_aggregation_best.png")
    savefig("sc1a_aggregation_best.eps")
    savefig("sc1a_aggregation_best.pdf")
    savefig("sc1a_aggregation_best.svg")


def create_sc1a_random():
    # SC1A random requires lots of computation time, so we use the cluster and get
    # bunch of data in random_temp/*pkl
    data = []
    for i in range(0,102):  # some files are missing (2)
        try:
            res = pickle.load(open("random_temp/aggr_%s.pkl" % (i+1), "r"))
            data.append(res['aggregation_all'][0])
        except:
            print('skipped')

    a.results = np.array(data)
    a._plot_aggr_random(range(0,66), 66)
    title("")
    ylabel('mean AUROC')
    legend(['Individual teams', 'Aggregate submission network, formed \nusing N randomly selected teams'], loc='lower left')
    savefig("sc1a_aggregation_rand.png")
    savefig("sc1a_aggregation_rand.eps")
    savefig("sc1a_aggregation_rand.pdf")
    savefig("sc1a_aggregation_rand.svg")

def create_sc1b():
    ## SC1B 
    b.plot_aggr_best_score()
    ylabel("AUROC")
    title("")
    legend(['Individual teams', 'Aggregate submission network, using top N teams'], 
            loc='lower left')
    savefig("sc1b_aggregation_best.png")
    savefig("sc1b_aggregation_best.eps")
    savefig("sc1b_aggregation_best.pdf")
    savefig("sc1b_aggregation_best.svg")

def create_sc1b_rand(N=100):
    b.remove_correlated_submissions()
    b.plot_aggr_random(N, 58)
    ylabel("AUROC")
    title("")
    legend(['Individual teams', 'Aggregate submission network, using N randomly selected teams'], 
            loc='lower left')
    savefig("sc1b_aggregation_rand.png")
    savefig("sc1b_aggregation_rand.eps")
    savefig("sc1b_aggregation_rand.pdf")
    savefig("sc1b_aggregation_rand.svg")

def run():
    #create_sc1a()
    #create_sc1a_random()
    create_sc1b()
    create_sc1b_rand()


#run()


