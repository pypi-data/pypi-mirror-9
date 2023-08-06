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
"""This module contains the credits data related to DREAM7 
parameter estimation and topology network challenge

"""
import re

# All data below were transcripted from the DREAM user credit log
# !!!!!!!!!!!!!!!!!!!!!!! order is ANTI chronological 
# credits['team1'][0] contains the credits of team1
# credits['team1'][1] contains the sub challenge type (model 1 or 2 mixed )
# credits['team1'][2] contains the name of the file downloaded
# To make it clear credits[team][0][0] was bought after credits[team][0][1]
credits1 = {
    'team1':[
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


    "team2": [
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

    "team3": [
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


    'team4':[
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

    'team5':[
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
        
    'team6':[
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

    'team7':[
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

    'team8':[
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

    'team9':[
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

    'team10':[
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

    'team11':[
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


    'team12':[
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

# Correspondence between filenames and human readable names

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



teams = ['team'+str(i ) for i in range(1,13)]
names = ['thetasigmabeta', 'synmikro','biometris','tbp', 'crux', 'orangeballs',
'2apc', 'bcb', 'dreamcatcher', 'reinhardt', 'ntu', 'forec_in_hd']

team_mapping = dict( [(k,v) for k,v in zip(names,teams)])



def get_data_challenge1(team):
    """Returns tuple with the credits and corresponding filenames for challenge 1 for a given team"""
    filenames = [x.strip() for x in credits1[team][2].split("\n")]
    models = credits1[team][1]
    credits = credits1[team][0]

    d1 = [x for x,y,z in zip(credits, models, filenames) if y==1]
    d2 = [z for x,y,z in zip(credits, models, filenames) if y==1]
    return(d1[::-1],d2[::-1])
