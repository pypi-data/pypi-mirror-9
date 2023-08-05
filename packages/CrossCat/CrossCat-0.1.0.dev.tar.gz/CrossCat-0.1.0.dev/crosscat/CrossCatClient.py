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
import inspect
#


class CrossCatClient(object):
    """ A client interface that gives a singular interface to all the different
    engines

    Depending on the client_type, dispatch to the appropriate engine constructor

    """

    def __init__(self, engine):
        """Initialize client with given engine

        Not to be called directly!

        """

        self.engine = engine
        return

    def __getattribute__(self, name):
        engine = object.__getattribute__(self, 'engine')
        attr = None
        if hasattr(engine, name):
            attr = getattr(engine, name)
        else:
            attr = object.__getattribute__(self, name)
        return attr

# Maybe this should be in CrossCatClient.__init__
def get_CrossCatClient(client_type, **kwargs):
    """Helper which instantiates the appropriate Engine and returns a Client

    """

    client = None
    if client_type == 'local':
        import crosscat.LocalEngine as LocalEngine
        le = LocalEngine.LocalEngine(**kwargs)
        client = CrossCatClient(le)
    elif client_type == 'hadoop':
        import crosscat.HadoopEngine as HadoopEngine
        he = HadoopEngine.HadoopEngine(**kwargs)
        client = CrossCatClient(he)
    elif client_type == 'jsonrpc':
        import crosscat.JSONRPCEngine as JSONRPCEngine
        je = JSONRPCEngine.JSONRPCEngine(**kwargs)
        client = CrossCatClient(je)
    elif client_type == 'multiprocessing':
        import crosscat.MultiprocessingEngine as MultiprocessingEngine
        me =  MultiprocessingEngine.MultiprocessingEngine(**kwargs)
        client = CrossCatClient(me)
    else:
        raise Exception('unknown client_type: %s' % client_type)
    return client


if __name__ == '__main__':
    import crosscat.utils.data_utils as du
    ccc = get_CrossCatClient('local', seed=0)
    #
    gen_seed = 0
    num_clusters = 4
    num_cols = 8
    num_rows = 16
    num_splits = 1
    max_mean = 10
    max_std = 0.1
    T, M_r, M_c = du.gen_factorial_data_objects(
        gen_seed, num_clusters,
        num_cols, num_rows, num_splits,
        max_mean=max_mean, max_std=max_std,
        )
    #
    X_L, X_D, = ccc.initialize(M_c, M_r, T)
    X_L_prime, X_D_prime = ccc.analyze(M_c, T, X_L, X_D)
    X_L_prime, X_D_prime = ccc.analyze(M_c, T, X_L_prime, X_D_prime)
    #
    ccc = get_CrossCatClient('jsonrpc', seed=0, URI='http://localhost:8007')
    X_L, X_D, = ccc.initialize(M_c, M_r, T)
    X_L_prime, X_D_prime = ccc.analyze(M_c, T, X_L, X_D)
    X_L_prime, X_D_prime = ccc.analyze(M_c, T, X_L_prime, X_D_prime)
    
