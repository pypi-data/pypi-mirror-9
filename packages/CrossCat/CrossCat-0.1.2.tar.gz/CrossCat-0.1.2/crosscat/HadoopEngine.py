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
#
import crosscat.utils.file_utils as fu
import crosscat.utils.general_utils as gu
import crosscat.utils.xnet_utils as xu
import crosscat.utils.hadoop_utils as hu
from crosscat.settings import Hadoop as hs


class HadoopEngine(object):
    """A class to dispatch jobs to a Hadoop cluster

    Requires that a binary, to be run by Hadoop streaming, already exists on the
    cluster.

    Requires specfication of write-able file locations where intermediate Hadoop
    output will be stored before being parsed and returned as X_L and X_D

    """

    def __init__(self, seed=0,
                 which_engine_binary=hs.default_engine_binary,
                 hdfs_dir=hs.default_hdfs_dir,
                 jobtracker_uri=hs.default_jobtracker_uri,
                 hdfs_uri=hs.default_hdfs_uri,
                 which_hadoop_jar=hs.default_hadoop_jar,
                 which_hadoop_binary=hs.default_hadoop_binary,
                 output_path=hs.default_output_path,
                 input_filename=hs.default_input_filename,
                 table_data_filename=hs.default_table_data_filename,
                 command_dict_filename=hs.default_command_dict_filename,
                 one_map_task_per_line=True,
                 ):
        xu.assert_vpn_is_connected()
        #
        self.which_hadoop_binary = which_hadoop_binary
        #
        self.seed_generator = gu.int_generator(seed)
        self.which_engine_binary = which_engine_binary
        self.hdfs_dir = hdfs_dir
        self.jobtracker_uri = jobtracker_uri
        self.hdfs_uri = hdfs_uri
        self.which_hadoop_jar = which_hadoop_jar
        self.output_path = output_path
        self.input_filename = input_filename
        self.table_data_filename = table_data_filename
        self.one_map_task_per_line = one_map_task_per_line
        self.command_dict_filename = command_dict_filename
        return

    def send_hadoop_command(self, n_tasks=1):
        hu.send_hadoop_command(
            self.hdfs_uri, self.hdfs_dir, self.jobtracker_uri,
            self.which_engine_binary, self.which_hadoop_binary, self.which_hadoop_jar,
            self.input_filename, self.table_data_filename,
            self.command_dict_filename, self.output_path,
            n_tasks, self.one_map_task_per_line)
        return

    def get_hadoop_results(self):
        was_successful = hu.get_hadoop_results(self.hdfs_uri, self.output_path, self.hdfs_dir)
        print 'was_successful: %s' % was_successful
        return was_successful

    def initialize(self, M_c, M_r, T, initialization='from_the_prior',
                   n_chains=1):
        """Sample a latent state from prior

        :param M_c: The column metadata
        :type M_c: dict
        :param M_r: The row metadata
        :type M_r: dict
        :param T: The data table in mapped representation (all floats, generated
                  by data_utils.read_data_objects)
        :type T: list of lists
        :returns: X_L, X_D -- the latent state

        """

        output_path = self.output_path
        input_filename = self.input_filename
        table_data_filename = self.table_data_filename
        intialize_args_dict_filename = self.command_dict_filename
        xu.assert_vpn_is_connected()
          #
        table_data = dict(M_c=M_c, M_r=M_r, T=T)
        initialize_args_dict = dict(command='initialize',
                                    initialization=initialization)
        xu.write_initialization_files(input_filename,
                                      table_data, table_data_filename,
                                      initialize_args_dict,
                                      intialize_args_dict_filename,
                                      n_chains)
        os.system('cp %s initialize_input' % input_filename)
        self.send_hadoop_command(n_tasks=n_chains)
        was_successful = self.get_hadoop_results()
        hadoop_output = None
        if was_successful:
            hu.copy_hadoop_output(output_path, 'initialize_output')
            X_L_list, X_D_list = hu.read_hadoop_output(output_path)
            hadoop_output = X_L_list, X_D_list
            return hadoop_output

    def analyze(self, M_c, T, X_L, X_D, kernel_list=(), n_steps=1, c=(), r=(),
                max_iterations=-1, max_time=-1, **kwargs):  
        """Evolve the latent state by running MCMC transition kernels

        :param M_c: The column metadata
        :type M_c: dict
        :param T: The data table in mapped representation (all floats, generated
                  by data_utils.read_data_objects)
        :type T: list of lists
        :param X_L: the latent variables associated with the latent state
        :type X_L: dict
        :param X_D: the particular cluster assignments of each row in each view
        :type X_D: list of lists
        :param kernel_list: names of the MCMC transition kernels to run
        :type kernel_list: list of strings
        :param n_steps: the number of times to run each MCMC transition kernel
        :type n_steps: int
        :param c: the (global) column indices to run MCMC transition kernels on
        :type c: list of ints
        :param r: the (global) row indices to run MCMC transition kernels on
        :type r: list of ints
        :param max_iterations: the maximum number of times ot run each MCMC
                               transition kernel. Applicable only if
                               max_time != -1.
        :type max_iterations: int
        :param max_time: the maximum amount of time (seconds) to run MCMC
                         transition kernels for before stopping to return
                         progress
        :type max_time: float
        :param kwargs: optional arguments to pass to hadoop_line_processor.jar.
                       Currently, presence of a 'chunk_size' kwarg causes
                       different behavior.
        :returns: X_L, X_D -- the evolved latent state
        
        """

        output_path = self.output_path
        input_filename = self.input_filename
        table_data_filename = self.table_data_filename
        analyze_args_dict_filename = self.command_dict_filename
        xu.assert_vpn_is_connected()
        #
        table_data = dict(M_c=M_c, T=T)
        analyze_args_dict = dict(command='analyze', kernel_list=kernel_list,
                                 n_steps=n_steps, c=c, r=r, max_time=max_time)
        # chunk_analyze is a special case of analyze
        if 'chunk_size' in kwargs:
          chunk_size = kwargs['chunk_size']
          chunk_filename_prefix = kwargs['chunk_filename_prefix']
          chunk_dest_dir = kwargs['chunk_dest_dir']
          analyze_args_dict['command'] = 'chunk_analyze'
          analyze_args_dict['chunk_size'] = chunk_size
          analyze_args_dict['chunk_filename_prefix'] = chunk_filename_prefix
          # WARNING: chunk_dest_dir MUST be writeable by hadoop user mapred
          analyze_args_dict['chunk_dest_dir'] = chunk_dest_dir
        if not su.get_is_multistate(X_L, X_D):
            X_L = [X_L]
            X_D = [X_D]
        #
        SEEDS = kwargs.get('SEEDS', None)
        xu.write_analyze_files(input_filename, X_L, X_D,
                               table_data, table_data_filename,
                               analyze_args_dict, analyze_args_dict_filename,
                               SEEDS)
        os.system('cp %s analyze_input' % input_filename)
        n_tasks = len(X_L)
        self.send_hadoop_command(n_tasks)
        was_successful = self.get_hadoop_results()
        hadoop_output = None
        if was_successful:
          hu.copy_hadoop_output(output_path, 'analyze_output')
          X_L_list, X_D_list = hu.read_hadoop_output(output_path)
          hadoop_output = X_L_list, X_D_list
        return hadoop_output

    def simple_predictive_sample(self, M_c, X_L, X_D, Y, Q, n=1):
        pass

    def impute(self, M_c, X_L, X_D, Y, Q, n):
        pass

    def impute_and_confidence(self, M_c, X_L, X_D, Y, Q, n):
        pass

        
if __name__ == '__main__':
    import argparse
    #
    import crosscat.utils.data_utils as du
    #
    parser = argparse.ArgumentParser()
    parser.add_argument('command', type=str)
    parser.add_argument('--base_uri', type=str, default=None)
    parser.add_argument('--hdfs_uri', type=str, default=hs.default_hdfs_uri)
    parser.add_argument('--jobtracker_uri', type=str,
                        default=hs.default_jobtracker_uri)
    parser.add_argument('--hdfs_dir', type=str, default=hs.default_hdfs_dir)
    parser.add_argument('-DEBUG', action='store_true')
    parser.add_argument('--which_engine_binary', type=str, default=hs.default_engine_binary)
    parser.add_argument('--which_hadoop_binary', type=str, default=hs.default_hadoop_binary)
    parser.add_argument('--which_hadoop_jar', type=str, default=hs.default_hadoop_jar)
    parser.add_argument('--n_chains', type=int, default=4)
    parser.add_argument('--n_steps', type=int, default=1)
    parser.add_argument('--chunk_size', type=int, default=1)
    parser.add_argument('--chunk_filename_prefix', type=str, default='chunk')
    parser.add_argument('--chunk_dest_dir', type=str, default='/user/bigdata/SSCI/chunk_dir')
    parser.add_argument('--max_time', type=float, default=-1)
    parser.add_argument('--table_filename', type=str, default='../www/data/dha_small.csv')
    parser.add_argument('--resume_filename', type=str, default=None)
    parser.add_argument('--pkl_filename', type=str, default=None)
    parser.add_argument('--cctypes_filename', type=str, default=None)
    #
    args = parser.parse_args()
    base_uri = args.base_uri
    hdfs_uri = args.hdfs_uri
    jobtracker_uri = args.jobtracker_uri
    hdfs_dir = args.hdfs_dir
    DEBUG = args.DEBUG
    which_engine_binary = args.which_engine_binary
    which_hadoop_binary = args.which_hadoop_binary
    which_hadoop_jar= args.which_hadoop_jar
    n_chains = args.n_chains
    n_steps = args.n_steps
    chunk_size = args.chunk_size
    chunk_filename_prefix = args.chunk_filename_prefix
    chunk_dest_dir = args.chunk_dest_dir
    max_time = args.max_time
    table_filename = args.table_filename
    resume_filename = args.resume_filename
    pkl_filename = args.pkl_filename
    #
    command = args.command
    # assert command in set(gu.get_method_names(HadoopEngine))
    #
    cctypes_filename = args.cctypes_filename
    cctypes = None
    if cctypes_filename is not None:
      cctypes = fu.unpickle(cctypes_filename)

    hdfs_uri, jobtracker_uri = hu.get_uris(base_uri, hdfs_uri, jobtracker_uri)
    T, M_r, M_c = du.read_model_data_from_csv(table_filename, gen_seed=0,
                                              cctypes=cctypes)
    he = HadoopEngine(which_engine_binary=which_engine_binary,
		      which_hadoop_binary=which_hadoop_binary,
		      which_hadoop_jar=which_hadoop_jar,
                      hdfs_dir=hdfs_dir, hdfs_uri=hdfs_uri,
                      jobtracker_uri=jobtracker_uri)
    
    X_L_list, X_D_list = None, None
    if command == 'initialize':
        hadoop_output = he.initialize(M_c, M_r, T,
                                      initialization='from_the_prior',
                                      n_chains=n_chains)
        if hadoop_output is not None:
            X_L_list, X_D_list = hadoop_output
    elif command == 'analyze':
        assert resume_filename is not None
        if fu.is_pkl(resume_filename):
          resume_dict = fu.unpickle(resume_filename)
        else:
          resume_dict = hu.read_hadoop_output_file(resume_filename)
        X_L_list = resume_dict['X_L_list']
        X_D_list = resume_dict['X_D_list']
        hadoop_output = he.analyze(M_c, T, X_L_list, X_D_list,
                                   n_steps=n_steps, max_time=max_time)
        if hadoop_output is not None:
            X_L_list, X_D_list = hadoop_output
    elif command == 'chunk_analyze':
        assert resume_filename is not None
        if fu.is_pkl(resume_filename):
          resume_dict = fu.unpickle(resume_filename)
          X_L_list = resume_dict['X_L_list']
          X_D_list = resume_dict['X_D_list']
        else:
          X_L_list, X_D_list = hu.read_hadoop_output(resume_filename)
        hadoop_output = he.analyze(M_c, T, X_L_list, X_D_list,
                                   n_steps=n_steps, max_time=max_time,
                                   chunk_size=chunk_size,
                                   chunk_filename_prefix=chunk_filename_prefix,
                                   chunk_dest_dir=chunk_dest_dir)
        if hadoop_output is not None:
            X_L_list, X_D_list = hadoop_output
    else:
        print 'Unknown command: %s' % command
        import sys
        sys.exit()
        
    if pkl_filename is not None:
      to_pkl_dict = dict(
            T=T,
            M_c=M_c,
            M_r=M_r,
            X_L_list=X_L_list,
            X_D_list=X_D_list,
            )
      fu.pickle(to_pkl_dict, filename=pkl_filename)
