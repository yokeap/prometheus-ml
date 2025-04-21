"""
Created on Mon Feb  7 17:02:38 2022

@author:Siwakorn Sukprasertchai (Kasetsart University)
"""

import numpy as np
import os 
import subprocess
import glob 
import time
import re
import shutil

data_file_name='./data/optim_run.csv' 

path_stl = './stl_cfd/'
base_dexfile='rough_mesh.dex'
result_folder='./result_logs'
case_folder_name = 'hull_opt'
stl_name = 'ship_gen'

# not sure, i think it is max value of resistance
default_max=11000


def run_dex(mesh=0.1):
    print('--------------------------------------')
    print('----------- Running CFD --------------')

    arg_=['./run_of.sh']
    input_stl_file= path_stl
    print('stl file name:',stl_name)
    input_stl_file+=stl_name + ".stl"
    print('full path of stl file:',input_stl_file)

    arg_.append("./rough_mesh.dex")
    # arg_.append("./ship_gen.stl")
    arg_.append(input_stl_file)

    print(arg_)

    # run run_of.sh
    subprocess.call(arg_)

    try:
        # src_resultfile='./'+ case_folder_name +'/results.log'
        
        # with open(src_resultfile, 'r') as f:
        #     result_output=f.read()

        # pressure_x_found = re.findall(r"pressure\s+:\s*\([-+]?\s*\d*\.\d*",result_output)
        # viscous_x_found = re.findall(r"viscous\s+:\s*\([-+]?\s*\d*\.\d*",result_output)

        # if pressure_x_found[-2] and viscous_x_found[-2]:
        #     resistance = 2*(-float(pressure_x_found[-2].split(': (')[1])  + (-float(viscous_x_found[-2].split(': (')[1])))
        # else:
        #     resistance = default_max
        # if pressure_x_found[-2]: 
        #     pressure_x = pressure_x_found[-2].split(': (')[1]
        #     pressure_x= float(pressure_x) * -2
        # else: 
        #     pressure_x_found = default_max
        # if viscous_x_found[-2]:
        #     viscous_x = viscous_x_found[-2].split(': (')[1]
        #     viscous_x = float(viscous_x) * -2
        # else: 
        #     viscous_x = default_max 

        # print("######################################") 
        # print("######################################")  
        # print('Pressure is:', pressure_x)
        # print('Viscous is:', viscous_x)
        # print('Resistance is:', resistance)
        # print("######################################")

        src_resultfile='./'+ case_folder_name +'/results.log'
        
        with open(src_resultfile, 'r') as f:
            result_output=f.read()

        resistance_found = re.findall(r"resistance:\s*([-+]?\d*\.?\d+)",result_output)

        if resistance_found:
            resistance = resistance_found[-1]
        else:
            resistance = default_max

        print("######################################") 
        print("######################################")  
        print('Resistance is:', resistance)
        print("######################################")

        return float(resistance)
    except:
        return (default_max*2)

def main_run():
    already_run = len(glob.glob(data_file_name))
    print('file exist?:',already_run)

    # make multi_runresults as 2D variable for stacking data 
    if already_run==1:
        multi_runresults=np.loadtxt(data_file_name, delimiter=",",skiprows=0, dtype=np.float32)
        multi_runresults= np.atleast_2d(multi_runresults)
        #print('shape of multi_runresults:',multi_runresults.shape)
    
    design_set_load= np.loadtxt('./design_points.csv', delimiter = ",")
    mesh = 0.1
    Fd_found= run_dex(mesh)
    return Fd_found

# main_run()
