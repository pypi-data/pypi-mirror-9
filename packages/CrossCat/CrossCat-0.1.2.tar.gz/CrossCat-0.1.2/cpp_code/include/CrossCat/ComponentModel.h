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
#ifndef GUARD_componentmodel_h
#define GUARD_componentmodel_h

#define _USE_CMATH_DEFINES
#include <cmath>
#include <iostream>
#include <sstream>
#include <map>
#include <string>
#include <vector>
#include "utils.h"
#include "constants.h"
#include <boost/random/student_t_distribution.hpp>
#include <boost/math/distributions/students_t.hpp>
#include <boost/math/special_functions/gamma.hpp>
#include <boost/random/mersenne_twister.hpp>

class ComponentModel {
public:
    virtual ~ComponentModel() {};
    //
    // getters
    CM_Hypers get_hypers() const;
    int get_count() const;
    std::map<std::string, double> get_suffstats() const;
    virtual std::map<std::string, double> _get_suffstats() const;
    virtual double get_draw(int random_seed) const;
    virtual double get_draw_constrained(int random_seed,
                                std::vector<double> constraints) const;
    //
    //
    // calculators
    virtual double calc_marginal_logp() const;
    virtual double calc_element_predictive_logp(double element) const;
    virtual double calc_element_predictive_logp_constrained(double element,
            std::vector<double> constraints) const;
    virtual std::vector<double> calc_hyper_conditionals(std::string which_hyper,
            std::vector<double> hyper_grid) const;
    //
    // mutators
    virtual double insert_element(double element);
    virtual double remove_element(double element);
    virtual double incorporate_hyper_update();
    //
    // helpers
    friend std::ostream& operator<<(std::ostream& os, const ComponentModel& cm);
    // make protected later
    CM_Hypers *p_hypers;
    std::string to_string(std::string join_str = "\n") const;
protected:
    int count;
    double log_Z_0;
    double score;
    //
    // helpers
    virtual void set_log_Z_0();
    virtual void init_suffstats();
private:
};

#endif // GUARD_componentmodel_h
