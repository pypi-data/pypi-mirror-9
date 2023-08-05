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
import numpy
#
import crosscat.cython_code.State as State
import crosscat.utils.general_utils as gu
import crosscat.utils.sample_utils as su


def calc_ari(group_idx_list_1, group_idx_list_2):
    def make_set_dict(list):
        set_dict = defaultdict(set)
        add_element = lambda (idx, group): set_dict[group].add(idx)
        map(add_element, enumerate(list))
        return set_dict
    def check_short_circuit(set_dict_1, list_1, set_dict_2, list_2):
        both_all_apart = len(set_dict_1) == len(list_1) and \
                len(set_dict_2) == len(list_2)
        both_all_together = len(set_dict_1) == 1 and len(set_dict_2) == 1
        return both_all_apart or both_all_together
    def gen_contingency_data(set_dict_1, set_dict_2):
        ##https://en.wikipedia.org/wiki/Rand_index#The_contingency_table
        array_dim = (len(set_dict_1), len(set_dict_2))
        Ns = numpy.ndarray(array_dim)
        for idx_1, value1 in enumerate(set_dict_1.values()):
            for idx_2, value2 in enumerate(set_dict_2.values()):
                Ns[idx_1, idx_2] = len(value1.intersection(value2))
        As = Ns.sum(axis=1)
        Bs = Ns.sum(axis=0)
        return Ns, As, Bs
    def choose_2_sum(x):
        return sum(x * (x - 1) / 2.0)
    group_idx_dict_1 = make_set_dict(group_idx_list_1)
    group_idx_dict_2 = make_set_dict(group_idx_list_2)
    if check_short_circuit(group_idx_dict_1, group_idx_list_1,
            group_idx_dict_2, group_idx_list_2):
        return 1.0
    Ns, As, Bs = gen_contingency_data(group_idx_dict_1, group_idx_dict_2)
    n_choose_2 = choose_2_sum(numpy.array([len(group_idx_list_1)]))
    cross_sums = choose_2_sum(Ns[Ns>1])
    a_sums = choose_2_sum(As)
    b_sums = choose_2_sum(Bs)
    numerator = n_choose_2 * cross_sums - a_sums * b_sums
    denominator = .5 * n_choose_2 * (a_sums + b_sums) - a_sums * b_sums
    return numerator / denominator

def determine_synthetic_column_ground_truth_assignments(num_cols, num_views):
    num_cols_per_view = num_cols / num_views
    view_assignments = []
    for view_idx in range(num_views):
        view_assignments.extend([view_idx] * num_cols_per_view)
    return view_assignments

def truth_from_permute_indices(data_inverse_permutation_indices, num_rows,num_cols,num_views, num_clusters):
    # We assume num_rows is divisible by num_clusters and num_cols is divisible by num_views
    num_cols_per_view = num_cols/num_views
    view_assignments = []
    for viewindx in range(num_views):
        view_assignments = view_assignments + [viewindx]*num_cols_per_view

    num_rows_per_cluster = num_rows/num_clusters
    
    reference_list = []
    for clusterindx in range(num_clusters):
        reference_list = reference_list + [clusterindx]*num_rows_per_cluster
        
    X_D_truth = []
    for viewindx in range(num_views):
        X_D_truth.append([a for (b,a) in sorted(zip(data_inverse_permutation_indices[viewindx], reference_list))])
        
        
    return view_assignments, X_D_truth

def ARI_CrossCat(Xc, Xrv, XRc, XRrv):
    ''' Adjusted Rand Index (ARI) calculation for a CrossCat clustered table
    
    To calculate ARI based on the CrossCat partition, each cell in the
    table is considered as an instance to be assigned to a cluster. A cluster
    is defined by both the view index AND the category index. In other words,
    if, and only if, two cells, regardless of which columns and rows they belong
    to, are lumped into the same view and category, the two cells are considered
    to be in the same cluster. 

    For a table of size Nrow x Ncol
    Xc: (1 x Ncol) array of view assignment for each column.
        Note: It is assumed that the view indices are consecutive integers
        starting from 0. Hence, the number of views is equal to highest
        view index plus 1.
    Xrv: (Nrow x Nview) array where each row is the assignmennt of categories for the
        corresponding row in the data table. The i-th element in a row
        corresponds to the category assignment of the i-th view of that row.
    XRc and XRrv have the same format as Xr and Xrv respectively.
    The ARI index is calculated from the comparison of the table clustering
    define by (XRc, XRrv) and (Xc, Xrv).
    '''
    Xrv = Xrv.T
    XRrv = XRrv.T
    # Find the highest category index of all views
    max_cat_index = numpy.max(Xrv)
    # re-assign category indices so that they have different values in
    # different views
    Xrv = Xrv + numpy.arange(0,Xrv.shape[1])*(max_cat_index+1)
    
    # similarly for the reference partition
    max_cat_index = numpy.max(XRrv)
    XRrv = XRrv + numpy.arange(0,XRrv.shape[1])*(max_cat_index+1)
    
    # Table clustering assignment for the first partition
    CellClusterAssgn = numpy.zeros((Xrv.shape[0], Xc.size))
    for icol in range(Xc.size):
        CellClusterAssgn[:,icol]=Xrv[:,Xc[icol]]
    # Flatten the table to a 1-D array compatible with the ARI function 
    CellClusterAssgn = CellClusterAssgn.reshape(CellClusterAssgn.size)
        
    # Table clustering assignment for the second partition
    RefCellClusterAssgn = numpy.zeros((Xrv.shape[0], Xc.size))
    for icol in range(Xc.size):
        RefCellClusterAssgn[:,icol]=XRrv[:,XRc[icol]]
    # Flatten the table
    RefCellClusterAssgn = RefCellClusterAssgn.reshape(RefCellClusterAssgn.size)
        
    # Compare the two partitions using ARI
    ARI = calc_ari(RefCellClusterAssgn, CellClusterAssgn)
    ARI_viewonly = calc_ari(Xc, XRc)

    return ARI, ARI_viewonly

def get_column_ARI(X_L, view_assignment_truth):
    view_assignments = X_L['column_partition']['assignments']
    ARI = calc_ari(view_assignments, view_assignment_truth)
    return ARI

def get_column_ARIs(X_L_list, view_assignment_truth):
    get_column_ARI_helper = lambda X_L: \
            get_column_ARI(X_L, view_assignment_truth)
    ARIs = map(get_column_ARI_helper, X_L_list)
    return ARIs

def multi_chain_ARI(X_L_list, X_D_List, view_assignment_truth, X_D_truth, return_list=False):
    num_chains = len(X_L_list)
    ari_table = numpy.zeros(num_chains)
    ari_views = numpy.zeros(num_chains)
    for chainindx in range(num_chains):
        view_assignments = X_L_list[chainindx]['column_partition']['assignments']
        curr_ari_table, curr_ari_views = ARI_CrossCat(numpy.asarray(view_assignments), numpy.asarray(X_D_List[chainindx]), numpy.asarray(view_assignment_truth), numpy.asarray(X_D_truth))
        ari_table[chainindx] = curr_ari_table
        ari_views[chainindx] = curr_ari_views

    ari_table_mean = numpy.mean(ari_table)
    ari_views_mean = numpy.mean(ari_views)
    if return_list:
        return ari_table, ari_views
    else:
        return ari_table_mean, ari_views_mean

def create_test_set(M_c, T, X_L, X_D, n_test, seed_seed=0):
    sample_row_idx = len(T) + 1
    n_cols = len(T[0])
    Y = []
    Q = [(sample_row_idx, col_idx) for col_idx in range(n_cols)]
    int_generator = gu.int_generator(seed_seed)
    get_next_seed = lambda: int_generator.next()
    samples = su.simple_predictive_sample(M_c, X_L, X_D, Y, Q, get_next_seed, n=n_test)
    return samples

# FIXME: remove dependence on T as input
#        by making p_State constructor actually use only suffstats
def calc_mean_test_log_likelihood(M_c, T, X_L, X_D, T_test):
    state = State.p_State(M_c, T, X_L, X_D)
    test_log_likelihoods = map(state.calc_row_predictive_logp, T_test)
    mean_test_log_likelihood = numpy.mean(test_log_likelihoods)
    return mean_test_log_likelihood
def calc_mean_test_log_likelihoods(M_c, T, X_L_list, X_D_list, T_test):
    mean_test_log_likelihoods = []
    for X_L, X_D in zip(X_L_list, X_D_list):
        mean_test_log_likelihood = calc_mean_test_log_likelihood(M_c, T, X_L,
                X_D, T_test)
        mean_test_log_likelihoods.append(mean_test_log_likelihood)
    return mean_test_log_likelihoods
