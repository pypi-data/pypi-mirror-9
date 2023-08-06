import math

from data_specification.enums.data_type import DataType

from spynnaker.pyNN.models.neural_properties.synapse_dynamics.abstract_rules.\
    abstract_time_dependency import AbstractTimeDependency
from spynnaker.pyNN.models.neural_properties.synapse_dynamics.\
    plastic_weight_control_synapse_row_io\
    import PlasticWeightControlSynapseRowIo
from spynnaker.pyNN.models.neural_properties.synapse_dynamics\
    import plasticity_helpers


class RecurrentTimeDependency(AbstractTimeDependency):
    def __init__(self, accumulator_depression=-6, accumulator_potentiation=6,
                 mean_pre_window=35.0, mean_post_window=35.0, dual_fsm=False):
        AbstractTimeDependency.__init__(self)

        self.accumulator_depression_plus_one = accumulator_depression + 1
        self.accumulator_potentiation_minus_one = accumulator_potentiation - 1
        self.mean_pre_window = mean_pre_window
        self.mean_post_window = mean_post_window
        self.dual_fsm = dual_fsm

    def __eq__(self, other):
        if (other is None) or (not isinstance(other, RecurrentTimeDependency)):
            return False
        return ((self.accumulator_depression_plus_one
                 == other.accumulator_depression_plus_one)
                and (self.accumulator_potentiation_minus_one
                     == other.accumulator_potentiation_minus_one)
                and (self.mean_pre_window == other.mean_pre_window)
                and (self.mean_post_window == other.mean_post_window))

    def create_synapse_row_io(self, synaptic_row_header_words,
                              dendritic_delay_fraction):
        return PlasticWeightControlSynapseRowIo(
            synaptic_row_header_words, dendritic_delay_fraction, False)

    def get_params_size_bytes(self):
        # 2 * 32-bit parameters
        # 2 * LUTS with STDP_FIXED_POINT_ONE * 16-bit entries
        return (4 * 2) + (2 * (2 * plasticity_helpers.STDP_FIXED_POINT_ONE))

    def is_time_dependance_rule_part(self):
        return True

    def write_plastic_params(self, spec, machineTimeStep, weight_scales,
                             global_weight_scale):
        # Write parameters
        spec.write_value(data=self.accumulator_depression_plus_one,
                         data_type=DataType.INT32)
        spec.write_value(data=self.accumulator_potentiation_minus_one,
                         data_type=DataType.INT32)

        # Convert mean times into machine timesteps
        mean_pre_timesteps = (float(self.mean_pre_window)
                              * (1000.0 / float(machineTimeStep)))
        mean_post_timesteps = (float(self.mean_post_window)
                               * (1000.0 / float(machineTimeStep)))

        # Write lookup tables
        self._write_exp_dist_lut(spec, mean_pre_timesteps)
        self._write_exp_dist_lut(spec, mean_post_timesteps)

    @property
    def num_terms(self):
        return 1

    @property
    def vertex_executable_suffix(self):
        return "recurrent_dual_fsm" if self.dual_fsm else "recurrent_pre_stochastic"

    @property
    def pre_trace_size_bytes(self):
        # When using the seperate FSMs, pre-trace contains window length, otherwise it's in the synapse
        return 2 if self.dual_fsm else 0

    def _write_exp_dist_lut(self, spec, mean):
        for x in range(plasticity_helpers.STDP_FIXED_POINT_ONE):
            # Calculate inverse CDF
            x_float = float(x) / float(plasticity_helpers.STDP_FIXED_POINT_ONE)
            p_float = math.log(1.0 - x_float) * -mean

            p = round(p_float)
            spec.write_value(data=p, data_type=DataType.UINT16)
