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
import sys
import csv
#
import crosscat.utils.xnet_utils as xu


def get_line_label(parsed_line):
    return int(parsed_line[0])
def extract_variables(parsed_line, variable_names_to_extract):
    variable_dict = parsed_line[1]
    variables = [
            variable_dict[variable_name]
            for variable_name in variable_names_to_extract
            ]
    return variables

def parsed_line_to_output_row(parsed_line, variable_names_to_extract,
        get_line_label=get_line_label):
    line_label = get_line_label(parsed_line)
    variables = extract_variables(parsed_line, variable_names_to_extract)
    ret_list = [line_label] + variables
    return ret_list

def parse_to_csv(in_filename, out_filename='parsed_convergence.csv'):
    variable_names_to_extract = ['num_rows', 'num_cols', 'num_clusters', 'num_views',
            'max_mean', 'n_steps', 'block_size','column_ari_list',
            'generative_mean_test_log_likelihood','mean_test_ll_list',
            'elapsed_seconds_list']
    header = ['experiment'] + variable_names_to_extract
    with open(in_filename) as in_fh:
      with open(out_filename,'w') as out_fh:
        csvwriter = csv.writer(out_fh)
        csvwriter.writerow(header)
        for line in in_fh:
            try:
              parsed_line = xu.parse_hadoop_line(line)
              output_row = parsed_line_to_output_row(parsed_line,
                      variable_names_to_extract=variable_names_to_extract)
              csvwriter.writerow(output_row)
            except Exception, e:
              sys.stderr.write(line + '\n' + str(e) + '\n')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('in_filename', type=str)
    parser.add_argument('--out_filename', type=str,
            default='parsed_convergence.csv')
    args = parser.parse_args()
    in_filename = args.in_filename
    out_filename = args.out_filename
    parse_to_csv(in_filename, out_filename)
