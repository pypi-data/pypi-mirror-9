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
#
import pylab
import numpy
#
import crosscat.cython_code.State as State
import crosscat.utils.data_utils as du


# parse input
parser = argparse.ArgumentParser()
parser.add_argument('--gen_seed', default=0, type=int)
parser.add_argument('--inf_seed', default=0, type=int)
parser.add_argument('--num_clusters', default=4, type=int)
parser.add_argument('--num_cols', default=16, type=int)
parser.add_argument('--num_rows', default=300, type=int)
parser.add_argument('--num_splits', default=2, type=int)
parser.add_argument('--max_mean', default=10, type=float)
parser.add_argument('--max_std', default=0.3, type=float)
parser.add_argument('--num_transitions', default=300, type=int)
parser.add_argument('--N_GRID', default=31, type=int)
args = parser.parse_args()
#
gen_seed = args.gen_seed
inf_seed = args.inf_seed
num_clusters = args.num_clusters
num_cols = args.num_cols
num_rows = args.num_rows
num_splits = args.num_splits
max_mean = args.max_mean
max_std = args.max_std
num_transitions = args.num_transitions
N_GRID = args.N_GRID

# create the data
if True:
    T, M_r, M_c = du.gen_factorial_data_objects(
        gen_seed, num_clusters,
        num_cols, num_rows, num_splits,
        max_mean=max_mean, max_std=max_std,
        )
else:
    with open('SynData2.csv') as fh:
        import numpy
        import csv
        T = numpy.array([
                row for row in csv.reader(fh)
                ], dtype=float).tolist()
        M_r = du.gen_M_r_from_T(T)
        M_c = du.gen_M_c_from_T(T)


# create the state
p_State = State.p_State(M_c, T, N_GRID=N_GRID, SEED=inf_seed)
p_State.plot_T(filename='T')

# transition the sampler
print "p_State.get_marginal_logp():", p_State.get_marginal_logp()
for transition_idx in range(num_transitions):
    print "transition #: %s" % transition_idx
    p_State.transition()
    counts = [
        view_state['row_partition_model']['counts']
        for view_state in p_State.get_X_L()['view_state']
        ]
    format_list = '; '.join([
            "s.num_views: %s",
            "cluster counts: %s",
            "s.column_crp_score: %.3f",
            "s.data_score: %.1f",
            "s.score:%.1f",
            ])
    values_tuple = (
        p_State.get_num_views(),
        str(counts),
        p_State.get_column_crp_score(),
        p_State.get_data_score(),
        p_State.get_marginal_logp(),
        )
    print format_list % values_tuple
    plot_filename = 'X_D'
    save_filename = 'last_state.pkl.gz'
    if transition_idx % 10 == 0:
        plot_filename = 'iter_%s_X_D' % transition_idx
        save_filename = 'iter_%s_state.pkl.gz' % transition_idx
    p_State.plot(filename=plot_filename)
    p_State.save(filename=save_filename, M_r=M_r, M_c=M_c, T=T)

# # print the final state
# X_D = p_State.get_X_D()
# X_L = p_State.get_X_L()
# print "X_D:", X_D
# print "X_L:", X_L
# for view_idx, view_state_i in enumerate(p_State.get_view_state()):
#     print "view_state_i:", view_idx, view_state_i
# print p_State

# # test generation of state from X_L, X_D
# p_State_2 = State.p_State(M_c, T, X_L, X_D)
# X_D_prime = p_State_2.get_X_D()
# X_L_prime = p_State_2.get_X_L()

# print "X_D_prime:", X_D_prime
# print "X_L_prime:", X_L_prime

# p_State.transition_views(); p_State.get_X_L()['view_state'][0]['row_partition_model']
