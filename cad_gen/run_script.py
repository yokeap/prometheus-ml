import numpy as np
from .vessel_class import Vessel
import math 
import matplotlib.pyplot as plt

def gen_cad(params):
    line_a1= params[0]
    line_a2= params[1]
    line_b1= params[2]
    line_b2= params[3]
    line_d1= params[4]

    vessel = Vessel('vessel_c.FCStd') 
    
    vessel.set_low1_len(line_a1)
    vessel.set_low2_len(line_a2)
    vessel.set_medium1_len(line_b1)
    vessel.set_medium2_len(line_b2)
    vessel.set_bow_len(line_d1)
    
    vessel.create_stl(1)

def main_cad():
    remus_volume=193537.425  # in cubic cm 

    #optimal_nt=np.array([29.79,67.30,81.90,95,89.52,66.74,38.26,24.93])
    dp= np.loadtxt('./design_points.csv', delimiter=',')
    #print('design_points are:',dp,'shape:',dp.shape)

    #Importing vessel seed design
    vessel = Vessel('vessel_c.FCStd') 
    #dp= np.append(np.array([b,D]),ds[i])
    #print('******design point is:******',dp,'dp shape  is:',dp.shape)

    ######Setting vehicle details###

    #d= dp[1]


    line_a1= dp[0]
    line_a2= dp[1]
    line_b1= dp[2]
    line_b2= dp[3]
    line_d1= dp[4]


    # a_ext=dp[4]
    # b_ext=dp[5]SSSS
    # c_ext=dp[6]

    # a=head_a+a_ext # type: ignore
    # b=head_b+b_ext
    # c=head_c+c_ext



    vessel.set_low1_len(line_a1)
    vessel.set_low2_len(line_a2)
    vessel.set_medium1_len(line_b1)
    vessel.set_medium2_len(line_b2)
    vessel.set_bow_len(line_d1)
    # vessel.set_high1_len(line_c1)
    # vessel.set_high2_len(line_c2)

    ##########
    hull_line_l1=vessel.get_low1_details()
    print('----> hull line low:',hull_line_l1)
    
    hull_line_l2=vessel.get_low2_details()
    print('----> hull line low:',hull_line_l2)


    hull_line_m1=vessel.get_medium1_details()
    print('----> hull line medium:',hull_line_m1)
    
    hull_line_m2=vessel.get_medium2_details()
    print('----> hull line medium:',hull_line_m2)


    # hull_line_h1=vessel.get_high1_details()
    # print('----> hull line high:',hull_line_h1)
    # hull_line_h2=vessel.get_high2_details()
    # print('----> hull line high:',hull_line_h2)

    hull_line_d1=vessel.get_bow_details()
    print('----> hull line bulbus_bow1:',hull_line_d1)


    ###Get volume and apped to design point
    # volume=vessel.get_outer_volume()
    # hull= np.array(a,b,c)
    # dp=np.append(hull,volume)
    # print('******design point is:******',dp,'dp shape  is:',dp.shape)

    # np.savetxt('design_points.csv',dp,delimiter=',')
    #########
    # def estimate_low(a,d,x,n): 
    #     return 0.5*d*np.power((1-np.power(((x-a)/a),2)),(1/n))





    vessel.create_stl(1)
# main_cad()
