import numpy as np
import scipy.optimize as opto
import matplotlib.pyplot as plt

def exp_func(x, a, b, c):
    x = np.linspace(0, 1, len(x))
    return a * np.exp(b*x) + c


def lin_func(x, m, c):
    x = np.linspace(0, 1, len(x))
    return m*x + c

def make_gauss(A, sig, mu):
    return lambda x: A/(sig * (2*np.pi)**.5) * np.e ** (-(x-mu)**2/(2 * sig**2))

def gauss_func(x, A, sig, mu):
    return np.array((A/(sig * (2*np.pi)**.5)) * np.e**(-(x-mu)**2/(2 * sig**2)))

def get_background(x, spectrum, offset=0):
    x = np.array(x, dtype=float)
    #p0 is seed parameters
    popt, pcov = opto.curve_fit(ft.exp_func, x, spectrum, p0=(0.01, 31, 35))
    a,b,c,= popt
    print a,b,c
    background_exp = ft.exp_func(x, a, b, c+offset)

    back_sub_fit = spectrum - background_exp 
    plt.plot(x, spectrum, 'r', label='Original Data')
    plt.plot(x, background_exp, 'k', label='Fiti DARREN Data')
    plt.plot(x, back_sub_fit, 'g', label='Fit DARREN Data')
    return background_exp 

def base_spectra(x, params_list, spread=80, offset=0):
    multi_gauss = np.zeros(len(x))
    adder = int(len(params_list)/2)
    for i in range(adder):
        A = params_list[i]
        mu = params_list[i+adder]
        multi_gauss += gauss_func(x, A, spread, mu+offset)
    return multi_gauss 

