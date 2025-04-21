import argparse
import os
import numpy as np

# from cad_gen.run_script import main_cad
from utils import *
import pandas as pd
import shutil
import glob 
import subprocess
import time
#from run_dexof import *
import sys 
from cfd_sim import run_cfd
from cad_gen import run_script, vessel_class
# from cfd_sim.dexof_reader_class import parse_dex_file
import GPyOpt
from subprocess import PIPE, run
import random
from numpy.random import seed


import optuna
import xgboost as xgb
from sklearn.metrics import mean_squared_error

# initial parameters (mm unit)  
# --- Load initial data if available
try:
    trials_df = pd.read_csv("./initial_design_points.csv")
    X_obs = trials_df[["a1", "a2", "b1", "b2", "d1"]].values
    y_obs = trials_df["Y"].values
except FileNotFoundError:
    X_obs = np.empty((0, 5))
    y_obs = np.empty((0, ))
    
# a_ext=0;c_ext=0                                # for exp2 set a_ext & c_ext = 2500 ; It define allowable extension in nose_length & tail legth during optimization. 
data_file_name='./data_bo/bo_hull.csv'      # data file name- change for each experiment
data_opt_name = './result_opt.csv'
#

sys.dont_write_bytecode = True
cad_storage_name= './cad_gen/design_points.csv'
cfd_storage_name= './cfd_sim/design_points.csv'

# path to log all runs
# DATA_LOG_CAD_PATH = './cad_gen/design_points.csv'
# DATA_LOG_CFD_PATH = './cad_gen/design_points.csv'
BEST_LOG_PATH = "./result_opt.csv"

# stl storage
src= './cad_gen/stl_repo'
dst='./cfd_sim/stl_cfd'

# resistance initial
resistance_storage = [y_obs] 

print("Initial values:")
print("X:\n", X_obs)
print("Y:\n", y_obs)

def delete_dir(loc):
    print('*Deleted directory:',loc)
    shutil.rmtree(loc)

def copy_dir(src,dst):
	print('*Copied directory from',src,'to destination:',dst)
	shutil.copytree(src, dst)

def deletefiles(loc):
	print('Deleted files from location:',loc)
	file_loc= loc+'/*'
	files = glob.glob(file_loc)
	for f in files:
		os.remove(f)

def deletefiles(loc):
    print('Deleted files from location',loc)
    file_loc = loc+'/*'
    files = glob.glob(file_loc)
    for f in files:
         os.remove(f)

def saveOpt(loc):
	print("Create files from location:", loc)
	files_loc = loc + "/*"
	files = glob.glob(files_loc)
	for f in files:
		os.mkdir(f)

def copy_file(src,dst):
     print('*Copied file from',src,'to destination:',dst)
     shutil.copy(src,dst)

def save_design_points(x):
    # np.set_printoptions(precision=4)
    # print(x)
    np.savetxt(cad_storage_name,x,  delimiter=',')
    np.savetxt(cfd_storage_name,x,  delimiter=',')
          
def run_cad_cfd(x):
    
    x = np.array(x)  # Ensure it's a NumPy array
    
    print('shape of x:', x.shape)
    print(','.join([str(v) for v in x]))

    save_design_points(x)

    delete_dir(dst)
    # subprocess.call('./cad_gen/run_cad.sh')
    prev = os.path.abspath(os.getcwd()) # Save the real cwd
    print('prev is',prev)
    cad_gen_path= prev+'/cad_gen'
    os.chdir(cad_gen_path)
    run_script.main_cad()
    os.chdir(prev)
    copy_dir(src,dst)
    deletefiles(src)

    prev = os.path.abspath(os.getcwd()) # Save the real cwd
    print('prev is',prev)
    cfd_sim_path= prev+'/cfd_sim'
    print('func path is:',cfd_sim_path)
    os.chdir(cfd_sim_path)
    result = run_cfd.main_run()
    resistance_storage.append(result)
    print('****Resistance resistance_storage:',resistance_storage)
    os.chdir(prev)
    return result

# --- Train XGBoost surrogate model
def train_xgb_model(X, y):
    model = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=100)
    model.fit(X, y)
    return model

# Define the search space
def objective(trial):
    global X_obs, y_obs

    x = np.array([
        trial.suggest_float("a1", 0.02, 0.05),
        trial.suggest_float("a2", 0.02, 0.05),
        trial.suggest_float("b1", 0.034, 0.074),
        trial.suggest_float("b2", 0.04, 0.08),
        trial.suggest_float("d1", 0.85, 1.0)
    ]).reshape(1, -1)

    # Use surrogate if we have enough data
    if len(X_obs) >= 10:
        model = train_xgb_model(X_obs, y_obs)
        y_pred = model.predict(x)[0]

        # Estimate uncertainty using validation error (optional)
        y_val = model.predict(X_obs)
        error = mean_squared_error(y_obs, y_val)

        print(f"[Surrogate] Predicted Resistance: {y_pred:.4f}, Est. Error: {error:.4f}")
        if error < 0.02:
            return float(y_pred)  # Skip CFD if surrogate is confident

    # Run CFD simulation
    y = run_cad_cfd(x.flatten().tolist())
    
    X_obs = np.vstack([X_obs, x])
    y_obs = np.append(y_obs, y)
    with open(cad_storage_name, "a") as f:
        f.write(",".join([f"{v:.6f}" for v in x.flatten()]) + f",{y:.6f}\n")
    with open(data_file_name, "a") as f:
        f.write(",".join([f"{v:.6f}" for v in x.flatten()]) + f",{y:.6f}\n")


    return y

def run_bo(run_id=0,aquistion='EI',seeds=0):
    global a_ext, c_ext
	################################################
    deletefiles('./cad_sim/fig_hull')
	
    # maximum boundary
    # bounds = [{'name': 'n', 'type': 'continuous', 'domain': (1,50)},
    #         {'name': 'theta', 'type': 'continuous', 'domain': (1,50)},
    #         {'name': 'a_ext', 'type': 'continuous', 'domain': (0,a_ext)},
    #         {'name': 'c_ext', 'type': 'continuous', 'domain': (0,c_ext)}]
    # bounds = [{'name': 'a1', 'type': 'continuous', 'domain': (0,0.07)},
    #           {'name': 'a2', 'type': 'continuous', 'domain': (0,0.07)},
    #           {'name': 'b1', 'type': 'continuous', 'domain': (0,0.1)},
    #           {'name': 'b2', 'type': 'continuous', 'domain': (0,0.1)},
    #           {'name': 'c1', 'type': 'continuous', 'domain': (0,0.1)},
    #           {'name': 'c2', 'type': 'continuous', 'domain': (0,0.1)},
    #           {'name': 'd1', 'type': 'continuous', 'domain': (0.01,0.05)},]
    bounds = [{'name': 'a1', 'type': 'continuous', 'domain': (0.02,0.05)},
              {'name': 'a2', 'type': 'continuous', 'domain': (0.02,0.05)},              
              {'name': 'b1', 'type': 'continuous', 'domain': (0.034,0.074)},
              {'name': 'b1', 'type': 'continuous', 'domain': (0.04,0.08)},
              {'name': 'd1', 'type': 'continuous', 'domain': (0.85,1)},]


    print('Bound is:',bounds)
    max_time  = None 
    max_iter  =  50
    num_iter=10
    batch= int(max_iter/num_iter)
	
    #################################################
    already_saved_opt_file = len(glob.glob(data_opt_name))
    
    if(already_saved_opt_file > 0):
         print('saved opt file exist?:',already_saved_opt_file)
         deletefiles(data_opt_name)

    already_run = len(glob.glob(data_file_name))
    print('file exist?:',already_run)

    print('Batch is:',batch)

    # make predictable random (numpy.random.seed())
    seed(seeds)
    for i in range(num_iter): 
        if already_run==1:
            evals = pd.read_csv(data_file_name, index_col=0, delimiter="\t")
            Y = np.array([[x] for x in evals["Y"]])
            X = np.array(evals.filter(regex="var*"))
            myBopt2D = GPyOpt.methods.BayesianOptimization(run_cad_cfd, bounds,model_type = 'GP',X=X, Y=Y,
                                              acquisition_type=aquistion, normalize_Y=False, 
                                              exact_feval = True) 
            print('In other runs run')
        else: 
            #  createfiles(data_file_name)
             open(data_file_name,'w')
             myBopt2D = GPyOpt.methods.BayesianOptimization(f=run_cad_cfd,
                                              domain=bounds,
                                              model_type = 'GP',
                                              acquisition_type=aquistion,  normalize_Y=False, 
                                              exact_feval = True) 
             already_run=1
             print('In 1st run')
        print('------Running batch is:',i) 

        # --- Run the optimization 
        try:
            myBopt2D.run_optimization(batch,verbosity=True)
            pass   
        except KeyboardInterrupt:
            pass

        sim_data_x= myBopt2D.X
        myBopt2D.save_evaluations(data_file_name)

    print("Value of (a1, a2, b1, b2, d1) that minimises the resistance : "+str(myBopt2D.x_opt))    
    print("Optimum resistance is: " + str(myBopt2D.fx_opt))

    myBopt2D.plot_acquisition()  
    myBopt2D.plot_convergence()


    np.savetxt(data_opt_name, ([myBopt2D.fx_opt, myBopt2D.x_opt[0], myBopt2D.x_opt[1], myBopt2D.x_opt[2]]), delimiter=",")

if __name__=='__main__':
    # run=[1]; seeds=[17]	
    # aqu2='LCB'
    
    # for i in range(len(run)):
    #      run_bo(run[i],aqu2,seeds[i])
    study = optuna.create_study(direction="minimize")

    try:
        study.optimize(objective, n_trials=50)
    except KeyboardInterrupt:
        print("Optimization interrupted.")

    best_params = study.best_params
    best_value = study.best_value

    print("\nBest parameters:")
    for k, v in best_params.items():
        print(f"  {k}: {v}")
    print(f"\nMinimum resistance: {best_value}")

    # Save best result
    best_row = [best_value] + [best_params[k] for k in ["a1", "a2", "b1", "b2", "d1"]]
    np.savetxt(BEST_LOG_PATH, [best_row], delimiter=",", header="Y,a1,a2,b1,b2,d1", comments="")
    
    # run_script.gen_cad(best_row)
