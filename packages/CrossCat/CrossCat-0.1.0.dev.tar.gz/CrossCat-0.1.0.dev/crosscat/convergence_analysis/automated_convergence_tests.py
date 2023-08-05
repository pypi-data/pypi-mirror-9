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
import os
import csv
import argparse
import tempfile
import time
import itertools
from collections import namedtuple
#
import numpy
#
import crosscat.utils.data_utils as du
import crosscat.utils.hadoop_utils as hu
import crosscat.utils.file_utils as fu
import crosscat.utils.xnet_utils as xu
import crosscat.LocalEngine as LE
import crosscat.HadoopEngine as HE
import crosscat.cython_code.State as State
import crosscat.convergence_analysis.parse_convergence_results as parse_cr
import crosscat.convergence_analysis.plot_convergence_results as plot_cr


def generate_hadoop_dicts(convergence_run_parameters, args_dict):
    dict_to_write = dict(convergence_run_parameters)
    dict_to_write.update(args_dict)
    yield dict_to_write

def write_hadoop_input(input_filename, convergence_run_parameters, n_steps, block_size, SEED):
    # prep settings dictionary
    convergence_analyze_args_dict = xu.default_analyze_args_dict
    convergence_analyze_args_dict['command'] = 'convergence_analyze'
    convergence_analyze_args_dict['SEED'] = SEED
    convergence_analyze_args_dict['n_steps'] = n_steps
    convergence_analyze_args_dict['block_size'] = block_size
    #
    n_tasks = 0
    with open(input_filename, 'a') as out_fh:
        dict_generator = generate_hadoop_dicts(convergence_run_parameters, convergence_analyze_args_dict)
        for dict_to_write in dict_generator:
            xu.write_hadoop_line(out_fh, key=dict_to_write['SEED'], dict_to_write=dict_to_write)
            n_tasks += 1
    return n_tasks

if __name__ == '__main__':
    default_num_rows_list = [200, 400, 1000]
    default_num_cols_list = [8, 16, 32]
    default_num_clusters_list = [5,10]
    default_num_splits_list = [2, 4]
    default_max_mean_list = [0.5, 1, 2]
    #
    parser = argparse.ArgumentParser()
    parser.add_argument('--gen_seed', type=int, default=0)
    parser.add_argument('--n_steps', type=int, default=500)
    parser.add_argument('--num_chains', type=int, default=50)
    parser.add_argument('--block_size', type=int, default=20)
    parser.add_argument('-do_local', action='store_true')
    parser.add_argument('--which_engine_binary', type=str,
                        default=HE.default_engine_binary)
    parser.add_argument('-do_remote', action='store_true')
    parser.add_argument('-do_plot', action='store_true')
    parser.add_argument('--num_rows_list', type=int, nargs='*',
            default=default_num_rows_list)
    parser.add_argument('--num_cols_list', type=int, nargs='*',
            default=default_num_cols_list)
    parser.add_argument('--num_clusters_list', type=int, nargs='*',
            default=default_num_clusters_list)
    parser.add_argument('--num_splits_list', type=int, nargs='*',
            default=default_num_splits_list)
    parser.add_argument('--max_mean_list', type=float, nargs='*',
            default=default_max_mean_list)
    #
    args = parser.parse_args()
    gen_seed = args.gen_seed
    n_steps = args.n_steps
    do_local = args.do_local
    num_chains = args.num_chains
    do_remote = args.do_remote
    do_plot = args.do_plot
    block_size = args.block_size
    num_rows_list = args.num_rows_list
    num_cols_list = args.num_cols_list
    num_clusters_list = args.num_clusters_list
    num_splits_list = args.num_splits_list
    max_mean_list = args.max_mean_list
    which_engine_binary = args.which_engine_binary
    #
    print 'using num_rows_list: %s' % num_rows_list
    print 'using num_cols_list: %s' % num_cols_list
    print 'using num_clusters_list: %s' % num_clusters_list
    print 'using num_splits_list: %s' % num_splits_list
    print 'using max_mean_list: %s' % max_mean_list
    print 'using engine_binary: %s' % which_engine_binary
    time.sleep(2)


    script_filename = 'hadoop_line_processor.py'
    # some hadoop processing related settings
    dirname = 'convergence_analysis'
    fu.ensure_dir(dirname)
    temp_dir = tempfile.mkdtemp(prefix='convergence_analysis_',
                                dir=dirname)
    print 'using dir: %s' % temp_dir
    #
    table_data_filename = os.path.join(temp_dir, 'table_data.pkl.gz')
    input_filename = os.path.join(temp_dir, 'hadoop_input')
    output_filename = os.path.join(temp_dir, 'hadoop_output')
    output_path = os.path.join(temp_dir, 'output')  
    parsed_out_file = os.path.join(temp_dir, 'parsed_convergence_output.csv')


    parameter_list = [num_rows_list, num_cols_list, num_clusters_list, num_splits_list]

    n_tasks = 0
    gen_seed = -1
    # Iterate over the parameter values and write each run as a line in the hadoop_input file
    take_product_of = [num_rows_list, num_cols_list, num_clusters_list, num_splits_list, max_mean_list]
    for num_rows, num_cols, num_clusters, num_splits, max_mean in itertools.product(*take_product_of):
        if numpy.mod(num_rows, num_clusters) == 0 and numpy.mod(num_cols, num_splits) == 0:
          gen_seed = gen_seed + 1
          for chainindx in range(num_chains):
              convergence_run_parameters = dict(num_rows=num_rows, num_cols=num_cols,
                      num_views=num_splits, num_clusters=num_clusters, max_mean=max_mean,
                      n_test=100,
                      init_seed=chainindx)
              n_tasks += write_hadoop_input(input_filename,
                      convergence_run_parameters,  n_steps, block_size,
                      SEED=gen_seed)

    # Create a dummy table data file
    table_data=dict(T=[],M_c=[],X_L=[],X_D=[])
    fu.pickle(table_data, table_data_filename)

    if do_local:
        xu.run_script_local(input_filename, script_filename, output_filename, table_data_filename)
        print 'Local Engine for automated convergence runs has not been completely implemented/tested'
    elif do_remote:
        hadoop_engine = HE.HadoopEngine(which_engine_binary=which_engine_binary,
                output_path=output_path,
                input_filename=input_filename,
                table_data_filename=table_data_filename)
        xu.write_support_files(table_data, hadoop_engine.table_data_filename,
                              dict(command='convergence_analyze'), hadoop_engine.command_dict_filename)
        hadoop_engine.send_hadoop_command(n_tasks=n_tasks)
        was_successful = hadoop_engine.get_hadoop_results()
        if was_successful:
            hu.copy_hadoop_output(hadoop_engine.output_path, output_filename)
            parse_cr.parse_to_csv(output_filename, parsed_out_file)
        else:
            print 'remote hadoop job NOT successful'
    else:
        # print what the command would be
        hadoop_engine = HE.HadoopEngine(which_engine_binary=which_engine_binary,
                output_path=output_path,
                input_filename=input_filename,
                table_data_filename=table_data_filename)
        cmd_str = hu.create_hadoop_cmd_str(
                hadoop_engine.hdfs_uri, hadoop_engine.hdfs_dir, hadoop_engine.jobtracker_uri,
                hadoop_engine.which_engine_binary, hadoop_engine.which_hadoop_binary,
                hadoop_engine.which_hadoop_jar,
                hadoop_engine.input_filename, hadoop_engine.table_data_filename,
                hadoop_engine.command_dict_filename, hadoop_engine.output_path,
                n_tasks, hadoop_engine.one_map_task_per_line)
        print cmd_str

    if do_plot and (do_local or do_remote):
      convergence_metrics_dict = plot_cr.parse_convergence_metrics_csv(parsed_out_file)
      for run_key, convergence_metrics in convergence_metrics_dict.iteritems():
        save_filename = str(run_key) + '.png'
        fh = plot_cr.plot_convergence_metrics(convergence_metrics,
            title_append=str(run_key), save_filename=save_filename)
            
