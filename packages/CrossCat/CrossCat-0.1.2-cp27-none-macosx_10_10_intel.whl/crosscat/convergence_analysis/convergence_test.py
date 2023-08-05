#
#   Copyright (c) 2010-2014, MIT Probabilistic Computing Project
#
#   Lead Developers: Dan Lovell and Jay Baxter
#   Authors: Dan Lovell, Baxter Eaves, Jay Baxter, Vikash Mansinghka
#   Research Leads: Vikash Mansinghka, Patrick Shafto
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
import argparse
import csv
import time
#
import crosscat.utils.data_utils as du
import crosscat.CrossCatClient as ccc
import crosscat.utils.file_utils as f_utils
import crosscat.utils.convergence_test_utils as ctu


# Parse input arguments
parser = argparse.ArgumentParser()
parser.add_argument('--filename', default=None,
                    type=str)
parser.add_argument('--ari_logfile', default='daily_ari_logs.csv',
                    type=str)
parser.add_argument('--inf_seed', default=0, type=int)
parser.add_argument('--gen_seed', default=0, type=int)
parser.add_argument('--num_transitions', default=500, type=int)
parser.add_argument('--N_GRID', default=31, type=int)
parser.add_argument('--max_rows', default=1000, type=int)
parser.add_argument('--num_clusters', default=10, type=int)
parser.add_argument('--num_views', default=2, type=int)
parser.add_argument('--num_cols', default=16, type=int)
parser.add_argument('--numChains',default=50, type = int)
parser.add_argument('--block_size',default=20, type = int)
#
args = parser.parse_args()
filename = args.filename
ari_logfile = args.ari_logfile
inf_seed = args.inf_seed
gen_seed = args.gen_seed
num_transitions = args.num_transitions
N_GRID = args.N_GRID
max_rows = args.max_rows
num_clusters = args.num_clusters
num_views = args.num_views
num_cols = args.num_cols
numChains = args.numChains
block_size = args.block_size


engine = ccc.get_CrossCatClient('hadoop', seed = inf_seed)

if filename is not None:
    # Load the data from table and sub-sample entities to max_rows
    T, M_r, M_c = du.read_model_data_from_csv(filename, max_rows, gen_seed)
    truth_flag = 0
else:
    T, M_r, M_c, data_inverse_permutation_indices = \
        du.gen_factorial_data_objects(gen_seed, num_clusters,
                                      num_cols, max_rows, num_views,
                                      max_mean=100, max_std=1,
                                      send_data_inverse_permutation_indices=True)
    view_assignment_truth, X_D_truth = ctu.truth_from_permute_indices(data_inverse_permutation_indices, max_rows,num_cols,num_views, num_clusters)
    truth_flag = 1

        
num_rows = len(T)
num_cols = len(T[0])

ari_table = []
ari_views = []

print 'Initializing ...'
# Call Initialize and Analyze
M_c, M_r, X_L_list, X_D_list = engine.initialize(M_c, M_r, T, n_chains = numChains)
if truth_flag:
    tmp_ari_table, tmp_ari_views = ctu.multi_chain_ARI(X_L_list,X_D_list, view_assignment_truth, X_D_truth)
    ari_table.append(tmp_ari_table)
    ari_views.append(tmp_ari_views)
            
completed_transitions = 0

n_steps = min(block_size, num_transitions)
print 'Analyzing ...'
while (completed_transitions < num_transitions):
    # We won't be limiting by time in the convergence runs
    X_L_list, X_D_list = engine.analyze(M_c, T, X_L_list, X_D_list, kernel_list=(),
                                        n_steps=n_steps, max_time=-1)
    
    if truth_flag:
        tmp_ari_table, tmp_ari_views = ctu.multi_chain_ARI(X_L_list,X_D_list, view_assignment_truth, X_D_truth)
        ari_table.append(tmp_ari_table)
        ari_views.append(tmp_ari_views)
        
    else:
        # Not sure we want to save the models for convergence testing 
        saved_dict = {'T':T, 'M_c':M_c, 'X_L_list':X_L_list, 'X_D_list': X_D_list}
        pkl_filename = 'model_{!s}.pkl.gz'.format(str(completed_transitions))
        f_utils.pickle(saved_dict, filename = pkl_filename)

    completed_transitions = completed_transitions+block_size
    print completed_transitions
    
# Always save the last model
saved_dict = {'T':T, 'M_c':M_c, 'X_L_list':X_L_list, 'X_D_list': X_D_list}
pkl_filename = 'model_{!s}.pkl.gz'.format('last')
f_utils.pickle(saved_dict, filename = pkl_filename)

if truth_flag:
    with open(ari_logfile, 'a') as outfile:
        csvwriter=csv.writer(outfile,delimiter=',')
        csvwriter.writerow([time.ctime(), num_transitions, block_size, max_rows, num_cols, num_views, num_clusters, ari_views, ari_table])
