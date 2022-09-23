import numpy as np

# from config_my_pulses_FB import config
from qm.qua import wait_for_trigger, reset_phase, program, update_frequency, for_, stream_processing, declare, declare_stream, wait, measure, play, save, fixed, demod, ramp, amp, if_, elif_, else_, align, ramp_to_zero, switch_, case_
from qm.QuantumMachinesManager import QuantumMachinesManager
from qualang_tools.bakery.bakery import baking


class OPX_measurerer():

    def __init__(self,
                 config,
                 qmm=None,
                 dividers={'gate_36': 8.18*1e-3, 'gate_29': 8.27*1e-3},
                 n_repetitions = 10):

        if qmm is None:
            self.qmm = QuantumMachinesManager(host='192.168.15.128', port=80)
        else:
            self.qmm = qmm

        self.dividers = dividers
        self.config = config
        self.CW_amp = 0.25

        

        self.overhauser_program = self._build_overhauser_program(n_repetitions)
        self.overhauser_id = self._compile_overhauser_program_and_open_qm(self.overhauser_program)

        self.meas_I_id = self._compile_measurement_I()

    def measure_I(self,):
        job = self._start_compiled_program(self.meas_I_id)
        results_I = self._get_I(job)
        return results_I

    def measure_overhauser_dataset(self, return_values = 'all'):
        if return_values == 'all':
            job = self._start_compiled_program(self.overhauser_id)
            all_data = self._get_overhauser_dataset(job)
            return all_data

        elif return_values == 'I':
            job = self._start_compiled_program(self.overhauser_id)
            I_handle = job.result_handles.get('I_2')
            I_handle.wait_for_all_values()
            results_I = I_handle.fetch_all(flat_struct=True)
            return results_I
        else:
            raise Exception(f'"return_values": {return_values} is not valid, try "all" or "I"')

    def _start_compiled_program(self, compiled_id):
        p_job = self.qm.queue.add_compiled(compiled_id)
        return p_job.wait_for_execution()

    def _get_I(self, job):
        I_handle = job.result_handles.get('I')
        I_handle.wait_for_all_values()
        results_I = I_handle.fetch_all()
        return results_I

    def _get_overhauser_dataset(self, job):
        # if only interested in I, we can maybe save some time here
        job.result_handles.wait_for_all_values()
        all_data = {name: data.fetch_all(flat_struct=True) for name, data in job.result_handles._all_results.items()}
        return all_data

    def _compile_overhauser_program_and_open_qm(self, program):
        self.qm = self.qmm.open_qm(self.config, close_other_machines=True)
        return self.qm.compile(program)

    def _compile_measurement_I(self, readout_pulse='readout_pulse_3us', quantum_element='bottom_right_DQD_readout'):
        with program() as measurement_program:
            I_val = declare(fixed)
            I_stream = declare_stream()

            measure(readout_pulse, quantum_element, None, demod.full('cos', I_val))
            save(I_val, I_stream)

            with stream_processing():
                I_stream.save('I')

        compiled_id = self.qm.compile(measurement_program)
        return compiled_id

    def _build_overhauser_program(self, n_repetitions):
        det_min_amp = -35  # mV negative in (1,1)
        angle_degree = 130.51  # degrees, 0 degree aligned with BNC29 in positive volt.direction

        initialize = {'gate_36': 0,  # in mV
                      'gate_29': 1}
        measurement_point = {'gate_36': 0,  # in mV
                             'gate_29': 1}

        det_min = {'gate_36': -det_min_amp*np.sin(angle_degree*np.pi/180),  # in mV
                   'gate_29': -det_min_amp*np.cos(angle_degree*np.pi/180)}

        duration_init_pulse_in_clk_cycles = 1000
        duration_wait_after_init_in_clk_cycles = 1000
        time_at_measurement_point_per_RF_burst_in_clk_cycles = 1375
        total_time_at_measurement_point_in_clk_cycles = duration_wait_after_init_in_clk_cycles + 2*time_at_measurement_point_per_RF_burst_in_clk_cycles
        corrD_duration_in_clk_cycles = 2000

        # det_pulse_duration
        v_duration_overhauser_pulse_np = np.arange(0, 101, 1)
        n_overhauser_pulses_steps = len(v_duration_overhauser_pulse_np)

        # corrD, 5 us long
        corrD_36_np = -(initialize['gate_36']*duration_init_pulse_in_clk_cycles + det_min['gate_36']*v_duration_overhauser_pulse_np/4 + measurement_point['gate_36']*total_time_at_measurement_point_in_clk_cycles)/self.CW_amp*self.dividers['gate_36']/corrD_duration_in_clk_cycles
        corrD_29_np = -(initialize['gate_29']*duration_init_pulse_in_clk_cycles + det_min['gate_29']*v_duration_overhauser_pulse_np/4 + measurement_point['gate_29']*total_time_at_measurement_point_in_clk_cycles)/self.CW_amp*self.dividers['gate_29']/corrD_duration_in_clk_cycles

        # bake waveforms
        baked_waveforms = self._bake_overhauser_waveforms(v_duration_overhauser_pulse_np)

        
        amp_array = [('gate_36', (det_min['gate_36']/self.CW_amp*self.dividers['gate_36'])),
                     ('gate_29', (det_min['gate_29']/self.CW_amp*self.dividers['gate_29']))]

        # readout_length = 4940
        # chunk_size = 76
        # slices = readout_length // chunk_size

        with program() as overhauser_sequence:
            # SETTINGS OVERHAUSER
            ref_meas_I = declare(fixed, )
            ref_meas_Q = declare(fixed, )
            sliced_meas_I = declare(fixed, size=65)  # where I_2 is saved, size is number of slices
            sliced_meas_Q = declare(fixed, size=65)
            sliced_meas_stepper = declare(int, )
            repetiotion_stepper = declare(int, )
            overhauser_pulse_stepper = declare(int, )

            corrD_36 = declare(fixed, value=corrD_36_np.tolist())
            corrD_29 = declare(fixed, value=corrD_29_np.tolist())

            ref_meas_I_stream = declare_stream()  # I_1 ref
            ref_meas_Q_stream = declare_stream()  # Q_1 ref
            sliced_meas_I_stream = declare_stream()  # I_2 sig
            sliced_meas_Q_stream = declare_stream()  # Q_2 sig

            with for_(repetiotion_stepper, 0, repetiotion_stepper < n_repetitions, repetiotion_stepper+1):
                self._run_overhauser_oscillations(amp_array,
                                                  initialize,
                                                  duration_init_pulse_in_clk_cycles,
                                                  duration_wait_after_init_in_clk_cycles,
                                                  measurement_point,
                                                  overhauser_pulse_stepper,
                                                  n_overhauser_pulses_steps,
                                                  time_at_measurement_point_per_RF_burst_in_clk_cycles,
                                                  ref_meas_I,
                                                  ref_meas_Q,
                                                  ref_meas_I_stream,
                                                  ref_meas_Q_stream,
                                                  baked_waveforms,
                                                  sliced_meas_I,
                                                  sliced_meas_Q,
                                                  corrD_duration_in_clk_cycles,
                                                  corrD_36,
                                                  corrD_29,
                                                  sliced_meas_stepper,
                                                  sliced_meas_Q_stream,
                                                  sliced_meas_I_stream)

            with stream_processing():
                ref_meas_I_stream.save_all("I_1")  # I_ref for estimating overhauser sequence
                ref_meas_Q_stream.save_all("Q_1")  # Q_ref for estimating overhauser sequence
                sliced_meas_I_stream.buffer(n_repetitions, n_overhauser_pulses_steps, 65).save_all("I_2")  # I_sig for estimating overhauser sequence
                sliced_meas_Q_stream.buffer(n_repetitions, n_overhauser_pulses_steps, 65).save_all("Q_2")  # Q_sig for estimating overhauser sequence

        return overhauser_sequence

    def _bake_overhauser_waveforms(self, v_duration_overhauser_pulse_np):
        baked_waveforms = []
        for overhauser_duration in v_duration_overhauser_pulse_np:
            with baking(self.config, padding_method='symmetric_l') as b:
                b.add_op('gate_36_pulse', 'gate_36', [self.CW_amp]*overhauser_duration+[0])
                b.add_op('gate_29_pulse', 'gate_29', [self.CW_amp]*overhauser_duration+[0])

                b.play('gate_36_pulse', 'gate_36')
                b.play('gate_29_pulse', 'gate_29')
            baked_waveforms.append(b)

        return baked_waveforms

    def _run_overhauser_oscillations(self,
                                     amp_array,
                                     initialize,
                                     duration_init_pulse_in_clk_cycles,
                                     duration_wait_after_init_in_clk_cycles,
                                     measurement_point,
                                     overhauser_pulse_stepper,
                                     n_overhauser_pulses_steps,
                                     time_at_measurement_point_per_RF_burst_in_clk_cycles,
                                     ref_meas_I,
                                     ref_meas_Q,
                                     ref_meas_I_stream,
                                     ref_meas_Q_stream,
                                     baked_waveforms,
                                     sliced_meas_I,
                                     sliced_meas_Q,
                                     corrD_duration_in_clk_cycles,
                                     corrD_36,
                                     corrD_29,
                                     sliced_meas_stepper,
                                     sliced_meas_Q_stream,
                                     sliced_meas_I_stream):

        with for_(overhauser_pulse_stepper, 0, overhauser_pulse_stepper < n_overhauser_pulses_steps, overhauser_pulse_stepper+1):
            # initialize singlet
            align("gate_36", "gate_29")
            play("CW"*amp((initialize['gate_36'])/self.CW_amp*self.dividers['gate_36']), "gate_36", duration=duration_init_pulse_in_clk_cycles)
            play("CW"*amp((initialize['gate_29'])/self.CW_amp*self.dividers['gate_29']), "gate_29", duration=duration_init_pulse_in_clk_cycles)

            # jumping  to reference point and waiting there
            align("gate_36", "gate_29")
            play("CW"*amp((-initialize['gate_36'] + measurement_point['gate_36'])/self.CW_amp*self.dividers['gate_36']), "gate_36", duration=duration_wait_after_init_in_clk_cycles)
            play("CW"*amp((-initialize['gate_29'] + measurement_point['gate_29'])/self.CW_amp*self.dividers['gate_29']), "gate_29", duration=duration_wait_after_init_in_clk_cycles)

            # measure reference signal
            align("gate_36", "gate_29", "bottom_right_DQD_readout")
            play("CW"*amp(0.0), "gate_36", duration=time_at_measurement_point_per_RF_burst_in_clk_cycles)
            play("CW"*amp(-0.0), "gate_29", duration=time_at_measurement_point_per_RF_burst_in_clk_cycles)
            measure("readout_pulse_3us", "bottom_right_DQD_readout", None, demod.full("cos", ref_meas_I, "out1"), demod.full("sin", ref_meas_Q, "out1"))

            # save values
            save(ref_meas_I, ref_meas_I_stream)
            save(ref_meas_Q, ref_meas_Q_stream)

            # det_pulse
            align("gate_36", "gate_29")
            with switch_(overhauser_pulse_stepper):
                for j in range(n_overhauser_pulses_steps):
                    with case_(j):
                        baked_waveforms[j].run(amp_array)

            # meas signal
            align("gate_36", "gate_29", "bottom_right_DQD_readout")
            play("CW"*amp(0.0), "gate_36", duration=time_at_measurement_point_per_RF_burst_in_clk_cycles)
            play("CW"*amp(0.0), "gate_29", duration=time_at_measurement_point_per_RF_burst_in_clk_cycles)
            wait(125)  # to avoid resonator ringing at the measurement
            reset_phase("bottom_right_DQD_readout")
            measure("readout_pulse_5us", "bottom_right_DQD_readout", None, demod.sliced("cos", sliced_meas_I, 19, "out1"), demod.sliced("sin", sliced_meas_Q, 19, "out1"))

            # corrD of 5 us
            align("gate_36", "gate_29")
            play("CW"*amp(corrD_36[overhauser_pulse_stepper] - measurement_point['gate_36']/self.CW_amp*self.dividers['gate_36']), "gate_36", duration=corrD_duration_in_clk_cycles)
            play("CW"*amp(corrD_29[overhauser_pulse_stepper] - measurement_point['gate_29']/self.CW_amp*self.dividers['gate_29']), "gate_29", duration=corrD_duration_in_clk_cycles)
            align("gate_36", "gate_29")
            ramp_to_zero("gate_36", 1)
            ramp_to_zero("gate_29", 1)
            with for_(sliced_meas_stepper, 0, sliced_meas_stepper < 65, sliced_meas_stepper+1):
                save(sliced_meas_I[sliced_meas_stepper], sliced_meas_I_stream)
                save(sliced_meas_Q[sliced_meas_stepper], sliced_meas_Q_stream)
