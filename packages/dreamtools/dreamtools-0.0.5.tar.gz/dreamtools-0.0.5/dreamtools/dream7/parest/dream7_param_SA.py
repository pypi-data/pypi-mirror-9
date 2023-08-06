# -*- python -*-
#
#  This file is part of the CNO software
#
#  Copyright (c) 2011-2012 - EBI
#
#  File author(s): Thomas Cokelaer <cokelaer@ebi.ac.uk>
#
#  Distributed under the GPLv3 License.
#
##############################################################################
import os
from pylab import *





path="/home/cokelaer"
teams = ["solutions", "2pac", "biometris", "bcb",  "crux", "dreamcatcher", "forec_in_hd",
"ntu", "orangeballs", "reinhardt", "synmikro", "tbp", "thetasigmabeta"]





def get_param(data, parameter="[p5]"):
    """analyse a data file returned by copasi sensitivity task"""
    n = 25
    N = 83
    # find the p5 row index and extract the corresponding data
    indices = [data.split("\n")[i].split("\t")[0] == parameter for i in range(n,N)]
    p5 = data.split("\n")[indices.index(True)+n] # skip the first column
    p5 = p5.split("\t")[1:]
    return p5

def get_label(data):
    headers = data.split("\n")[23].split("\t")[1:]
    headers = [x.split(".")[0][7:-1] for x in headers]
    headers = [x.replace("_", "\_") for x in headers]
    return headers

def create_plot():
    for i in [3,5,8]:
        figure()
        axes([.1,.4,.8,.5])
        for team in teams:

            data = open(path + os.sep + "SA_"+team+".dat").read()

            if i==3:
                xdata = get_param(data, "[p3]")
                plot(xdata, label=r"p3\_"+team.replace("_", "\_"))
            elif i==5:
                xdata = get_param(data, "[p5]")
                plot(xdata, label=r"p5\_"+team.replace("_", "\_"))
            elif i==8:
                xdata = get_param(data, "[p8]")
                plot(xdata, label=r"p8\_"+team.replace("_", "\_"))

        labels=get_label(data)
        xticks(range(0,len(labels)), labels, rotation=90)
        legend(loc="best", prop={'size':10}, ncol=2)


        savefig("test_%s.png" % i)


create_plot()



def plot2():

    teams = sorted(d6c1.time_course_distances.keys())
    s1 = [d6c1.parameters_distances[x]['model1'] for x in teams]
    s2 = [d6c1.time_course_distances[k]['model1'] for k in teams]
    ind = argsort(s1)
    clf(); loglog([s1[i] for i in ind if "copasi" in teams[i]], [s2[i] for i in ind if "copasi" in teams[i]], 'o-', label="copasi")
    loglog([x for i,x in enumerate(s1) if i in nocopasi], [x for i,x in enumerate(s2) if i in nocopasi], 'bx', label="user data")
    clf(); loglog([s1[i] for i in ind if "copasi" in teams[i]], [s2[i] for i in ind if "copasi" in teams[i]], 'o-', label="copasi")
    loglog([x for i,x in enumerate(s1) if i in nocopasi], [x for i,x in enumerate(s2) if i in nocopasi], 'b-x', label="user data")
    clf(); loglog([s1[i] for i in ind if "copasi" in teams[i]], [s2[i] for i in ind if "copasi" in teams[i]], 'o-', label="copasi")
    clf(); loglog([s1[i] for i in ind if "copasi" in teams[i]], [s2[i] for i in ind if "copasi" in teams[i]], 'o-', label="copasi")
    loglog([x for i,x in enumerate(s1) if i in nocopasi], [x for i,x in enumerate(s2) if i in nocopasi], 'rx-', label="user data")
    clf(); loglog([s1[i] for i in ind if "copasi" in teams[i]], [s2[i] for i in ind if "copasi" in teams[i]], 'o-', label="copasi")
    loglog([x for i,x in enumerate(s1) if i in nocopasi], [x for i,x in enumerate(s2) if i in nocopasi], 'rx', label="user data", markersize=20)
    xlabel("parameter scores")
    ylabel("TC scores")
    grid()
    legend()
    title("Comparison of TC scores versus parameter scores (user data versus copasi data)")

