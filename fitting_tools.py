import numpy as np

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
