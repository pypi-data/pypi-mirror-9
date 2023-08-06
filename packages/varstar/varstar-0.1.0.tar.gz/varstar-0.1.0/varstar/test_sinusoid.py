import pytest
import numpy as np
import sinusoid
from copy import deepcopy


class TestSinusoid(object):

    def setup_class(self):
        self.freq = 2.1  # there is no logic to this value
        self.ampl = 1.4
        self.phase = np.pi / 3

    def value(self, x):
        return self.ampl * np.sin(2 * np.pi * self.freq * x + self.phase)

    def test_call(self):
        sinu = sinusoid.Sinusoid(self.freq, self.ampl, self.phase)
        x = np.linspace(-2/self.freq, 3*self.freq, num=1000)
        print self.freq
        assert ((sinu(x) - self.value(x)) == 0).all()

    def teardown_class(self):
        pass


class TestSinusoidalModel(object):

# Add setup of a single mode
# Add test of value of single mode -- can't, no way to assign
# amplitude/phase except by fitting.
# Commit this package of changes.

    def setup_class(self):
        self.f1 = 2.1
        self.ampl = 1.4
        self.phase = 0
        self.double_mode = {'freq': [1.2, 2.3],
                            'modes': [[1, 0], [0, 1], [1, 1]]}
        self.double_model = sinusoid.SinusoidModel(frequencies=self.double_mode['freq'],
                                                   modes=self.double_mode['modes'])
        self.expected_modes = tuple([tuple(mode) for mode in self.double_mode['modes']])
# Then...
#   + Change all things that are currently lists to immutable tuples
#   + Add tests for immutability of frequencies, modes
#   + Add method for adding frequency that returns new instance.
#   + Add method for adding new mode that returns new instance.
#   + Add method for calculating "mode" frequencies.

    def test_frequencies_are_immutable(self):
        assert self.double_model.frequencies == tuple(self.double_mode['freq'])

    def test_modes_are_immutable(self):
        ## make sure it is impossible to change mode defitions.
        model = sinusoid.SinusoidModel(frequencies=self.double_mode['freq'],
                                       modes=self.double_mode['modes'])

        assert (model.modes == self.expected_modes)

    def test_number_modes_matches_frequencies(self):
        with pytest.raises(ValueError):
            bad_model = sinusoid.SinusoidModel(frequencies=self.double_mode['freq'],
                                               modes=[[1, 0, 0]])

    def test_add_frequency_to_empty_model(self):
        empty_model = sinusoid.SinusoidModel()
        empty_model.add_frequency(self.double_mode['freq'][0],
                                  self.double_mode['freq'][1])
        assert empty_model.frequencies == tuple(self.double_mode['freq'])

    def test_add_single_mode_to_empty_model(self):
        empty_model = sinusoid.SinusoidModel()
        empty_model.add_frequency(self.double_mode['freq'][0],
                                  self.double_mode['freq'][1])
        first_mode = self.double_mode['modes'][0]
        empty_model.add_mode(first_mode[0], first_mode[1])
        assert (empty_model.modes[0] == tuple(first_mode))

    def test_add_several_modes_to_empty_model(self):
        empty_model = sinusoid.SinusoidModel()
        empty_model.add_frequency(self.double_mode['freq'][0],
                                  self.double_mode['freq'][1])
        modes = self.double_mode['modes']
        empty_model.add_mode(modes[0], modes[1], modes[2])
        print empty_model.modes
        assert (empty_model.modes == self.expected_modes)

    def test_adding_frequency_extends_modes(self):
        model = deepcopy(self.double_model)
        model.add_frequency(1.8)
        for new_mode, old_mode in zip(model.modes, self.double_model.modes):
            correct_mode = list(old_mode)
            correct_mode.append(0)
            assert (new_mode == tuple(correct_mode))

    def test_supress_extending_modes_when_adding_freq(self):
        model = deepcopy(self.double_model)
        model.add_frequency(1.8, extend_modes=False)
        assert (model.modes == ())

    def test_adding_several_frequencies_extends_modes(self):
        model = deepcopy(self.double_model)
        model.add_frequency(1.8, 4.5)
        for new_mode, old_mode in zip(model.modes, self.double_model.modes):
            correct_mode = list(old_mode)
            correct_mode.extend([0, 0])
            assert (new_mode == tuple(correct_mode))

    def test_decreasing_number_of_freqs_should_fail(self):
        model = deepcopy(self.double_model)
        with pytest.raises(ValueError):
            model.frequencies = [1.2]

    def test_increasing_frequencies_in_setter_fails(self):
        model = deepcopy(self.double_model)
        with pytest.raises(ValueError):
            model.frequencies = [1, 2, 3]

    def test_changing_frequency_values(self):
        model = deepcopy(self.double_model)
        new_freqs = (3, 4)
        model.frequencies = new_freqs
        assert (model.frequencies == new_freqs)

    def test_adding_duplicate_frequency_fails(self):
        model = deepcopy(self.double_model)
        with pytest.raises(ValueError):
            model.add_frequency(model.frequencies[0])

    def test_setting_frequencies_with_duplicates_fails(self):
        model = sinusoid.SinusoidModel()
        with pytest.raises(ValueError):
            model.frequencies = [1, 2, 1]
        model.frequencies = [1, 2]
        with pytest.raises(ValueError):
            model.frequencies = [1, 3]

    def test_adding_duplicate_mode_fails(self):
        model = deepcopy(self.double_model)
        with pytest.raises(ValueError):
            model.add_mode(model.modes[0])
