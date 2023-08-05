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
import subprocess
import os

def test_view():
    run_shell_command('test_view')

def test_view_speed():
    run_shell_command('test_view_speed')

def test_state():
    run_shell_command('test_state')

def run_shell_command(name):
    p = subprocess.Popen(['%s/%s' % (os.path.dirname(os.path.abspath(__file__)), name)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    retcode = p.wait()
    out = p.stdout.read()
    err = p.stderr.read()
    if len(err) > 0:
        fail(err)
