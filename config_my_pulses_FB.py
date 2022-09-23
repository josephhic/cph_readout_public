config = {
    'version': 1,
    'controllers': {
        'con1': {
            'analog_outputs': {
                '1': {
                    'offset': 0.0,
                },
                '3': {
                    'offset': -0.0072,
                },
                '2': {
                    'offset': -0.0072,
                },
            },
            'digital_outputs': {
                '2': {},
            },
            'analog_inputs': {
                '2': {
                    'offset': 0,
                },
            },
        },
    },
    'elements': {
        'gate_29': {
            'singleInput': {
                'port': ('con1', 3),
            },
            'intermediate_frequency': 0.0,
            'hold_offset': {
                'duration': 24,
            },
            'operations': {
                'CW': 'CW',
            },
        },
        'gate_36': {
            'singleInput': {
                'port': ('con1', 2),
            },
            'intermediate_frequency': 0.0,
            'hold_offset': {
                'duration': 24,
            },
            'operations': {
                'CW': 'CW',
            },
        },
        'bottom_right_DQD_readout': {
            'singleInput': {
                'port': ('con1', 1),
            },
            'intermediate_frequency': 158256000,
            'operations': {
                'readout_pulse_10us': 'readout_pulse_10us',
                'readout_pulse_3ms': 'readout_pulse_3ms',
                'readout_pulse_4us': 'readout_pulse_4us',
                'readout_pulse_3us': 'readout_pulse_3us',
                'readout_pulse_2us': 'readout_pulse_2us',
                'readout_pulse_100us': 'readout_pulse_100us',
                'readout_pulse_5us': 'readout_pulse_5us',
                'readout_pulse_5us_full_demod': 'readout_pulse_5us_full_demod',
            },
            'outputs': {
                'out1': ('con1', 2),
            },
            'time_of_flight': 500,#24
            'smearing': 0,
        },
    },
    'pulses': {
        'CW': {
            'operation': 'control',
            'length': 100,
            'waveforms': {
                'single': 'const_wf',
            },
        },
        'readout_pulse_10us': {
            'operation': 'measurement',
            'length': 9956,
            'waveforms': {
                'single': 'readout_wf_0_2',
            },
            'integration_weights': {
                'cos': 'cos',
                'sin': 'sin',
            },
            'digital_marker': 'ON',
        },
        'readout_pulse_4us': {
            'operation': 'measurement',
            'length': 3952,
            'waveforms': {
                'single': 'readout_wf_0_2',
            },
            'integration_weights': {
                'cos': 'cos_4us',
                'sin': 'sin_4us',
            },
            'digital_marker': 'ON',
        },
        'readout_pulse_3us': {
            'operation': 'measurement',
            'length': 2964,
            'waveforms': {
                'single': 'readout_wf_0_2',
            },
            'integration_weights': {
                'cos': 'cos_3us',
                'sin': 'sin_3us',
            },
            'digital_marker': 'ON',
        },
        'readout_pulse_2us': {
            'operation': 'measurement',
            'length': 1976,
            'waveforms': {
                'single': 'readout_wf_0_2',
            },
            'integration_weights': {
                'cos': 'cos_2us',
                'sin': 'sin_2us',
            },
            'digital_marker': 'ON',
        },
        'readout_pulse_100us': {
            'operation': 'measurement',
            'length': 100000,
            'waveforms': {
                'single': 'readout_wf_0_2',
            },
            'integration_weights': {
                'cos': 'cos_100',
                'sin': 'sin_100',
            },
            'digital_marker': 'ON',
        },
        'readout_pulse_3ms': {
            'operation': 'measurement',
            'length': 3000000,
            'waveforms': {
                'single': 'readout_wf_0_2',
            },
            'integration_weights': {
                'cos': 'cos_buffered',
                'sin': 'sin_buffered',
            },
            'digital_marker': 'ON',
        },
        'readout_pulse_5us': {
            'operation': 'measurement',
            'length': 4940,
            'waveforms': {
                'single': 'readout_wf_0_2',
            },
            'integration_weights': {
                'cos': 'cos_5us',
                'sin': 'sin_5us',
            },
            'digital_marker': 'ON',
        },
        'readout_pulse_5us_full_demod': {
            'operation': 'measurement',
            'length': 4940,
            'waveforms': {
                'single': 'readout_wf_0_2',
            },
            'integration_weights': {
                'cos': 'cos_5us_full_demod',
                'sin': 'sin_5us_full_demod',
            },
            'digital_marker': 'ON',
        },
    },
    'waveforms': {
        'const_wf': {
            'type': 'constant',
            'sample': 0.25,
        },
        'zero_wf': {
            'type': 'constant',
            'sample': 0.0,
        },
        'readout_wf_0_2': {
            'type': 'constant',
            'sample': 0.2,
        },
    },
    'digital_waveforms': {
        'ON': {
            'samples': [(1, 0)],
        },
    },
    'integration_weights': {
        'cos': {
            'cosine': [(1.0, 9956)],
            'sine': [(0.0, 9956)],
        },
        'sin': {
            'cosine': [(0.0, 9956)],
            'sine': [(1.0, 9956)],
        },
        'cos_100': {
            'cosine': [(1.0, 100000)],
            'sine': [(0.0, 100000)],
        },
        'sin_100': {
            'cosine': [(0.0, 100000)],
            'sine': [(1.0, 100000)],
        },
        'cos_4us': {
            'cosine': [(1.0, 3952)],
            'sine': [(0.0, 3952)],
        },
        'sin_4us': {
            'cosine': [(0.0, 3952)],
            'sine': [(1.0, 3952)],
        },
        'cos_3us': {
            'cosine': [(1.0, 2964)],
            'sine': [(0.0, 2964)],
        },
        'sin_3us': {
            'cosine': [(0.0, 2964)],
            'sine': [(1.0, 2964)],
        },
        'cos_2us': {
            'cosine': [(1.0, 3000)],
            'sine': [(0.0, 3000)],
        },
        'sin_2us': {
            'cosine': [(0.0, 1976)],
            'sine': [(1.0, 1976)],
        },
        'cos_buffered': {
            'cosine': [(1.0, 3000000)],
            'sine': [(0.0, 3000000)],
        },
        'sin_buffered': {
            'cosine': [(0.0, 3000000)],
            'sine': [(1.0, 3000000)],
        },
        'cos_5us': {
            'cosine': [(1.0, 4940)],
            'sine': [(0.0, 4940)],
        },
        'sin_5us': {
            'cosine': [(0.0, 4940)],
            'sine': [(1.0, 4940)],
        },
        'cos_5us_full_demod': {
            'cosine': [(0.013157894736842105, 4940)],  #4940 is readoutpulse length in ns, 0.012.. is given by number of slices divided by 4940 (ns)
            'sine': [(0.0, 4940)],
        },
        'sin_5us_full_demod': {
            'cosine': [(0.0, 4940)],
            'sine': [(0.013157894736842105, 4940)],
        },
    },
}