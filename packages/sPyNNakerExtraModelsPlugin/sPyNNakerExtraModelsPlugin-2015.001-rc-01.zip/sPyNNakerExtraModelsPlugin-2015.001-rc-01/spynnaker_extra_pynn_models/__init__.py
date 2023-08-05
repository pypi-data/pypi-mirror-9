from spynnaker_extra_pynn_models import model_binaries


def _init_module():
    import logging
    import os
    import spynnaker.pyNN

    # Register this path with SpyNNaker
    spynnaker.pyNN.register_binary_search_path(os.path.dirname(
        model_binaries.__file__))

_init_module()

from spynnaker_extra_pynn_models.neural_models.if_cond_exp_stoc \
    import IFConductanceExponentialStochasticPopulation as IF_cond_exp_stoc
from spynnaker_extra_pynn_models.neural_properties.synapse_dynamics\
    .dependences.recurrent_time_dependency\
    import RecurrentTimeDependency as RecurrentRule
