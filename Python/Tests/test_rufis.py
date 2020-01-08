import unittest
from nipype.interfaces.base import CommandLine
from QUIT.interfaces.core import NewImage, Diff
from QUIT.interfaces.rufis import MUPA, MUPASim, MUPAMT, MUPAMTSim, MT, MTSim
from QUIT.interfaces.mt import Lineshape

vb = True
CommandLine.terminal_output = 'allatonce'


class RUFIS(unittest.TestCase):
    def test_MUPAMT(self):
        seq = {
            'MUPA': {
                'TR': 2.5e-3,
                'Tramp': 5e-3,
                'FA': [6, 2, 2, 2, 2, 2],
                'Trf': [24, 24, 24, 24, 8, 8],
                'SPS': 512,
                'prep': ['inv', 'null', 'null', 'null', 't2-80', 'null'],
                'prep_pulses': {
                    'inv': {
                        'FAeff': 175.32508531003188,
                        'T_long': 0.006487,
                        'T_trans': 0.004396,
                        'int_b1_sq': 53390.0
                    },
                    't2-80': {
                        'FAeff': 0.0716197243913529,
                        'T_long': 0.005472,
                        'T_trans': 0.08083,
                        'int_b1_sq': 279600.0
                    },
                    'null': {
                        'FAeff': 0.0,
                        'T_long': 0.0,
                        'T_trans': 0.0,
                        'int_b1_sq': 0.0
                    }
                }
            }
        }
        sim_file = 'sim_mupa_mt.nii.gz'
        img_sz = [16, 16, 16]
        noise = 0.005

        NewImage(img_size=img_sz, fill=100.0,
                 out_file='M0_f.nii.gz', verbose=vb).run()
        NewImage(img_size=img_sz, grad_dim=0, grad_vals=(5.0, 25.0),
                 out_file='M0_b.nii.gz', verbose=vb).run()
        NewImage(img_size=img_sz, grad_dim=2, grad_vals=(0.8, 1.5),
                 out_file='T1_f.nii.gz', verbose=vb).run()
        NewImage(img_size=img_sz, grad_dim=1, grad_vals=(0.06, 0.25),
                 out_file='T2_f.nii.gz', verbose=vb).run()
        NewImage(img_size=img_sz, grad_dim=0, grad_vals=(1.0, 25.0),
                 out_file='M0_b.nii.gz', verbose=vb).run()
        NewImage(img_size=img_sz, fill=1.0,
                 out_file='B1.nii.gz', verbose=vb).run()
        NewImage(img_size=img_sz, grad_dim=2, grad_vals=(0.8, 1.5),
                 out_file='T1_f.nii.gz', verbose=vb).run()

        Lineshape(lineshape='SuperLorentzian',
                  out_file='lineshape.json', t2b=12e-6).run()
        MUPAMTSim(sequence=seq, in_file=sim_file, lineshape='lineshape.json',
                  M0_f='M0_f.nii.gz', T1_f='T1_f.nii.gz', T2_f='T2_f.nii.gz', M0_b='M0_b.nii.gz', B1='B1.nii.gz',
                  noise=noise, verbose=vb).run()
        MUPAMT(sequence=seq, lineshape='lineshape.json',
               in_file=sim_file, verbose=vb, threads=-1, covar=True).run()

        diff_M0_f = Diff(in_file='MUPAMT_M0_f.nii.gz', baseline='M0_f.nii.gz',
                         noise=noise, verbose=vb).run()
        diff_T1 = Diff(in_file='MUPAMT_T1_f.nii.gz', baseline='T1_f.nii.gz',
                       noise=noise, verbose=vb).run()
        diff_T2 = Diff(in_file='MUPAMT_T2_f.nii.gz', baseline='T2_f.nii.gz',
                       noise=noise, verbose=vb).run()
        diff_M0_b = Diff(in_file='MUPAMT_M0_b.nii.gz',
                         baseline='M0_b.nii.gz', noise=noise, verbose=vb).run()
        self.assertLessEqual(diff_M0_f.outputs.out_diff, 30)
        self.assertLessEqual(diff_T1.outputs.out_diff, 30)
        self.assertLessEqual(diff_T2.outputs.out_diff, 30)
        self.assertLessEqual(diff_M0_b.outputs.out_diff, 30)

    def test_MT(self):
        seq = {
            'MT': {
                'TR': 0.002012,
                'Tramp': 0.01,
                'Tspoil': 0.005,
                'Trf': 0.000028,
                'SPS': 48,
                'RUFIS_FA': [2, 8, 3, 3, 3, 3, 3, 3],
                'MT_FA': [0, 0, 30, 60, 800, 800, 800, 800],
                'MT_offsets': [0, 0, 0, 0, 1000, 2000, 4000, 8000],
                'MT_pulsewidth': 10e-3,
                'MT_pulse':
                {
                    'B1x': [9.587E-5, 0.0001917, 0.0001917, 0.0002876, 0.0002876, 0.0003835, 0.0004794, 0.0005752, 0.0006711, 0.000767, 0.0009587, 0.00115, 0.001342, 0.001534, 0.001822, 0.002109, 0.002493, 0.002972, 0.003451, 0.004027, 0.004602, 0.005369, 0.006232, 0.007094, 0.008245, 0.009491, 0.01083, 0.01237, 0.01419, 0.01611, 0.01841, 0.0209, 0.02368, 0.02675, 0.0302, 0.03403, 0.03835, 0.04305, 0.04832, 0.05398, 0.0603, 0.0673, 0.07487, 0.08312, 0.09213, 0.102, 0.1126, 0.1242, 0.1367, 0.1501, 0.1646, 0.1801, 0.1968, 0.2147, 0.2335, 0.2538, 0.2751, 0.2979, 0.3217, 0.3471, 0.3735, 0.4013, 0.4305, 0.4608, 0.4924, 0.5251, 0.559, 0.5941, 0.6302, 0.6672, 0.705, 0.7437, 0.783, 0.823, 0.8632, 0.904, 0.9448, 0.9856, 1.026, 1.067, 1.107, 1.146, 1.185, 1.223, 1.259, 1.294, 1.328, 1.36, 1.391, 1.419, 1.445, 1.47, 1.491, 1.511, 1.528, 1.542, 1.553, 1.562, 1.567, 1.57, 1.57, 1.567, 1.562, 1.553, 1.542, 1.528, 1.511, 1.491, 1.47, 1.445, 1.419, 1.391, 1.36, 1.328, 1.294, 1.259, 1.223, 1.185, 1.146, 1.107, 1.067, 1.026, 0.9856, 0.9448, 0.904, 0.8632, 0.823, 0.783, 0.7437, 0.705, 0.6672, 0.6302, 0.5941, 0.559, 0.5251, 0.4924, 0.4608, 0.4305, 0.4013, 0.3735, 0.3471, 0.3217, 0.2979, 0.2751, 0.2538, 0.2335, 0.2147, 0.1968, 0.1801, 0.1646, 0.1501, 0.1367, 0.1242, 0.1126, 0.102, 0.09213, 0.08312, 0.07487, 0.0673, 0.0603, 0.05398, 0.04832, 0.04305, 0.03835, 0.03403, 0.0302, 0.02675, 0.02368, 0.0209, 0.01841, 0.01611, 0.01419, 0.01237, 0.01083, 0.009491, 0.008245, 0.007094, 0.006232, 0.005369, 0.004602, 0.004027, 0.003451, 0.002972, 0.002493, 0.002109, 0.001822, 0.001534, 0.001342, 0.00115, 0.0009587, 0.000767, 0.0006711, 0.0005752, 0.0004794, 0.0003835, 0.0002876, 0.0002876, 0.0001917, 0.0001917, 0.0001438],
                    'B1y': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    'FA': 90,
                    'width': 12.8e-3
                }
            }
        }
        sim_file = 'sim_mt.nii.gz'
        img_sz = [16, 16, 3]
        noise = 0.005

        NewImage(img_size=img_sz, fill=100.0,
                 out_file='M0_f.nii.gz', verbose=vb).run()
        NewImage(img_size=img_sz, fill=1,
                 out_file='T1_f.nii.gz', verbose=vb).run()
        NewImage(img_size=img_sz, grad_dim=0, grad_vals=(80e-3, 250e-3),
                 out_file='T2_f.nii.gz', verbose=vb).run()
        NewImage(img_size=img_sz, grad_dim=1, grad_vals=(1, 33),
                 out_file='M0_b.nii.gz', verbose=vb).run()
        NewImage(img_size=img_sz, fill=12e-6,
                 out_file='T2_b.nii.gz', verbose=vb).run()
        NewImage(img_size=img_sz, fill=5,
                 out_file='k.nii.gz', verbose=vb).run()
        NewImage(img_size=img_sz, grad_dim=2, grad_vals=(0.8, 1.2),
                 out_file='B1.nii.gz', verbose=vb).run()

        Lineshape(lineshape='SuperLorentzian',
                  out_file='lineshape.json', t2b=12e-6).run()
        MTSim(sequence=seq, in_file=sim_file, lineshape='lineshape.json',
              M0_f='M0_f.nii.gz', T1_f='T1_f.nii.gz', T2_f='T2_f.nii.gz',
              M0_b='M0_b.nii.gz', T2_b='T2_b.nii.gz', k='k.nii.gz',
              B1='B1.nii.gz',
              noise=noise, verbose=vb).run()
        MT(sequence=seq, lineshape='lineshape.json',
           in_file=sim_file, verbose=vb, threads=-1).run()

        diff_M0_f = Diff(in_file='MT_M0_f.nii.gz', baseline='M0_f.nii.gz',
                         noise=noise, verbose=vb).run()
        diff_T1 = Diff(in_file='MT_T1_f.nii.gz', baseline='T1_f.nii.gz',
                       noise=noise, verbose=vb).run()
        diff_T2 = Diff(in_file='MT_T2_f.nii.gz', baseline='T2_f.nii.gz',
                       noise=noise, verbose=vb).run()
        diff_M0_b = Diff(in_file='MT_M0_b.nii.gz',
                         baseline='M0_b.nii.gz', noise=noise, verbose=vb).run()
        print('M0_f', diff_M0_f.outputs.out_diff, 'T1_f', diff_T1.outputs.out_diff,
              'T2_f', diff_T2.outputs.out_diff, 'M0_b', diff_M0_b.outputs.out_diff)
        self.assertLessEqual(diff_M0_f.outputs.out_diff, 10)
        self.assertLessEqual(diff_T1.outputs.out_diff, 10)
        self.assertLessEqual(diff_T2.outputs.out_diff, 10)
        self.assertLessEqual(diff_M0_b.outputs.out_diff, 10)


if __name__ == '__main__':
    unittest.main(verbosity=2)