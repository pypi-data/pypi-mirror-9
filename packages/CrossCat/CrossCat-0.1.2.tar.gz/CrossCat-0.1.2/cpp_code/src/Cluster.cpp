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
#include <stdlib.h>
#include "Cluster.h"

using namespace std;

Cluster::Cluster(vector<CM_Hypers*>& hypers_v) {
    init_columns(hypers_v);
}

Cluster::Cluster() {
    vector<CM_Hypers*> hypers_v;
    init_columns(hypers_v);
}

void Cluster::delete_component_models(bool check_empty) {
    if (check_empty) {
        assert(row_indices.size() == 0);
    }
    while (p_model_v.size() != 0) {
        ComponentModel *p_cm = p_model_v.back();
        p_model_v.pop_back();
        delete p_cm;
    }
}

int Cluster::get_num_cols() const {
    return p_model_v.size();
}

int Cluster::get_count() const {
    return row_indices.size();
}

double Cluster::get_marginal_logp() const {
    return score;
}

map<string, double> Cluster::get_suffstats_i(int idx) const {
    return p_model_v[idx]->get_suffstats();
}

CM_Hypers Cluster::get_hypers_i(int idx) const {
    return p_model_v[idx]->get_hypers();
}

set<int> Cluster::get_row_indices_set() const {
    return row_indices;
}

vector<int> Cluster::get_row_indices_vector() const {
    return set_to_vector(row_indices);
}

vector<double> Cluster::get_draw(int random_seed) const {
    RandomNumberGenerator rng(random_seed);
    std::vector<double> draws;
    std::vector<ComponentModel*>::const_iterator it;
    for(it=p_model_v.begin(); it!=p_model_v.end(); it++) {
        int randi = rng.nexti(MAX_INT);
        double draw = (**it).get_draw(randi);
        draws.push_back(draw);
    }
    return draws;
}

std::vector<double> Cluster::calc_marginal_logps() const {
    std::vector<double> logps;
    std::vector<ComponentModel*>::const_iterator it;
    for (it = p_model_v.begin(); it != p_model_v.end(); it++) {
        double logp = (**it).calc_marginal_logp();
        logps.push_back(logp);
    }
    return logps;
}

double Cluster::calc_sum_marginal_logps() const {
    std::vector<double> logp_map = calc_marginal_logps();
    double sum_logps = std::accumulate(logp_map.begin(), logp_map.end(), 0.);
    return sum_logps;
}

double Cluster::calc_row_predictive_logp(vector<double> values) const {
    double sum_logps = 0;
    for (unsigned int col_idx = 0; col_idx < values.size(); col_idx++) {
        double el = values[col_idx];
        sum_logps += p_model_v[col_idx]->calc_element_predictive_logp(el);
    }
    return sum_logps;
}

vector<double> Cluster::calc_hyper_conditionals(int which_col,
        string which_hyper,
        vector<double> hyper_grid) const {
    ComponentModel *cm = p_model_v[which_col];
    vector<double> hyper_conditionals = cm->calc_hyper_conditionals(which_hyper,
                                        hyper_grid);
    return hyper_conditionals;
}

double Cluster::calc_column_predictive_logp(vector<double> column_data,
        string col_datatype,
        vector<int> data_global_row_indices,
        CM_Hypers hypers) {
    // FIXME: global_to_data must be used if not all rows are present
    // map<int, int> global_to_data = construct_lookup_map(data_global_row_indices);
    ComponentModel prevent_warning;
    ComponentModel *p_cm = &prevent_warning;
    if (col_datatype == CONTINUOUS_DATATYPE) {
        p_cm = new ContinuousComponentModel(hypers);
    } else if (col_datatype == CYCLIC_DATATYPE) {
        p_cm = new CyclicComponentModel(hypers);
    } else if (col_datatype == MULTINOMIAL_DATATYPE) {
        p_cm = new MultinomialComponentModel(hypers);
    } else {
        cout << "Cluster::calc_column_predictive_logp: col_datatype=" << col_datatype
             << endl;
        assert(1 == 0);
        exit(EXIT_FAILURE);
    }
    set<int>::iterator it;
    for (it = row_indices.begin(); it != row_indices.end(); it++) {
        int global_row_idx = *it;
        // FIXME: global_to_data must be used if not all rows are present
        // int data_idx = global_to_data[global_row_idx];
        int data_idx = global_row_idx;
        double value = column_data[data_idx];
        p_cm->insert_element(value);
    }
    double score_delta = p_cm->calc_marginal_logp();
    delete p_cm;
    return score_delta;
}

double Cluster::insert_row(vector<double> values, int row_idx) {
    double sum_score_deltas = 0;
    // track row indices
    pair<set<int>::iterator, bool> set_pair = \
            row_indices.insert(row_idx);
    if (!set_pair.second) {
        cout << "Cluster::insert_row: !set_pair.second" << endl;
        assert(set_pair.second);
        exit(EXIT_FAILURE);
    }
    // track score
    for (unsigned int col_idx = 0; col_idx < values.size(); col_idx++) {
        sum_score_deltas += p_model_v[col_idx]->insert_element(values[col_idx]);
    }
    score += sum_score_deltas;
    return sum_score_deltas;
}

double Cluster::remove_row(vector<double> values, int row_idx) {
    double sum_score_deltas = 0;
    // track row indices
    unsigned int num_removed = row_indices.erase(row_idx);
    if (num_removed == 0) {
        cout << "Cluster::remove_row: num_removed==0" << endl;
        assert(num_removed != 0);
        exit(EXIT_FAILURE);
    }
    // track score
    for (unsigned int col_idx = 0; col_idx < values.size(); col_idx++) {
        double value_to_remove = values[col_idx];
        ComponentModel *p_cm = p_model_v[col_idx];
        sum_score_deltas += p_cm->remove_element(value_to_remove);
    }
    score += sum_score_deltas;
    return sum_score_deltas;
}

double Cluster::remove_col(int col_idx) {
    double score_delta = p_model_v[col_idx]->calc_marginal_logp();
    // FIXME: make sure destruction proper
    ComponentModel *p_cm = p_model_v[col_idx];
    p_model_v.erase(p_model_v.begin() + col_idx);
    delete p_cm;
    score -= score_delta;
    return score_delta;
}

double Cluster::insert_col(vector<double> data,
                           string col_datatype,
                           vector<int> data_global_row_indices,
                           CM_Hypers& hypers) {
    // FIXME: global_to_data must be used if not all rows are present
    // map<int, int> global_to_data = construct_lookup_map(data_global_row_indices);
    ComponentModel prevent_warning;
    ComponentModel *p_cm = &prevent_warning;
    if (col_datatype == CONTINUOUS_DATATYPE) {
        p_cm = new ContinuousComponentModel(hypers);
    } else if (col_datatype == MULTINOMIAL_DATATYPE) {
        p_cm = new MultinomialComponentModel(hypers);
    } else if (col_datatype == CYCLIC_DATATYPE) {
        p_cm = new CyclicComponentModel(hypers);
    } else {
        cout << "ERROR: Cluster::insert_col: col_datatype=" << col_datatype << endl;
        assert(1 == 0);
        exit(EXIT_FAILURE);
    }
    set<int>::iterator it;
    for (it = row_indices.begin(); it != row_indices.end(); it++) {
        int global_row_idx = *it;
        // FIXME: global_to_data must be used if not all rows are present
        // int data_idx = global_to_data[global_row_idx]    int data_idx = global_to_data[global_row_idx];
        int data_idx = global_row_idx;
        double value = data[data_idx];
        p_cm->insert_element(value);
    }
    double score_delta = p_cm->calc_marginal_logp();
    p_model_v.push_back(p_cm);
    score += score_delta;
    //
    return score_delta;
}

double Cluster::incorporate_hyper_update(int which_col) {
    double score_delta = p_model_v[which_col]->incorporate_hyper_update();
    score += score_delta;
    return score_delta;
}

std::ostream& operator<<(std::ostream& os, const Cluster& c) {
    os << c.to_string() << endl;
    return os;
}

string Cluster::to_string(string join_str, bool top_level) const {
    stringstream ss;
    if (!top_level) {
        ss << "========" << std::endl;
        ss <<  "row_indices:: " << row_indices;
        for (int col_idx = 0; col_idx < get_num_cols(); col_idx++) {
            ss << join_str << "column idx: " << col_idx << " :: ";
            ss << *(p_model_v[col_idx]);
        }
        ss << "========" << std::endl;
    }
    ss << "cluster marginal logp: " << get_marginal_logp() << std::endl;
    return ss.str();
}

void Cluster::init_columns(vector<CM_Hypers*>& hypers_v) {
    score = 0;
    vector<CM_Hypers*>::iterator it;
    for (it = hypers_v.begin(); it != hypers_v.end(); it++) {
        CM_Hypers& hypers = **it;
        ComponentModel *p_cm;
        if (in(hypers, continuous_key)) {
            // FIXME: should be passed col_datatypes here
            //         and instantiate correct type?
            p_cm = new ContinuousComponentModel(hypers);
            p_model_v.push_back(p_cm);
        } else if (in(hypers, multinomial_key)){
            p_cm = new MultinomialComponentModel(hypers);
            p_model_v.push_back(p_cm);
        } else if (in(hypers, cyclic_key)) {
            p_cm = new CyclicComponentModel(hypers);
            p_model_v.push_back(p_cm);
        } else {
            cout << "Cluster::init_columns: hypers=" << hypers << endl;
            assert(1 == 0);
            exit(EXIT_FAILURE);
        }
        int col_idx = p_model_v.size() - 1;
        score += p_model_v[col_idx]->calc_marginal_logp();
    }
}
