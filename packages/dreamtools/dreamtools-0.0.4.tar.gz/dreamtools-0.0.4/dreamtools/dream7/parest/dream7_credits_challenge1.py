# -*- python -*-
#
#  Copyright (c) 2011-2012 - EBI-EMBL
#
#  File author(s): Thomas Cokelaer <cokelaer@ebi.ac.uk>
#
#  Distributed under the GPLv3 License.
#  See accompanying file LICENSE.txt or copy at
#      http://www.gnu.org/licenses/gpl-3.0.html
#
##############################################################################
"""This module creates figures related to parameter challenge paper

Just run the script and it should generates a few figures.

"""
import re

#All data below were transcripted from the DREAM user credit log by hand...
credits = {
    'thetasigmabeta':[
        [850, 850, 1350, 1350, 400, 1600, 1600, 400,400, 400, 400,
        1200, 400, 400, 1450, 850, 1800, 1350, 1300, 400, 400, 400, 400],
        [2,2,2,2,1,1,1,2,2,2, 2,1,2,2,1,1,2,2,1, 1,1,1,1],
        """p5_p7_mod_2_dwn_p2.tab
        array_mod_2_over_p3_low.tab
        array_mod_2_over_p6_high.tab
        array_mod_2_over_p7_high.tab
        p1_p3_mod_1_wildtype.tab
        model_1_rs1a.tab
        model_1_as1.tab
        p10_p11_mod_2_wildtype.tab
        p8_p9_mod_2_wildtype.tab
        p6_p7_mod_2_wildtype.tab
        p4_p5_mod_2_wildtype.tab
        p1_p3_mod_1_del_pro5.tab
        p10_p3_mod_2_wildtype.tab
        p1_p2_mod_2_wildtype.tab
        array_mod_1_dwn_rbs3_high.tab
        p2_p3_mod_1_dwn_rbs3.tab
        array_mod_2_del_p8_high.tab
        array_mod_2_over_p9_high.tab
        array_mod_1_del_pro6_low.tab
        p1_p2_mod_1_wildtype.tab
        p8_p9_mod_1_wildtype.tab
        p4_p5_mod_1_wildtype.tab
        p6_p7_mod_1_wildtype.tab"""],


    "synmikro": [
        [750, 750, 400, 850, 850, 850,750, 1300, 850, 850, 1300,
        850, 1600, 1200, 1200, 1300, 950, 1800, 400, 400, 400, 400],
        [1,1,2,1,2,2,1,2,2,2, 2,2,1,1,1,1,2,2,1,1,1,1],
        """p7_p8_mod_1_dwn_v7_mrna.tab
        p3_p5_mod_1_dwn_v7_mrna.tab
        p5_p7_mod_2_wildtype.tab
        array_mod_1_dwn_v9_mrna_low.tab
        array_mod_2_over_p3_low.tab
        array_mod_2_over_p10_low.tab
        p8_p9_mod_1_dwn_v9_mrna.tab
        array_mod_2_del_p1_low.tab
        array_mod_2_over_p7_low.tab
        array_mod_2_over_p11_low.tab
        array_mod_2_del_p11_low.tab
        array_mod_2_over_p9_low.tab
        model_1_as1.tab
        p1_p2_mod_1_del_pro3.tab
        p1_p2_mod_1_del_pro6.tab
        array_mod_1_del_pro6_low.tab
        array_mod_2_dwn_p8_low.tab
        array_mod_2_del_p7_high.tab
        p4_p5_mod_1_wildtype.tab
        p2_p3_mod_1_wildtype.tab
        p6_p7_mod_1_wildtype.tab
        p1_p9_mod_1_wildtype.tab"""],

    "biometris": [
        [1350,850,850,1600,850,1800,850,850,1600,850,750,1350, 1000, 1800, 400, 950, 400, 400, 850, 400],
        [2,2,2,1,2,2,1,2,1,2, 1,2,2,1,1,1,1,1,1,1],
        """array_mod_2_over_p4_1_high.tab
        array_mod_2_over_p6_low.tab
        array_mod_2_over_p7_low.tab
        model_1_rs1b.tab
        array_mod_2_over_p8_low.tab
        array_mod_2_del_p7_high.tab
        p2_p3_mod_1_dwn_rbs3.tab
        array_mod_2_over_p3_low.tab
        model_1_rs1a.tab
        array_mod_2_over_p5_2_low.tab
        p1_p2_mod_1_dwn_v3_mrna.tab
        array_mod_2_over_p1_high.tab
        array_mod_2_wildtype_high.tab
        array_mod_1_del_pro6_high.tab
        p1_p7_mod_1_wildtype.tab
        array_mod_1_dwn_rbs9_low.tab
        p4_p9_mod_1_wildtype.tab
        p3_p8_mod_1_wildtype.tab
        array_mod_1_dwn_v7_mrna_low.tab
        p5_p6_mod_1_wildtype.tab"""],


    'tbp':[
        [1350, 1450, 1350, 1350, 750, 750, 1200, 1800, 750, 750,
        400, 1450, 1000, 400, 1200, 400, 400, 1200, 1300, 500],
        [2,2,2,2,1,1,1,2,1,1, 1,2,2,1,1,1,1,1,1,1],
        """array_mod_2_over_p7_high.tab
        array_mod_2_dwn_p11_high.tab
        array_mod_2_over_p11_high.tab
        array_mod_2_over_p3_high.tab
        p1_p2_mod_1_dwn_v2_mrna.tab
        p4_p9_mod_1_dwn_v9_mrna.tab
        p1_p2_mod_1_del_pro6.tab
        array_mod_2_del_p7_high.tab
        p3_p4_mod_1_dwn_v4_mrna.tab
        p8_p9_mod_1_dwn_v8_mrna.tab
        p1_p7_mod_1_wildtype.tab
        array_mod_2_dwn_p6_high.tab
        array_mod_2_wildtype_high.tab
        p6_p9_mod_1_wildtype.tab
        p1_p2_mod_1_del_pro3.tab
        p2_p4_mod_1_wildtype.tab
        p3_p5_mod_1_wildtype.tab
        p6_p8_mod_1_del_pro6.tab
        array_mod_1_del_pro6_low.tab
        array_mod_1_wildtype_low.tab"""],

    'crux':[
        [950, 1350, 1350, 1350, 1800, 400, 400, 400, 400, 400,
        1000,400,1200,1600,750,1600,1600,400,1600,400,400],
        [2,2,2,2,2,2,2,2,2,2, 2,1,1,1,1,1,1,1,1,1,1],
        """array_mod_2_dwn_p7_low.tab
        array_mod_2_over_p11_high.tab
        array_mod_2_over_p8_high.tab
        array_mod_2_over_p4_1_high.tab
        array_mod_2_del_p7_high.tab
        p10_p11_mod_2_wildtype.tab
        p8_p9_mod_2_wildtype.tab
        p5_p7_mod_2_wildtype.tab
        p3_p4_mod_2_wildtype.tab
        p1_p2_mod_2_wildtype.tab
        array_mod_2_wildtype_high.tab
        p8_p9_mod_1_wildtype.tab
        p1_p8_mod_1_del_pro6.tab
        model_1_as1.tab
        p2_p9_mod_1_dwn_v3_mrna.tab
        model_1_rs7.tab
        model_1_as7.tab
        p1_p3_mod_1_wildtype.tab
        model_1_as4.tab
        p4_p5_mod_1_wildtype.tab
        p6_p7_mod_1_wildtype.tab"""],
        
    'orangeballs':[
        [850, 850, 850, 1800, 400, 850, 850, 400, 400, 400, 400,
        950, 850, 1600, 1600, 850, 750, 850, 750, 750, 1200, 400, 400,
        400, 400],
        [2,2,2,2,2,2,2,2,2,2, 2, 2, 2,1,1,1,1,1,1,1,1,1,1,1,1],
        """array_mod_2_over_p11_low.tab
        array_mod_2_over_p9_low.tab
        array_mod_2_over_p5_2_low.tab
        array_mod_2_del_p7_high.tab
        p1_p11_mod_2_wildtype.tab
        array_mod_2_over_p7_low.tab
        array_mod_2_over_p6_low.tab
        p6_p7_mod_2_wildtype.tab
        p8_p9_mod_2_wildtype.tab
        p4_p5_mod_2_wildtype.tab
        p2_p3_mod_2_wildtype.tab
        array_mod_2_dwn_p7_low.tab
        array_mod_2_over_p10_low.tab
        model_1_rs1b.tab
        model_1_rs1a.tab
        p3_p5_mod_1_dwn_rbs8.tab
        p3_p6_mod_1_dwn_v4_mrna.tab
        array_mod_1_dwn_v6_mrna_low.tab
        p2_p3_mod_1_dwn_v3_mrna.tab
        p4_p9_mod_1_dwn_v9_mrna.tab
        p1_p2_mod_1_del_pro6.tab
        p1_p2_mod_1_wildtype.tab
        p8_p9_mod_1_wildtype.tab
        p5_p7_mod_1_wildtype.tab
        p3_p4_mod_1_wildtype.tab"""],

    '2apc':[
        [400, 400, 850, 850, 1300, 850, 1300, 850, 850, 850, 1300,
        750, 1600, 1200, 750, 400, 750, 1300, 1200, 750, 1200],
        [2,2,2,2,2,2,2,2,2,2,2,1,1,1,1,1,1,1,1,1,1],
        """p11_p9_mod_2_wildtype.tab
        p4_p5_mod_2_wildtype.tab
        array_mod_2_over_p9_low.tab
        array_mod_2_over_p1_low.tab
        array_mod_2_del_p7_low.tab
        array_mod_2_over_p5_2_low.tab
        array_mod_2_del_p3_low.tab
        array_mod_2_over_p7_low.tab
        array_mod_2_over_p11_low.tab
        array_mod_2_over_p8_low.tab
        array_mod_2_del_p11_low.tab
        p2_p7_mod_1_dwn_v3_mrna.tab
        model_1_rs1b.tab
        p1_p3_mod_1_del_pro6.tab
        p3_p9_mod_1_dwn_v4_mrna.tab
        p3_p5_mod_1_wildtype.tab
        p3_p8_mod_1_dwn_v7_mrna.tab
        array_mod_1_del_pro7_low.tab
        p3_p4_mod_1_del_pro8.tab
        p3_p8_mod_1_dwn_v6_mrna.tab
        p2_p8_mod_1_del_pro6.tab"""],

    'bcb':[
        [1300, 850, 850, 850, 1300, 1300, 1300, 1600, 1300, 1300,
        1600, 1200, 1600, 1300],
        [2,2,2,2,2,2,2,1,1,1,1,1,1,1],
        """array_mod_2_del_p3_low.tab
        array_mod_2_over_p8_low.tab
        array_mod_2_over_p3_low.tab
        array_mod_2_over_p11_low.tab
        array_mod_2_del_p8_low.tab
        array_mod_2_del_p7_low.tab
        array_mod_2_del_p11_low.tab
        model_1_rs7.tab
        array_mod_1_del_pro5_low.tab
        array_mod_1_del_pro7_low.tab
        model_1_as9.tab
        p6_p7_mod_1_del_pro6.tab
        model_1_as1.tab
        array_mod_1_del_pro6_low.tab"""
        ],

    'dreamcatcher':[
        [1350, 1800, 1800, 1350, 850, 750, 1800, 1300, 1600, 1000,
        750, 400, 1200, 400, 1350, 1350, 400, 400],
        [2,2,1,2,1,1,2,2,1,2,1,1,1,1,1,2,1,1],
        """array_mod_2_over_p10_high.tab
        array_mod_2_del_p4_1_high.tab
        array_mod_1_del_pro6_high.tab
        array_mod_2_over_p7_high.tab
        p2_p3_mod_1_dwn_rbs3.tab
        p3_p8_mod_1_dwn_v7_mrna.tab
        array_mod_2_del_p9_high.tab
        array_mod_2_del_p7_low.tab
        model_1_rs1a.tab
        array_mod_2_wildtype_high.tab
        p4_p9_mod_1_dwn_v9_mrna.tab
        p5_p8_mod_1_wildtype.tab
        p1_p2_mod_1_del_pro6.tab
        p3_p6_mod_1_wildtype.tab
        array_mod_1_dwn_v6_mrna_high.tab
        array_mod_2_over_p8_high.tab
        p4_p7_mod_1_wildtype.tab
        p2_p9_mod_1_wildtype.tab"""],

    'reinhardt':[
        [1450, 1200, 750, 750, 750, 1450, 1200, 400, 400, 400, 400, 750],
        [1,1,1,1,1,1,1,1,1,1,1,1],
        """array_mod_1_dwn_rbs6_high.tab
        p2_p3_mod_1_del_pro9.tab
        p3_p7_mod_1_dwn_v4_mrna.tab
        p3_p8_mod_1_dwn_v6_mrna.tab
        p8_p9_mod_1_dwn_v7_mrna.tab
        array_mod_1_dwn_rbs9_high.tab
        p3_p8_mod_1_del_pro7.tab
        p2_p5_mod_1_wildtype.tab
        p1_p8_mod_1_wildtype.tab
        p6_p9_mod_1_wildtype.tab
        p3_p4_mod_1_wildtype.tab
        p5_p7_mod_1_dwn_v6_mrna.tab"""
    ],

    'ntu':[
        [1600, 1600, 1600, 850, 850, 1300, 1300, 1300, 1800, 400,
        850, 400, 400, 400, 400, 400, 400, 1000, 400, 400, 400, 400, 400,
        1000],
        [1,1,1,1,2,2,2,2,2,1,1,2,2,2,2,2,2,2,1,1,1,1,1,1],
        """model_1_rs7.tab
        model_1_as7.tab
        model_1_as4.tab
        p2_p3_mod_1_dwn_rbs3.tab
        array_mod_2_over_p8_low.tab
        array_mod_2_del_p9_low.tab
        array_mod_2_del_p6_low.tab
        array_mod_2_del_p7_low.tab
        array_mod_2_del_p2_high.tab
        p5_p8_mod_1_wildtype.tab
        p3_p5_mod_1_dwn_rbs5.tab
        p11_p6_mod_2_wildtype.tab
        p10_p9_mod_2_wildtype.tab
        p7_p8_mod_2_wildtype.tab
        p4_p5_mod_2_wildtype.tab
        p3_p4_mod_2_wildtype.tab
        p1_p2_mod_2_wildtype.tab
        array_mod_2_wildtype_high.tab
        p4_p9_mod_1_wildtype.tab
        p1_p2_mod_1_wildtype.tab
        p3_p5_mod_1_wildtype.tab
        p7_p8_mod_1_wildtype.tab
        p6_p7_mod_1_wildtype.tab
        array_mod_1_wildtype_high.tab"""
     ],


    'forec_in_hd':[
        [400,400,1800,1350,850,1600,1800,400,1200,400,1800,1450,400,400,1800,1800,1000,1000],
        [2,2,2,2,1,1,2,1,1,1,1,2,1,1,1,2,1,2],
        """p11_p7_mod_2_wildtype.tab
        p1_p10_mod_2_wildtype.tab
        array_mod_2_del_p5_2_high.tab
        array_mod_2_over_p1_high.tab
        p3_p7_mod_1_dwn_rbs4.tab
        model_1_as4.tab
        array_mod_2_del_p4_1_high.tab
        p1_p4_mod_1_wildtype.tab
        p1_p2_mod_1_del_pro3.tab
        p2_p6_mod_1_wildtype.tab
        array_mod_1_del_pro5_high.tab
        array_mod_2_dwn_p8_high.tab
        p5_p8_mod_1_wildtype.tab
        p3_p9_mod_1_wildtype.tab
        array_mod_1_del_pro6_high.tab
        array_mod_2_del_p7_high.tab
        array_mod_1_wildtype_high.tab
        array_mod_2_wildtype_high.tab"""
    ]
}


def check(verbose=False):
    """This function performs some sanity checks on the input data 

    We must have 3 columns of same length containing

        * credit spent
        * the corresponding sub challenge (1 or 2)
        * name of the file bought


    """
    # sanity check
    for k,v in credits.iteritems():
        d1 = v[0]
        d2 = v[1]
        d3 = v[2].split()
    
        if verbose:print "-----------------", k, sum(d1)
        assert sorted(list(set(d2))) in [ [1,2] , [1], [2]]
        if verbose:print len(d1), len(d2), len(d3)
        assert len(d3) == len(d1) == len(d2)

# calling the sanity check 
check()


# -----------------------------------------------------------------------------
# FIGURE 1 : create histogram of all credits values  therefore mixing
# challenges, expereiments over all teams.
# p[ut all credit expenses in one list
print "creating dream7_challenge1_credit1 figure 1"
all_values = []
for team, v in credits.iteritems():
    all_values.extend(v[0])
#print sorted(set(all_values))

# figure showing the type of credits spent over all teams
print "creating dream7_challenge1_credit1 figure"
from pylab import *
clf(); 
hist([x for x in all_values], 50); 
grid(); 
ylabel("\#", fontsize=16);
xlabel("Credit type", fontsize=16);
savefig("dream7_challenge1_credit1.png")



# -----------------------------------------------------------------------------
# Figure 2. The same but we average over teams to get errors
print "creating dream7_challenge1_credit1 figure 2"
amount_spent = [sum(d[0]) for d in credits.values()]
print "amount spent per team", amount_spent
categories = sorted(list(set(all_values)))

#For model1, all teams spent their credits
import numpy
teams = credits.keys()
res = numpy.zeros((len(teams), len(categories)))
for i,team in enumerate(teams):
    values = credits[team][0]
    S = sum(values)
    fracs = []
    for j, c in enumerate(categories):
        frac = (values.count(c) * c)/float(S) * 100 # fraction of this category compared to total amount spent
        res[i,j] = frac

# compute mean and std
M = numpy.mean(res, axis=0)
v = numpy.std(res, axis=0)
clf(); 
errorbar(categories, M, yerr=v, fmt='o'); axis([350,1850,0,30]);
grid(); 
xlabel("Credit category (per value)", fontsize=16); 
ylabel("Fraction of credit spent in each category", fontsize=16)
savefig("dream7_challenge1_credit2.png")




# -----------------------------------------------------------------------------
#Figure 3 ow we want to be more precise because there are 2 categories or credit
# that have the same value: microarray+downregulation+loweres ==
# fluorescence+downregulation == 850
# Moreover, we want to look at the sub challenge individually.


data1_credits = []
data1_names = []
data2_credits = []
data2_names = []
for i in range(0, len(teams)):
    for x,y,z in zip(credits[teams[i]][0], credits[teams[i]][1], credits[teams[i]][2].split()):

        if y == 1: #sub challenge 1
            data1_credits.append(x)
            data1_names.append(z)
        elif y == 2: #sub challenge 1
            data2_credits.append(x)
            data2_names.append(z)


labels1 = [
    r"$\mu$ array del(L)",
    r"$\mu$ array siRNA(L)",
    r"$\mu$ array rbs(L)",
    r"$\mu$ array wildtype(L)",
    r"$\mu$ array del(H)",
    r"$\mu$ array siRNA(H)",
    r"$\mu$ array rbs(H)",
    r"$\mu$ array wildtype(H)",
    "Fluorescence del",
    "Fluorescence siRNA",
    "Fluorescence rbs",
    "Fluorescence wildtype",
    "Gel-shift wildtype"
]

types_experiments1 = [
    r"array_mod_1_del_pro\d{1,2}_low",
    r"array_mod_1_dwn_v\d{1,2}_mrna_low",
    r"array_mod_1_dwn_rbs\d{1,2}_low",
    r"array_mod_1_wildtype_low",
    r"array_mod_1_del_pro\d{1,2}_high",
    r"array_mod_1_dwn_v\d{1,2}_mrna_high",
    r"array_mod_1_dwn_rbs\d{1,2}_high",
    r"array_mod_1_wildtype_high",
    r"p\d{1,2}_p\d{1,2}_mod_1_del_pro",
    r"p\d{1,2}_p\d{1,2}_mod_1_dwn_v\d{1,2}_mrna",
    r"p\d{1,2}_p\d{1,2}_mod_1_dwn_rbs\d{1,2}",
    r"p\d{1,2}_p\d{1,2}_mod_1_wildtype",
    r"model_1_as\d{1,2}",
    r"model_1_rs\d{1,2}"]

count = [0] * len(types_experiments1)
# loop over all experiment to check what is the type of the credit (data1_names)
# bought by the participants and fill a counter.
for i, exp in enumerate(types_experiments1):
    for d in data1_names:
        # each type of experiments is a regular expression to look for
        if re.search(exp, d):
            count[i]+=1

assert sum(count) == len(data1_names)


print "creating dream7_challenge1_credit1 figure 3"
# !!! model_1_as and model_1_rs are both in the Getshift wildtype. So, we add
# them both 
count[12] += count[13]

temp = numpy.array(count[0:13])/float(sum(count[0:13]))
print temp
print (sum(temp))

clf(); 
axes([0.15,0.26,0.8,0.7])
bar(range(0, 4), count[0:4], color="#99ccff")
bar(range(4, 8), count[4:8], color="#3366ff")
bar(range(8, 12), count[8:12], color="#ccffcc")
bar(range(12, 13), count[12], color="#ffcc99")
grid(); 
ylabel("\#", fontsize=16);
xlabel("Type of credit", fontsize=11);
xticks([x+.5 for x in range(0,len(labels1))], labels1, rotation=45, ha='right')
xlim(0,len(count)-1)
savefig("dream7_challenge1_credit3_sub1.png")


count1 = count[:]



# -----------------------------------------------------------------------------

labels2 = [
    r"Mspec del(L)     ",
    r"Mspec over(L)    ",
    r"Mspec down(L)    ",
    r"Mspec wildtype(L)",
    r"Mspec del(H)     ",
    r"Mspec over(H)    ",
    r"Mspec down(H)    ",
    r"Mspec wildtype(H)",
    "Fluorescence-del",
    "Fluorescence-over",
    "Fluorescence-down",
    "Fluorescence-wildtype",
    "Gel-shift-wildtype"
]
# ?\d?_ is used because prot 4 and 5 may be written p4_1 or p4_2
types_experiments2 = [
    r"array_mod_2_del_p\d{1,2}_?\d?_low",
    r"array_mod_2_over_p\d{1,2}_?\d?_low",
    r"array_mod_2_dwn_p\d{1,2}_?\d?_low",
    r"array_mod_2_wildtype_low",
    r"array_mod_2_del_p\d{1,2}_?\d?_high",
    r"array_mod_2_over_p\d{1,2}_?\d?_high",
    r"array_mod_2_dwn_p\d{1,2}_?\d?_high",
    r"array_mod_2_wildtype_high",
    r"p\d{1,2}_p\d{1,2}_mod_2_del_pro",
    r"p\d{1,2}_p\d{1,2}_mod_2_over_pro\d{1,2}_mrna",
    r"p\d{1,2}_p\d{1,2}_mod_2_dwn_p\d{1,2}",
    r"p\d{1,2}_p\d{1,2}_mod_2_wildtype",
    r"model_2_as\d{1,2}",
    r"model_2_rs\d{1,2}"]


founds = [0] * len(data2_names)
for i,x in enumerate(data2_names):
    found = False
    for pat in types_experiments2:
        if re.search(pat,x) != None:
            found = True
            break
        found
    if found: founds[i] = True
    if found == False: pass



count = [0] * len(types_experiments2)
# loop over all experiment to check what is the type of the credit (data1_names)
# bought by the participants and fill a counter.
for i, exp in enumerate(types_experiments2):
    for d in data2_names:
        # exah type of experiments is a regular expression to look for
        if re.search(exp, d):
            count[i]+=1

assert sum(count) == len(data2_names)

temp = numpy.array(count[0:13])/float(sum(count[0:13]))
print temp
print (sum(temp))



count2 = count[:]

print "creating dream7_challenge1_credit1 figure 4"
from pylab import *

clf(); 
axes([0.15,0.26,0.8,0.7])
bar(range(0, len(count)), count)

bar(range(0, 4), count[0:4], color="#99ccff")
bar(range(4, 8), count[4:8], color="#3366ff")
bar(range(8, 12), count[8:12], color="#ccffcc")
bar(range(12, 13), count[12], color="#ffcc99")


grid(); 
ylabel("\#", fontsize=16);
xlabel("Type of credit", fontsize=11);
shift = 0.5
xticks([x+shift for x in range(0,len(labels2))], labels2, rotation=45,ha="right")
xlim(0,len(count)-1) # gelshift is duplicated in the search, not the labels.
savefig("dream7_challenge1_credit3_sub2.png")



# ----------------------------------------------------------------------------
# sequence of bought credit per team and sub challenge
sequences1 = {}
sequences2 = {}
# loop over all experiment to check what is the type of the credit (data1_names)
# bought by the participants and fill a counter.
for team in teams:
    sequences1[team] = []
    sequences2[team] = []
    data1_names2 = []
    data2_names2 = []
    #first get the credit type per sub challenge
    for x,y,z in zip(credits[team][0], credits[team][1], credits[team][2].split()):
        if y ==1: data1_names2.append(z)
        if y ==2: data2_names2.append(z)

    # identify the order according to type_experiment1
    for x in data1_names2:
        for i, exp in enumerate(types_experiments1):
            if re.search(exp, x):
                sequences1[team].append(i)
                break
    for x in data2_names2:
        for i, exp in enumerate(types_experiments2):
            if re.search(exp, x):
                sequences2[team].append(i)
                break



# some graph theory
try:
    import networkx as nx
except:
    exit()


def get_edges(sequences):
    edges = []
    for team in sequences.keys():
        s1 = sequences[team][0:-1]
        s2 = sequences[team][1:]
        for x,y in zip(s1,s2):
            if y==13:
                y=12
            if x==13:
                x=12
            edges.append((x+1,y+1))
    return edges

edges = get_edges(sequences1)
sedges = set(edges)



# playing with networkx (not # successful....)----------------------------------------
g = nx.DiGraph()
for x in sedges: 
    count = edges.count(x)
    #print count
    g.add_edge(x[0], x[1], weight=count)



clf(); 
nx.draw(g, 
    pos={
        1:(0,300), 2:(100,300), 3:(200,300), 4:(300,300), 
        5:(0, 200), 6:(100,200), 7:(200,200), 8:(300,200), 
        9:(0,100), 10:(100,100), 11:(200,100), 12:(300,100), 
        13:(300,0)},

    node_size = [x*160 for x in nx.degree(g).values()],
    node_color = ['yellow' for x in nx.degree(g).values()],
    edge_color = 'red',
    edge_width = 4
    )


def get_graph_team(team):
    edges = []
    for s1, s2 in zip(sequences1[team][0:-1], sequences1[team][1:]):
        if s1==13: s1=12
        if s2==13: s2=12
        edges.append((s1+1, s2+1))

    g = nx.MultiGraph()
    for x in edges:
        g.add_edge(x[0], x[1])
    return g

clf()



# bar(nx.degree(g).keys(), nx.degree(g).values())

# playing with igraph ----------------------------------------
import igraph

def get_graph(edges):

    sedges = set(edges)
    # igraph uses IDs from 0 to N-1 but edges are not using indices here. there go
    # from 1 to 13. So, we must trick igraph by using 14 vertices (0 and then 1 to
    # 13) qnd remove the zero afterwards that is not used in the sedges anyway.
    g = igraph.Graph(n=14, edges=list(sedges), directed=True)
    g.delete_vertices(0) # remove the first 

    # now, the vertices are IDs from 0 to 12. That the way igraph wroks. So, we now
    # need to givev names to the vertices:
    g.vs['name'] = [str(x) for x in range(1,14)]
    g.vs['label'] = g.vs['name'] # labels are used in the plot function

    degree = g.degree()

    # size 
    g.vs['size'] = [log2(5+x)*10 for x in degree]
    g.vs['label_dist'] = [0] * 13
    # then we need a layout:


    #color_dict = {"m": "blue", "f": "pink"}
    #plot(g, layout = layout, vertex_color = [color_dict[gender] for gender in g.vs["gender"]])

    traversed_edges = []
    for i,x in enumerate(sedges):
        count = edges.count(x)
        traversed_edges.append(count)
    g.es['width'] = traversed_edges
    return g

l = igraph.Layout([(0,0), (100,0), (200,0), (300,0), (0,100), (100,100), (200,100), (300,100), (0,200), (100,200), (200, 200), (300, 200), (300, 300)])
edges = get_edges(sequences1)
g1 = get_graph(edges)
igraph.plot(g1, "dream7_challenge1_credit_graph1.png", layout=l, margin=60)
#igraph.write_graph_gml(g1, "test.gml")
g1.write_graphml("test1.graphml")
g1.write_gml("test1.gml")

edges = get_edges(sequences2)
g2 = get_graph(edges)
igraph.plot(g2, "dream7_challenge1_credit_graph2.png", layout=l, margin=60)
g2.write_graphml("test2.graphml")
g2.write_gml("test2.gml")


"""get the edges width:
since yEd has only 7 type of width, we need to nor;qlise qnd ;ultiply by 7:

gml_data =  [(x.source, x.target, x['width'], ceil(x['width']/22.*7)) for x in list(data.g1.es)]
 
"""

# print edge information in gml format
def printgml():

    M1 = max([x['width'] for x in list(g1.es)])
    gml_edge_data1 =  [(x.source, x.target, x['width'], ceil(log2(.1+x['width'])/log2(.1+M1)*7.)) for x in list(g1.es)]
    for edge in gml_edge_data1:
        print("""edge
         [
             source  %s
             target  %s
             graphics
             [
                 width %s
                 fill    "#FF6600"
                 targetArrow "standard"
             ]
             LabelGraphics
             [
                 text    "%s"
                 fontSize    12
                 fontName    "Dialog"
                 model   "six_pos"
                 position    "tail"
             ]
         ]""" % (edge[0], edge[1], edge[3], edge[2]))

    M2 = max([x['width'] for x in list(g2.es)])
    gml_edge_data2 =  [(x.source, x.target, x['width'], ceil(log2(.1+x['width'])/log2(.1+M2)*7.)) for x in list(g2.es)]
    for edge in gml_edge_data2:
        print("""edge
         [
             source  %s
             target  %s
             graphics
             [
                 width %s
                 fill    "#FF6600"
                 targetArrow "standard"
             ]
             LabelGraphics
             [
                 text    "%s"
                 fontSize    12
                 fontName    "Dialog"
                 model   "six_pos"
                 position    "tail"
             ]
         ]""" % (edge[0], edge[1], edge[3], edge[2]))

