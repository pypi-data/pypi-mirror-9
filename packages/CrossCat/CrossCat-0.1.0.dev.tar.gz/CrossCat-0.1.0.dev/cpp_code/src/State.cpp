/*
*   Copyright (c) 2010-2014, MIT Probabilistic Computing Project
*
*   Lead Developers: Dan Lovell and Jay Baxter
*   Authors: Dan Lovell, Baxter Eaves, Jay Baxter, Vikash Mansinghka
*   Research Leads: Vikash Mansinghka, Patrick Shafto
*
*   Licensed under the Apache License, Version 2.0 (the "License");
*   you may not use this file except in compliance with the License.
*   You may obtain a copy of the License at
*
*       http://www.apache.org/licenses/LICENSE-2.0
*
*   Unless required by applicable law or agreed to in writing, software
*   distributed under the License is distributed on an "AS IS" BASIS,
*   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
*   See the License for the specific language governing permissions and
*   limitations under the License.
*/
#include "State.h"


using namespace std;
using boost::numeric::ublas::matrix;
using boost::numeric::ublas::project;
using boost::numeric::ublas::range;


// FIXME: shouldn't need T, not really using suffstats here
State::State(const MatrixD& data,
             vector<string> GLOBAL_COL_DATATYPES,
             vector<int> GLOBAL_COL_MULTINOMIAL_COUNTS,
             vector<int> global_row_indices,
             vector<int> global_col_indices,
             map<int, CM_Hypers> HYPERS_M,
             vector<vector<int> > column_partition,
             double COLUMN_CRP_ALPHA,
             vector<vector<vector<int> > > row_partition_v,
             vector<double> row_crp_alpha_v,
             vector<double> ROW_CRP_ALPHA_GRID,
             vector<double> COLUMN_CRP_ALPHA_GRID,
             vector<double> S_GRID,
             vector<double> MU_GRID,
             int N_GRID, int SEED, int CT_KERNEL) : rng(SEED) {
    assert( CT_KERNEL==1 || CT_KERNEL==0);
    ct_kernel = CT_KERNEL;
    column_crp_score = 0;
    data_score = 0;
    global_col_datatypes = construct_lookup_map(global_col_indices,
            GLOBAL_COL_DATATYPES);
    global_col_multinomial_counts = construct_lookup_map(global_col_indices,
            GLOBAL_COL_MULTINOMIAL_COUNTS);
    // construct grids
    construct_base_hyper_grids(data, N_GRID, ROW_CRP_ALPHA_GRID,
            COLUMN_CRP_ALPHA_GRID);
    construct_column_hyper_grids(data, global_col_indices, GLOBAL_COL_DATATYPES,
                                     S_GRID, MU_GRID);
    // actually build the state
    hypers_m = HYPERS_M;
    column_crp_alpha = COLUMN_CRP_ALPHA;
    init_views(data,
               global_row_indices, global_col_indices,
               column_partition, row_partition_v,
               row_crp_alpha_v);
}

State::State(const MatrixD& data,
             vector<string> GLOBAL_COL_DATATYPES,
             vector<int> GLOBAL_COL_MULTINOMIAL_COUNTS,
             vector<int> global_row_indices,
             vector<int> global_col_indices,
             string col_initialization,
             string row_initialization,
             vector<double> ROW_CRP_ALPHA_GRID,
             vector<double> COLUMN_CRP_ALPHA_GRID,
             vector<double> S_GRID,
             vector<double> MU_GRID,
             int N_GRID, int SEED, int CT_KERNEL) : rng(SEED) {
    assert( CT_KERNEL==1 || CT_KERNEL==0);
    ct_kernel = CT_KERNEL;
    column_crp_score = 0;
    data_score = 0;
    if (row_initialization == "") {
        row_initialization = col_initialization;
    }
    global_col_datatypes = construct_lookup_map(global_col_indices,
                           GLOBAL_COL_DATATYPES);
    global_col_multinomial_counts = construct_lookup_map(global_col_indices,
            GLOBAL_COL_MULTINOMIAL_COUNTS);
    // construct grids
    construct_base_hyper_grids(data, N_GRID, ROW_CRP_ALPHA_GRID,
            COLUMN_CRP_ALPHA_GRID);
    construct_column_hyper_grids(data, global_col_indices, GLOBAL_COL_DATATYPES,
                                     S_GRID, MU_GRID);
    //
    init_column_hypers(global_col_indices);
    column_crp_alpha = sample_column_crp_alpha();
    vector<vector<int> > column_partition = generate_col_partition(
            global_col_indices,
            col_initialization);
    vector<double> row_crp_alpha_v = sample_row_crp_alphas(
                                         column_partition.size());
    vector<vector<vector<int> > > row_partition_v = generate_row_partitions(
                global_row_indices,
                row_crp_alpha_v, row_initialization);
    init_views(data,
               global_row_indices, global_col_indices,
               column_partition, row_partition_v,
               row_crp_alpha_v);
}

State::~State() {
    remove_all();
}

int State::get_num_cols() const {
    return view_lookup.size();
}

int State::get_num_views() const {
    return views.size();
}

vector<int> State::get_view_counts() const {
    vector<int> view_counts;
    set<View*>::iterator it;
    for (it = views.begin(); it != views.end(); it++) {
        View& v = (**it);
        int view_num_cols = v.get_num_cols();
        view_counts.push_back(view_num_cols);
    }
    return view_counts;
}

double State::insert_row(vector<double> row_data, int matching_row_idx, int row_idx) {

    bool append_row = (row_idx == -1);

    if(append_row)
        row_idx = (int) (**views.begin()).cluster_lookup.size();
    
    set<View*>::iterator it;
    double score_delta = 0;
    for(it=views.begin(); it!=views.end(); it++) {
        View &v = **it;
        vector<int> global_col_indices = v.get_global_col_indices();
        // append lookup if needed
        if( append_row ){
            Cluster &new_cluster = v.get_new_cluster();
            vector<double> data_subset = extract_columns(row_data, global_col_indices);
            score_delta += v.insert_row(data_subset, new_cluster, matching_row_idx);
            // FIXME: row crp to score_delta?
        }else{
            vector<double> data_subset = extract_columns(row_data, global_col_indices);
            score_delta += v.insert_row(data_subset, matching_row_idx, row_idx);    
        }
        
    }
    return score_delta;
}

double State::insert_feature(int feature_idx, vector<double> feature_data,
                             View& which_view) {
    string col_datatype = global_col_datatypes[feature_idx];
    CM_Hypers& hypers = hypers_m[feature_idx];
    double crp_logp_delta, data_logp_delta;
    double score_delta = calc_feature_view_predictive_logp(feature_data,
                         col_datatype,
                         which_view,
                         crp_logp_delta,
                         data_logp_delta,
                         hypers);
    vector<int> data_global_row_indices = create_sequence(feature_data.size());
    which_view.insert_col(feature_data,
                          data_global_row_indices, feature_idx,
                          hypers);
    view_lookup[feature_idx] = &which_view;
    column_crp_score += crp_logp_delta;
    data_score += data_logp_delta;
    return score_delta;
}

double State::sample_insert_feature(int feature_idx,
                                    vector<double> feature_data,
                                    View& singleton_view) {
    string col_datatype = global_col_datatypes[feature_idx];
    vector<double> unorm_logps = calc_feature_view_predictive_logps(feature_data,
                                 feature_idx);
    double rand_u = draw_rand_u();
    int draw = numerics::draw_sample_unnormalized(unorm_logps, rand_u);
    View& which_view = get_view(draw);
    double score_delta = insert_feature(feature_idx, feature_data, which_view);
    remove_if_empty(singleton_view);
    return score_delta;
}


double State::remove_feature(int feature_idx, vector<double> feature_data,
                             View* &p_singleton_view) {
    string col_datatype = global_col_datatypes[feature_idx];
    CM_Hypers &hypers = hypers_m[feature_idx];
    map<int,View*>::iterator it = view_lookup.find(feature_idx);
    assert(it!=view_lookup.end());
    View &which_view = *(it->second);
    view_lookup.erase(it);
    int view_num_cols = which_view.get_num_cols();
    double data_logp_delta = which_view.remove_col(feature_idx);
    double crp_logp_delta, other_data_logp_delta;
    double score_delta = calc_feature_view_predictive_logp(feature_data,
                         col_datatype,
                         which_view,
                         crp_logp_delta,
                         other_data_logp_delta,
                         hypers);
    //
    if(view_num_cols==1) {
        p_singleton_view = &which_view;
    } else {
        p_singleton_view = &get_new_view();
    }
    column_crp_score -= crp_logp_delta;
    data_score -= data_logp_delta;
    assert(abs(other_data_logp_delta-data_logp_delta)<1E-6);
    return score_delta;
}

double State::transition_feature_gibbs(int feature_idx, vector<double> feature_data) {
    double score_delta = 0;
    View *p_singleton_view;
    score_delta += remove_feature(feature_idx, feature_data, p_singleton_view);
    View &singleton_view = *p_singleton_view;
    score_delta += sample_insert_feature(feature_idx, feature_data, singleton_view);
    return score_delta;
}

double propose_singleton_p = .5;

double State::get_proposal_logp(View& proposed_view) {
    bool is_singleton = proposed_view.get_num_cols() == 0;
    double proposal_logp = 0;
    if(is_singleton) {
        // what is proability of choosing the singleton we're leaving?
        proposal_logp = log(propose_singleton_p) + proposed_view.calc_crp_marginal();
    } else {
        // what is proability of choosing the NON-singleton we're leaving?
        // WARNING: uniform sampling of existing views is baked in
        proposal_logp = log(1 - propose_singleton_p) - log(get_num_views());
    }
    return proposal_logp;
}

double State::get_proposal_log_ratio(View& from_view, View& to_view) {
    // presumes you've already popped the freature from its view!!!
    double proposal_log_numerator = get_proposal_logp(from_view);
    double proposal_log_denominator = get_proposal_logp(to_view);
    double proposal_log_ratio = proposal_log_numerator - proposal_log_denominator;
    return proposal_log_ratio;
}

double State::mh_choose(int feature_idx, vector<double> feature_data, View &proposed_view) {
    double score_delta = 0;
    View &original_view = *view_lookup[feature_idx];

    if(&original_view==&proposed_view) {
        // short circuit: no impact
        return 0;
    }

    // remove feature from model; get score delta to choose current view
    View *p_singleton_view;
    double original_view_score_delta = remove_feature(feature_idx, feature_data, p_singleton_view);
    score_delta = original_view_score_delta;
    View &singleton_view = *p_singleton_view;

    // get score delta to choose proposed view
    double crp_log_delta_new, data_log_delta_new;
    string col_datatype = get(global_col_datatypes, feature_idx);
    CM_Hypers hypers = get(hypers_m, feature_idx);
    double proposed_view_score_delta = calc_feature_view_predictive_logp(feature_data,
                                       col_datatype, proposed_view,
                                       crp_log_delta_new,
                                       data_log_delta_new,
                                       hypers);

    double state_log_ratio = proposed_view_score_delta - original_view_score_delta;
    double proposal_log_ratio = get_proposal_log_ratio(original_view, proposed_view);

    // Metropolis jump
    double log_r = log(draw_rand_u());
    View *p_insert_into;
    if(log_r < state_log_ratio + proposal_log_ratio) {
        p_insert_into = &proposed_view;
    } else {
        p_insert_into = &original_view;
    }
    score_delta += insert_feature(feature_idx, feature_data, *p_insert_into);

    // clean up
    bool original_was_not_singleton = &original_view != &singleton_view;
    remove_if_empty(original_view);
    if(original_was_not_singleton) {
        remove_if_empty(singleton_view);
    }

    return score_delta;
}

// updated kernel with birth-death process
double State::transition_feature_mh(int feature_idx, vector<double> feature_data) {
    double score_delta = 0;
    View *p_proposed_view;

    // do we create a new veiw or move to an existing view?
    bool propose_singleton = (draw_rand_u() < propose_singleton_p);
    if(propose_singleton) {
        p_proposed_view = &get_new_view();
    } else {
        int num_views = views.size();
        int proposed_view_index = draw_rand_i(num_views);
        p_proposed_view = &get_view(proposed_view_index);
    }

    // Metropolis jump
    score_delta = mh_choose(feature_idx, feature_data, *p_proposed_view);

    // clean up
    remove_if_empty(*p_proposed_view);

    return score_delta;
}

double State::transition_features(const MatrixD &data, vector<int> which_features) {
    double score_delta = 0;
    int num_features = which_features.size();
    if(num_features==0) {
        which_features = create_sequence(data.size2());
        // FIXME: use seed to shuffle
        std::random_shuffle(which_features.begin(), which_features.end());
    }
    vector<int>::iterator it;
    for(it=which_features.begin(); it!=which_features.end(); it++) {
        int feature_idx = *it;
        vector<double> feature_data = extract_col(data, feature_idx);
        // kernel selection
        if(ct_kernel == 0) {
            score_delta += transition_feature_gibbs(feature_idx, feature_data);
        } else if(ct_kernel == 1) {
            score_delta += transition_feature_mh(feature_idx, feature_data);
        } else {
            printf("Invalid CT_KERNEL");
            assert(0==1);
        }
    }
    return score_delta;
}

View& State::get_new_view() {
    // FIXME: this is a hack
    // it being necessary suggests perhaps I should not be passing
    // global_row_indices and instead always assume its a sequence of 0..N
    vector<int> first_view_cluster_counts = get_view(0).get_cluster_counts();
    int num_vectors = std::accumulate(first_view_cluster_counts.begin(),
                                      first_view_cluster_counts.end(), 0);
    vector<int> global_row_indices = create_sequence(num_vectors);
    View *p_new_view = new View(global_col_datatypes,
                                global_row_indices,
                                row_crp_alpha_grid, multinomial_alpha_grid, r_grid, nu_grid,
                                vm_b_grid,
                                s_grids, mu_grids, 
                                vm_a_grids, vm_kappa_grids,
                                draw_rand_i());
    views.insert(p_new_view);
    return *p_new_view;
}

View& State::get_view(int view_idx) {
    assert(view_idx <= views.size());
    bool not_new = ((unsigned int) view_idx) < views.size();
    if (not_new) {
        set<View*>::iterator it = views.begin();
        std::advance(it, view_idx);
        return **it;
    } else {
        // This shouldn't happen anymore
        assert(1 == 0);
        return get_new_view();
    }
}

void State::remove_if_empty(View& which_view) {
    if (which_view.get_num_cols() == 0) {
        views.erase(views.find(&which_view));
        which_view.remove_all();
        delete &which_view;
    }
}

void State::remove_all() {
    view_lookup.empty();
    set<View*>::iterator it = views.begin();
    while (it != views.end()) {
        View& which_view = **it;
        which_view.remove_all();
        views.erase(views.find(&which_view));
        delete &which_view;
        it = views.begin();
    }
}

double State::get_column_crp_alpha() const {
    return column_crp_alpha;
}

double State::get_column_crp_score() const {
    return column_crp_score;
}

double State::get_data_score() const {
    set<View*>::const_iterator it;
    double data_score = 0;
    for (it = views.begin(); it != views.end(); it++) {
        double data_score_i = (**it).get_score();
        data_score += data_score_i;
    }
    return data_score;
}

double State::get_marginal_logp() const {
    return column_crp_score + get_data_score();
}

map<string, double> State::get_row_partition_model_hypers_i(
    int view_idx) const {
    set<View*>::const_iterator it = views.begin();
    std::advance(it, view_idx);
    return (**it).get_row_partition_model_hypers();
}

vector<int> State::get_row_partition_model_counts_i(int view_idx) const {
    set<View*>::const_iterator it = views.begin();
    std::advance(it, view_idx);
    return (**it).get_row_partition_model_counts();
}

vector<vector<map<string, double> > > State::get_column_component_suffstats_i(
    int view_idx) const {
    // ordering should be same as column_names
    set<View*>::const_iterator it = views.begin();
    std::advance(it, view_idx);
    assert(it != views.end());
    return (**it).get_column_component_suffstats();
}

vector<CM_Hypers> State::get_column_hypers() const {
    vector<CM_Hypers> column_hypers;
    int num_cols = get_num_cols();
    map<int, CM_Hypers>::const_iterator it;
    for (int global_col_idx = 0; global_col_idx < num_cols; global_col_idx++) {
        it = hypers_m.find(global_col_idx);
        if (it == hypers_m.end()) {
            continue;
        }
        CM_Hypers hypers_i = it->second;
        // FIXME: actually detect
        hypers_i["fixed"] = 0.;
        column_hypers.push_back(hypers_i);
    }
    return column_hypers;
}

map<string, double> State::get_column_partition_hypers() const {
    map<string, double> local_hypers;
    local_hypers["alpha"] = get_column_crp_alpha();
    return local_hypers;
}

vector<int> State::get_column_partition_assignments() const {
    return define_group_ordering(view_lookup, views);
}

vector<int> State::get_column_partition_counts() const {
    return get_view_counts();
}

vector<vector<int> > State::get_X_D() const {
    vector<vector<int> > X_D;
    set<View*>::iterator it;
    for (it = views.begin(); it != views.end(); it++) {
        View& v = **it;
        vector<int> canonical_clustering = v.get_canonical_clustering();
        X_D.push_back(canonical_clustering);
    }
    return X_D;
}

vector<double> State::get_draw(int row_idx, int random_seed) const {
    RandomNumberGenerator rng(random_seed);
    set<View*>::iterator it;
    vector<double> _draw;
    vector<int> global_col_indices;
    for (it = views.begin(); it != views.end(); it++) {
        View& v = **it;
        int randi = rng.nexti(MAX_INT);
        vector<double> draw_i = v.get_draw(row_idx, randi);
        vector<int> global_col_indices_i = v.get_global_col_indices();
        _draw = append(_draw, draw_i);
        global_col_indices = append(global_col_indices, global_col_indices_i);
    }
    int num_cols = get_num_cols();
    vector<double> draw(num_cols);
    for(int idx=0; idx<num_cols; idx++) {
        int col_idx = global_col_indices[idx];
        double value = _draw[idx];
        draw[col_idx] = value;
    }
    return draw;
}

map<int, vector<int> > State::get_column_groups() const {
    map<View*, int> view_to_int = set_to_map(views);
    map<View*, set<int> > view_to_set = group_by_value(view_lookup);
    map<int, vector<int> > view_idx_to_vec;
    set<View*>::iterator it;
    for (it = views.begin(); it != views.end(); it++) {
        View* p_v = *it;
        int view_idx = view_to_int[p_v];
        set<int> int_set = view_to_set[p_v];
        vector<int> int_vec(int_set.begin(), int_set.end());
        std::sort(int_vec.begin(), int_vec.end());
        view_idx_to_vec[view_idx] = int_vec;
    }
    return view_idx_to_vec;
}

double State::transition_view_i(int which_view,
                                map<int, vector<double> > row_data_map) {
    // assumes views set ordering stays constant between calls
    set<View*>::iterator it = views.begin();
    std::advance(it, which_view);
    View& v = **it;
    double score_delta = v.transition(row_data_map);
    data_score += score_delta;
    return score_delta;
}

// helper for cython
double State::transition_view_i(int which_view, const MatrixD& data) {
    vector<int> global_column_indices = create_sequence(data.size2());
    View& v = get_view(which_view);
    vector<int> view_cols = get_indices_to_reorder(global_column_indices,
                            v.global_to_local);
    const MatrixD data_subset = extract_columns(data, view_cols);
    map<int, vector<double> > data_subset_map = construct_data_map(data_subset);
    return v.transition(data_subset_map);
}

double State::transition_views(const MatrixD& data) {
    vector<int> global_column_indices = create_sequence(data.size2());
    //
    double score_delta = 0;
    // ordering doesn't matter, don't need to shuffle
    for (int view_idx = 0; view_idx < get_num_views(); view_idx++) {
        View& v = get_view(view_idx);
        vector<int> view_cols = get_indices_to_reorder(global_column_indices,
                                v.global_to_local);
        const MatrixD data_subset = extract_columns(data, view_cols);
        map<int, vector<double> > data_subset_map = construct_data_map(data_subset);
        score_delta += v.transition(data_subset_map);
    }
    return score_delta;
}

double State::transition_row_partition_assignments(const MatrixD& data,
        vector<int> which_rows) {
    vector<int> global_column_indices = create_sequence(data.size2());
    double score_delta = 0;
    //
    int num_rows = which_rows.size();
    if (num_rows == 0) {
        num_rows = data.size1();
        which_rows = create_sequence(num_rows);
        //FIXME: use own shuffle so seed control is in effect
        std::random_shuffle(which_rows.begin(), which_rows.end());
    }
    set<View*>::iterator svp_it;
    for (svp_it = views.begin(); svp_it != views.end(); svp_it++) {
        // for each view
        View& v = **svp_it;
        vector<int> view_cols = get_indices_to_reorder(global_column_indices,
                                v.global_to_local);
        const MatrixD data_subset = extract_columns(data, view_cols);
        map<int, vector<double> > row_data_map = construct_data_map(data_subset);
        vector<int>::iterator vi_it;
        for (vi_it = which_rows.begin(); vi_it != which_rows.end(); vi_it++) {
            // for each SPECIFIED row
            int row_idx = *vi_it;
            vector<double> vd = row_data_map[row_idx];
            score_delta += v.transition_z(vd, row_idx);
        }
    }
    data_score += score_delta;
    return score_delta;
}

double State::transition_views_zs(const MatrixD& data) {
    vector<int> global_column_indices = create_sequence(data.size2());
    //
    double score_delta = 0;
    // ordering doesn't matter, don't need to shuffle
    for (int view_idx = 0; view_idx < get_num_views(); view_idx++) {
        View& v = get_view(view_idx);
        vector<int> view_cols = get_indices_to_reorder(global_column_indices,
                                v.global_to_local);
        const MatrixD data_subset = extract_columns(data, view_cols);
        map<int, vector<double> > data_subset_map = construct_data_map(data_subset);
        score_delta += v.transition_zs(data_subset_map);
    }
    data_score += score_delta;
    return score_delta;
}

double State::transition_views_row_partition_hyper() {
    double score_delta = 0;
    for (int view_idx = 0; view_idx < get_num_views(); view_idx++) {
        View& v = get_view(view_idx);
        score_delta += v.transition_crp_alpha();
    }
    data_score += score_delta;
    return score_delta;
}

double State::transition_row_partition_hyperparameters(vector<int>
        which_cols) {
    double score_delta = 0;
    set<View*> which_views;
    int num_cols = which_cols.size();
    if (num_cols != 0) {
        vector<int>::iterator it;
        for (it = which_cols.begin(); it != which_cols.end(); it++) {
            View *v_p = view_lookup[*it];
            which_views.insert(v_p);
        }
    } else {
        which_views = views;
    }
    set<View*>::iterator it;
    for (it = which_views.begin(); it != which_views.end(); it++) {
        score_delta += (*it)->transition_crp_alpha();
    }
    data_score += score_delta;
    return score_delta;
}

double State::transition_column_hyperparameters(vector<int> which_cols) {
    double score_delta = 0;
    //
    int num_cols = which_cols.size();
    if (num_cols == 0) {
        num_cols = view_lookup.size();
        which_cols = create_sequence(num_cols);
        //FIXME: use own shuffle so seed control is in effect
        std::random_shuffle(which_cols.begin(), which_cols.end());
    }
    vector<int>::iterator it;
    for (it = which_cols.begin(); it != which_cols.end(); it++) {
        View& which_view = *view_lookup[*it];
        // FIXME: this is a hack, global_to_local should be private and a getter should be used instead
        int local_col_idx = which_view.global_to_local[*it];
        score_delta += which_view.transition_hypers_i(local_col_idx);
    }
    data_score += score_delta;
    return score_delta;
}

double State::transition_views_col_hypers() {
    double score_delta = 0;
    for (int view_idx = 0; view_idx < get_num_views(); view_idx++) {
        View& v = get_view(view_idx);
        score_delta += v.transition_hypers();
    }
    data_score += score_delta;
    return score_delta;
}

double State::calc_feature_view_predictive_logp(vector<double> col_data,
        string col_datatype, View v,
        double& crp_log_delta,
        double& data_log_delta,
        CM_Hypers hypers) const {
    int view_column_count = v.get_num_cols();
    int num_columns = get_num_cols();
    crp_log_delta = numerics::calc_cluster_crp_logp(view_column_count, num_columns,
                    column_crp_alpha);
    //
    vector<int> data_global_row_indices = create_sequence(col_data.size());
    // pass singleton_view down to here, or at least hypers
    data_log_delta = v.calc_column_predictive_logp(col_data, col_datatype,
                     data_global_row_indices,
                     hypers);
    //
    double score_delta = data_log_delta + crp_log_delta;
    return score_delta;
}

vector<double> State::calc_feature_view_predictive_logps(
    vector<double> col_data,
    int global_col_idx) const {
    vector<double> logps;
    CM_Hypers hypers = get(hypers_m, global_col_idx);
    set<View*>::iterator it;
    double crp_log_delta, data_log_delta;
    string col_datatype = get(global_col_datatypes, global_col_idx);
    for (it = views.begin(); it != views.end(); it++) {
        View& v = **it;
        double score_delta = calc_feature_view_predictive_logp(col_data,
                             col_datatype,
                             v,
                             crp_log_delta,
                             data_log_delta,
                             hypers);
        logps.push_back(score_delta);
    }
    return logps;
}

double State::calc_column_crp_marginal() const {
    vector<int> view_counts = get_view_counts();
    int num_cols = get_num_cols();
    return numerics::calc_crp_alpha_conditional(view_counts, column_crp_alpha,
            num_cols, true);
}

vector<double> State::calc_column_crp_marginals(vector<double> alphas_to_score)
const {
    vector<int> view_counts = get_view_counts();
    vector<double> crp_scores;
    vector<double>::iterator it = alphas_to_score.begin();
    int num_cols = get_num_cols();
    for (; it != alphas_to_score.end(); it++) {
        double alpha_to_score = *it;
        double this_crp_score = numerics::calc_crp_alpha_conditional(view_counts,
                                alpha_to_score,
                                num_cols,
                                true);
        crp_scores.push_back(this_crp_score);
    }
    return crp_scores;
}

double State::calc_row_predictive_logp(const vector<double>& in_vd) {
    vector<double> view_sum_predictive_logps;
    vector<int> global_column_indices = create_sequence(in_vd.size());
    set<View*>::iterator svp_it;
    for (svp_it = views.begin(); svp_it != views.end(); svp_it++) {
        // for each view
        View& v = **svp_it;
        vector<int> view_cols = get_indices_to_reorder(global_column_indices,
                                v.global_to_local);
        vector<double> use_vd = extract_columns(in_vd, view_cols);
        vector<double> this_view_predictive_logps = \
                v.calc_cluster_vector_predictive_logps(use_vd);
        double this_view_sum_predictive_logp = \
                                               numerics::logaddexp(this_view_predictive_logps);
        view_sum_predictive_logps.push_back(this_view_sum_predictive_logp);
    }
    double row_predictive_logp = std_vector_sum(view_sum_predictive_logps);
    return row_predictive_logp;
}

double State::transition_column_crp_alpha() {
    // to make score_crp not calculate absolute, need to track score deltas
    // and apply delta to crp_score
    double crp_score_0 = get_column_crp_score();
    vector<double> unorm_logps = calc_column_crp_marginals(column_crp_alpha_grid);
    double rand_u = draw_rand_u();
    int draw = numerics::draw_sample_unnormalized(unorm_logps, rand_u);
    column_crp_alpha = column_crp_alpha_grid[draw];
    column_crp_score = unorm_logps[draw];
    double crp_score_delta = column_crp_score - crp_score_0;
    return crp_score_delta;
}

double State::transition(const MatrixD& data) {
    vector<int> which_transitions = create_sequence(3);
    //FIXME: use own shuffle so seed control is in effect
    std::random_shuffle(which_transitions.begin(), which_transitions.end());
    double score_delta = 0;
    vector<int>::iterator it;
    for (it = which_transitions.begin(); it != which_transitions.end(); it++) {
        int which_transition = *it;
        if (which_transition == 0) {
            score_delta += transition_views(data);
        } else if (which_transition == 1) {
            vector<int> which_features;
            score_delta += transition_features(data, which_features);
        } else if (which_transition == 2) {
            score_delta += transition_column_crp_alpha();
        }
    }
    return score_delta;
}

void State::construct_base_hyper_grids(const MatrixD& data, int N_GRID,
        vector<double> ROW_CRP_ALPHA_GRID,
        vector<double> COLUMN_CRP_ALPHA_GRID) {
    int num_rows = data.size1();
    int num_cols = data.size2();
    if (ROW_CRP_ALPHA_GRID.size() == 0) {
        ROW_CRP_ALPHA_GRID = create_crp_alpha_grid(num_rows, N_GRID);
    }
    if (COLUMN_CRP_ALPHA_GRID.size() == 0) {
        COLUMN_CRP_ALPHA_GRID = create_crp_alpha_grid(num_cols, N_GRID);
    }
    row_crp_alpha_grid = ROW_CRP_ALPHA_GRID;
    column_crp_alpha_grid = COLUMN_CRP_ALPHA_GRID;
    construct_cyclic_base_hyper_grids(N_GRID, num_rows, vm_b_grid);
    construct_continuous_base_hyper_grids(N_GRID, num_rows, r_grid, nu_grid);
    construct_multinomial_base_hyper_grids(N_GRID, num_rows,
                                           multinomial_alpha_grid);
}

void State::construct_column_hyper_grids(const MatrixD& data,
        vector<int> global_col_indices,
        vector<string> GLOBAL_COL_DATATYPES,
        vector<double> S_GRID,
        vector<double> MU_GRID) {
    int N_GRID = r_grid.size();
    vector<int>::iterator it;
    for (it = global_col_indices.begin(); it != global_col_indices.end(); it++) {
        int global_col_idx = *it;
        string col_datatype = GLOBAL_COL_DATATYPES[global_col_idx];
        if (col_datatype == CONTINUOUS_DATATYPE) {
            if (S_GRID.size() == 0) {
                // FIXME: enable separate setting of S_GRID, MU_GRID
                vector<double> col_data = extract_col(data, global_col_idx);
                construct_continuous_specific_hyper_grid(N_GRID, col_data,
                        s_grids[global_col_idx],
                        mu_grids[global_col_idx]);
            } else {
                s_grids[global_col_idx] = S_GRID;
                mu_grids[global_col_idx] = MU_GRID;
            }
        }else if (col_datatype == CYCLIC_DATATYPE){
            vector<double> col_data = extract_col(data, global_col_idx);
                construct_cyclic_specific_hyper_grid(N_GRID, col_data,
                        vm_a_grids[global_col_idx],
                        vm_kappa_grids[global_col_idx]);
        }
    }
}

double State::draw_rand_u() {
    return rng.next();
}

int State::draw_rand_i(int max) {
    return rng.nexti(max);
}

CM_Hypers State::uniform_sample_hypers(int global_col_idx) {
    // presume all grids the same size
    int N_GRID = r_grid.size();
    string col_datatype = global_col_datatypes[global_col_idx];
    CM_Hypers hypers;
    if (col_datatype == CONTINUOUS_DATATYPE) {
        int r_draw = draw_rand_i(N_GRID);
        hypers["r"] = r_grid[r_draw];
        int nu_draw = draw_rand_i(N_GRID);
        hypers["nu"] = nu_grid[nu_draw];
        int s_draw = draw_rand_i(N_GRID);
        hypers["s"] = s_grids[global_col_idx][s_draw];
        int mu_draw = draw_rand_i(N_GRID);
        hypers["mu"] = mu_grids[global_col_idx][mu_draw];
    } else if (col_datatype == CYCLIC_DATATYPE){
        int b_draw = draw_rand_i(N_GRID);
        hypers["b"] = vm_b_grid[b_draw];
        int a_draw = draw_rand_i(N_GRID);
        hypers["a"] = vm_a_grids[global_col_idx][b_draw];
        int kappa_draw = draw_rand_i(N_GRID);
        hypers["kappa"] = vm_kappa_grids[global_col_idx][kappa_draw];
    } else if (col_datatype == MULTINOMIAL_DATATYPE) {
        int dirichelt_alpha_draw = draw_rand_i(N_GRID);
        hypers["dirichlet_alpha"] = multinomial_alpha_grid[dirichelt_alpha_draw];
        hypers["K"] = global_col_multinomial_counts[global_col_idx];
    } else {
        assert(1 == 0);
    }
    return hypers;
}

double State::sample_column_crp_alpha() {
    int N_GRID = column_crp_alpha_grid.size();
    return column_crp_alpha_grid[draw_rand_i(N_GRID)];
}

double State::sample_row_crp_alpha() {
    int N_GRID = row_crp_alpha_grid.size();
    double row_crp_alpha = row_crp_alpha_grid[rng.nexti(N_GRID)];
    return row_crp_alpha;
}

vector<double> State::sample_row_crp_alphas(int N_views) {
    // needs rng, row_crp_alpha_grid
    vector<double> row_crp_alpha_v;
    for (int view_idx = 0; view_idx < N_views; view_idx++) {
        double row_crp_alpha = sample_row_crp_alpha();
        row_crp_alpha_v.push_back(row_crp_alpha);
    }
    return row_crp_alpha_v;
}

vector<vector<int> > State::generate_col_partition(vector<int>
        global_col_indices, string col_initialization) {
    vector<vector<int> > column_partition = draw_crp_init(global_col_indices,
                                            column_crp_alpha, rng,
                                            col_initialization);
    return column_partition;
}

vector<vector<vector<int> > > State::generate_row_partitions(
    vector<int> global_row_indices,
    vector<double> row_crp_alpha_v, string row_initialization) {
    vector<vector<vector<int> > > row_partition_v = draw_crp_init(global_row_indices,
            row_crp_alpha_v, rng, row_initialization);
    return row_partition_v;
}

void State::init_column_hypers(vector<int> global_col_indices) {
    vector<int>::iterator gci_it;
    for (gci_it = global_col_indices.begin(); gci_it != global_col_indices.end();
            gci_it++) {
        int global_col_idx = *gci_it;
        hypers_m[global_col_idx] = uniform_sample_hypers(global_col_idx);
        if (!in(hypers_m[global_col_idx], (string) "fixed")) {
            hypers_m[global_col_idx]["fixed"] = 0;
        }
    }
}

void State::init_views(const MatrixD& data,
                       vector<int> global_row_indices,
                       vector<int> global_col_indices,
                       vector<vector<int> > column_partition,
                       vector<vector<vector<int> > > row_partition_v,
                       vector<double> row_crp_alpha_v) {
    assert(column_partition.size() == row_partition_v.size());
    assert(column_partition.size() == row_crp_alpha_v.size());
    int num_views = column_partition.size();
    for (int view_idx = 0; view_idx < num_views; view_idx++) {
        vector<int> column_indices = column_partition[view_idx];
        vector<vector<int> > row_partition = row_partition_v[view_idx];
        double row_crp_alpha = row_crp_alpha_v[view_idx];
        const MatrixD data_subset = extract_columns(data, column_indices);
        View *p_v = new View(data_subset,
                             global_col_datatypes,
                             row_partition,
                             global_row_indices, column_indices,
                             hypers_m,
                             row_crp_alpha_grid,
                             multinomial_alpha_grid, r_grid, nu_grid,
                             vm_b_grid,
                             s_grids, mu_grids,
                             vm_a_grids, vm_kappa_grids,
                             row_crp_alpha,
                             draw_rand_i());
        views.insert(p_v);
        vector<int>::iterator ci_it;
        for (ci_it = column_indices.begin(); ci_it != column_indices.end(); ci_it++) {
            int column_index = *ci_it;
            view_lookup[column_index] = p_v;
        }
    }
}

std::ostream& operator<<(std::ostream& os, const State& s) {
    os << s.to_string() << endl;
    return os;
}

string State::to_string(string join_str, bool top_level) const {
    stringstream ss;
    if (!top_level) {
        int view_idx = 0;
        set<View*>::const_iterator it;
        ss << "========" << std::endl;
        for (it = views.begin(); it != views.end(); it++) {
            View v = **it;
            ss << "view idx: " << view_idx++ << endl;
            ss << v << endl;
            ss << "========" << std::endl;
        }
    }
    ss << "column_crp_alpha: " << column_crp_alpha;
    ss << "; column_crp_score: " << column_crp_score;
    ss << "; data_score: " << get_data_score();
    return ss.str();
}
