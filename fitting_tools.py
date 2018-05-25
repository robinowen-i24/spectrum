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

def get_scale(curve, data):
    results_list = []
    scale_list = []
    c_idx = np.where(curve == np.max(curve))[0][0]
    d_idx = np.where(data == np.max(data))[0][0]
    peak_pos_err = np.abs(c_idx-d_idx)

    for pos_scale in np.linspace(0,999999,100001):
        result = np.abs(data - (pos_scale*curve))
	sumit =  np.sum(result)
        if sumit < 0.0:
	    continue
        else:
	    results_list.append(sumit)
	    scale_list.append(pos_scale)
    minima = np.min(results_list)
    idx = results_list.index(minima)
    return scale_list[idx]
   

def get_shift(guess, raw, lo, hi):
    d = {}
    for x in range(-200, 200):
        residual = np.sum(raw[lo:hi] - guess[lo+x:hi+x])
        d[x] = residual
        #print x, residual
    shift = min(d, key=d.get)
    return shift

 
def base_spectra(x, emis_dict, spread=80, offset=0):
    multi_gauss = np.zeros(len(x))
    for line, info in emis_dict.items():
        position = info[0] 
        amplitude = info[1] 
        multi_gauss += gauss_func(x, amplitude, spread, position+offset)
    return multi_gauss 

def try_fit(scale_dict, poss_emis_dict, params_dict, vortex_nrg_axis, sum_spec):
    spread = 110
    offset = 0

    guess_spec = np.zeros(len(vortex_nrg_axis))
    main_elem = max(scale_dict, key=scale_dict.get)
    for elem in scale_dict.keys():
        list_of_lines = [x[0] for x in poss_emis_dict[elem].values()]
        lo = int(min(list_of_lines) - 300)
        hi = int(max(list_of_lines) + 300)
        shift = get_shift(guess_spec, sum_spec, lo, hi)
        print 'This is the shift', shift, 'elem', elem, lo, hi
    offset = -12

    guess_spec = np.zeros(len(vortex_nrg_axis))
    for elem,scale in scale_dict.items():
        base = base_spectra(vortex_nrg_axis, poss_emis_dict[elem], spread, offset) 
        elem_spectrum = scale * base
        guess_spec += elem_spectrum
 
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    fig.subplots_adjust(left=0.05, bottom=0.05, right=0.95, top=0.95, wspace=0.0, hspace=0.0)
    ax.plot(vortex_nrg_axis, guess_spec+offset, c='k', lw=1)
    ax.plot(vortex_nrg_axis,   sum_spec, c='c', lw=1)
    return 1
   
