
############################################
# Functions for A-R power law calculatoins #
############################################

def calc_R_from_A(A, a, b, L):
    R = (A/(a*L))**(1/b)
    return R

def a_b(f_GHz, pol, approx_type='ITU'):
    from scipy.interpolate import interp1d
    
    if f_GHz>=1 and f_GHz<=100:
        if pol=='V' or pol=='v':
            f_a = interp1d(ITU_table[0,:], ITU_table[2,:], kind='cubic')
            f_b = interp1d(ITU_table[0,:], ITU_table[4,:], kind='cubic')
        elif pol=='H' or pol=='h':
            f_a = interp1d(ITU_table[0,:], ITU_table[1,:], kind='cubic')    
            f_b = interp1d(ITU_table[0,:], ITU_table[3,:], kind='cubic')
        else:
            ValueError('Polarizatoin must be V, v, H or h.')
        a = f_a(f_GHz)
        b = f_b(f_GHz)
    else:
        ValueError('Frequency must be between 1 Ghz and 100 GHz.');
    return a, b

import numpy as np
ITU_table = np.array([
  [1.000e+0, 2.000e+0, 4.000e+0, 6.000e+0, 7.000e+0, 8.000e+0, 1.000e+1, 
   1.200e+1, 1.500e+1, 2.000e+1, 2.500e+1, 3.000e+1, 3.500e+1, 4.000e+1, 
   4.500e+1, 5.000e+1, 6.000e+1, 7.000e+1, 8.000e+1, 9.000e+1, 1.000e+2],
  [3.870e-5, 2.000e-4, 6.000e-4, 1.800e-3, 3.000e-3, 4.500e-3, 1.010e-2,
   1.880e-2, 3.670e-2, 7.510e-2, 1.240e-1, 1.870e-1, 2.630e-1, 3.500e-1, 
   4.420e-1, 5.360e-1, 7.070e-1, 8.510e-1, 9.750e-1, 1.060e+0, 1.120e+0],
  [3.520e-5, 1.000e-4, 6.000e-4, 1.600e-3, 2.600e-3, 4.000e-3, 8.900e-3,
   1.680e-2, 3.350e-2, 6.910e-2, 1.130e-1, 1.670e-1, 2.330e-1, 3.100e-1,
   3.930e-1, 4.790e-1, 6.420e-1, 7.840e-1, 9.060e-1, 9.990e-1, 1.060e+0],
  [9.120e-1, 9.630e-1, 1.121e+0, 1.308e+0, 1.332e+0, 1.327e+0, 1.276e+0,
   1.217e+0, 1.154e+0, 1.099e+0, 1.061e+0, 1.021e+0, 9.790e-1, 9.390e-1,
   9.030e-1, 8.730e-1, 8.260e-1, 7.930e-1, 7.690e-1, 7.530e-1, 7.430e-1],
  [8.800e-1, 9.230e-1, 1.075e+0, 1.265e+0, 1.312e+0, 1.310e+0, 1.264e+0, 
   1.200e+0, 1.128e+0, 1.065e+0, 1.030e+0, 1.000e+0, 9.630e-1, 9.290e-1,
   8.970e-1, 8.680e-1, 8.240e-1, 7.930e-1, 7.690e-1, 7.540e-1, 7.440e-1]])
    
    