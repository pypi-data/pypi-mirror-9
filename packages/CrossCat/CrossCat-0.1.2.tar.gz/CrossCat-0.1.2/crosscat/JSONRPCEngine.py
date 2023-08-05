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
from functools import partial
#
import crosscat.EngineTemplate as EngineTemplate
import crosscat.utils.data_utils as du
import crosscat.utils.api_utils as au
import crosscat.utils.general_utils as gu


method_name_to_args = gu.get_method_name_to_args(EngineTemplate.EngineTemplate)
method_names_set = set(gu.get_method_names(EngineTemplate.EngineTemplate))


class JSONRPCEngine(EngineTemplate.EngineTemplate):
    """An 'adapter' for sending commands to an Engine resident on a remote machine.

    JSONRPCEngine supports all methods that the remote engine does.  The remote engine must be listening at the URI specified in the constructor.  Commands are sent via JSONRPC-2.0.

    """

    def __init__(self, seed=None, URI=None):
        super(JSONRPCEngine, self).__init__(seed=seed)
        self.URI = URI
        return

    def dispatch(self, method_name, *args, **kwargs):
        args_names = method_name_to_args[method_name]
        args_dict = dict(zip(args_names, args))
        kwargs.update(args_dict)
        out = au.call(method_name, kwargs, self.URI)
        if isinstance(out, tuple):
            out, id = out
        return out

    def __getattribute__(self, name):
        attr = None
        if name in method_names_set:
            partial_dispatch = partial(self.dispatch, name)
            attr = partial_dispatch
        else:
            attr = object.__getattribute__(self, name)
        return attr


if __name__ == '__main__':
    je = JSONRPCEngine(seed=10, URI='http://localhost:8007')
    #
    gen_seed = 0
    num_clusters = 4
    num_cols = 32
    num_rows = 400
    num_splits = 1
    max_mean = 10
    max_std = 0.1
    T, M_r, M_c = du.gen_factorial_data_objects(
        gen_seed, num_clusters,
        num_cols, num_rows, num_splits,
        max_mean=max_mean, max_std=max_std,
        )
    #
    X_L, X_D, = je.initialize(M_c, M_r, T)
    X_L_prime, X_D_prime = je.analyze(M_c, T, X_L, X_D)
    X_L_prime, X_D_prime = je.analyze(M_c, T, X_L_prime, X_D_prime)
