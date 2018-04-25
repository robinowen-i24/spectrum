#!/dls_sw/apps/dials/dials-v1-9-0/build/bin/dials.python

import map_hdf5
import file_scraper
from emissions import possible_emissions
import numpy as np
import scipy.optimize as opto
import sys
#import math
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from matplotlib.colors import LinearSegmentedColormap
#import peakutils as pks


def get_sum_spectrum(fid):
    print fid 
    full_file_array = file_scraper.get_h5py_data(fid)

    indv_spectra_array = full_file_array[:,0,:]
    plt.plot(indv_spectra_array.T)
    num_of_spectra = indv_spectra_array.shape[0]
    num_of_bins    = indv_spectra_array.shape[1]
    print 'Number of spectra', num_of_spectra
    print 'Number of bins   ', num_of_bins

    spectrum_sum_scaled = (1.0 / num_of_spectra) * indv_spectra_array.sum(axis=0)
    #Slight fudge, scale needs better way of arriving at answer
    scale_vortex_nrg = 8041.0 / 801.0
    print 'Scale of Vortex to Energy', scale_vortex_nrg
    terminal_energy = scale_vortex_nrg * (num_of_bins-1)
    print 'Terminal energy', terminal_energy
    
    x_axis = scale_vortex_nrg * np.arange(0, num_of_bins, 1)
    one_ev_energy_axis = np.arange(0, np.floor(terminal_energy), 1)
    #one_ev_energy_axis = np.arange(0, math.floor(terminal_energy), 1)
    spectrum_sum_scal_mapped = interp1d(x_axis, spectrum_sum_scaled, 'linear')(one_ev_energy_axis) 

    #shift vertically
    
    spectrum_sum_scal_mapped = spectrum_sum_scal_mapped #- 8.0 
    return one_ev_energy_axis, spectrum_sum_scal_mapped

def get_background(x, spectrum, offset=0):
    x = np.array(x, dtype=float)
    #p0 is seed parameters
    popt, pcov = opto.curve_fit(exp_func, x, spectrum, p0=(0.01, 31, 35))
    a,b,c,= popt
    print a,b,c
    background_exp = exp_func(x, a, b, c+offset)

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
    if np.abs(c_idx - d_idx) > 7000:
       print 'WARNING THIS HAPPENED'
       return 0.0
    for pos_scale in np.linspace(0,300,10001):
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

def base_spectra(x, params_list, spread=80, offset=0):
    multi_gauss = np.zeros(len(x))
    adder = int(len(params_list)/2)
    for i in range(adder):
        A = params_list[i]
        mu = params_list[i+adder]
        multi_gauss += gauss_func(x, A, spread, mu+offset)
    return multi_gauss 
    
def get_scale_dict(poss_emis_dict, vortex_nrg_axis, sum_spec, spread, offset, cutoff, exclude_list, include_list):
    per_tab_dict = file_scraper.get_per_tab_dict()
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1, axisbg='0.2')
    fig.subplots_adjust(left=0.05, bottom=0.05, right=0.95, top=0.95, wspace=0.0, hspace=0.0)
    ax.plot(vortex_nrg_axis, sum_spec, c='w', lw=1)
    scale_dict = {}
    
    print '\n\n'
    print per_tab_dict.keys()
    print include_list
    if 'all' in exclude_list:
        exclude_list = set.difference(set(per_tab_dict.keys()), set(include_list))
    
    print 'EXCLUDE LIST', exclude_list
    for elem, emis_dict in poss_emis_dict.items():
        if elem in exclude_list:
            continue
        elem_color = per_tab_dict[elem][3]
	emis_line_list = []
        for line_type in poss_emis_dict[elem].keys():
            emis_line, rel_int = poss_emis_dict[elem][line_type]
            if emis_line == -1.0:
                #print ' %s %s has an emission peak of -1.0'%(elem, line_type)
		continue
            emis_line_list.append(emis_line)
        mini = int(min(emis_line_list) - 300)
        maxi = int(max(emis_line_list) + 300)
        emis_nrg_axis = np.arange(mini, maxi, 1)
	#print elem,  mini, maxi
        lo_index = np.where(vortex_nrg_axis==mini)[0][0]
        hi_index = np.where(vortex_nrg_axis==maxi)[0][0]
        sum_spec_cut = sum_spec[lo_index:hi_index]

        A_list = []
        mu_list = []
        for line_type in poss_emis_dict[elem].keys():
            emis_line, rel_int = poss_emis_dict[elem][line_type]
            if emis_line == -1.0:
		continue
            if int(emis_line) not in emis_nrg_axis :
                continue
            else:
               A_list.append(rel_int)
               mu_list.append(emis_line)

        params_list = A_list + mu_list 
        base = base_spectra(emis_nrg_axis, params_list, spread, offset) 
        if len(A_list) == 0:
            continue
        else:
            scale_result = get_scale(base, sum_spec_cut)
	    if scale_result < cutoff and elem not in include_list:
                continue
		#scale_dict[elem] = 0.0
	    else: 
                print elem, 'ELEMENT'
                print 'A_list', A_list 
                print 'mu_list', mu_list
                print 'scale', scale_result, 'cutoff', cutoff
	        scale_dict[elem] = scale_result
                #ax.plot(emis_nrg_axis, base, c=elem_color)
                ax.plot(emis_nrg_axis, scale_result*base, c=elem_color,lw=3, label=elem)
                ax.plot(emis_nrg_axis, sum_spec_cut, c='k')
        print
    return scale_dict

def main(*args):
    minimum_nrg = 2000
    incident_nrg = 20000
    cutoff = 2.5
    mapme = False
    spread = 100.0
    offset = -4.0
    exclude_list = []
    include_list = []
    for arg in args:
        print arg
        k = arg.split("=")[0]
        v = arg.split("=")[1]
        if 'file' in k:
            fid = v
	elif 'energy' in k:
	    incident_nrg = float(v)
        elif 'map' in k:
            mapme = True
        elif 'exclude' in k:
            exclude_list = v.lstrip('[').rstrip(']').split(',')
        elif 'include' in k:
            include_list = v.lstrip('[').rstrip(']').split(',')
        elif 'cutoff' in k:
            cutoff = float(v)
        elif 'offset' in k:
            offset = float(v)
        elif 'spread' in k:
            spread = float(v)

    print exclude_list 
    print include_list 
    poss_emis_dict = possible_emissions(incident_nrg, minimum_nrg)
    print '\n\n'

    #Get the Sum Spectra vs Energy from the hdf5 file
    vortex_nrg_axis, sum_spec = get_sum_spectrum(fid)
    #Get emission line standards
    per_tab_dict = get_per_tab_dict()
   
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1, axisbg='0.2')
    fig.subplots_adjust(left=0.05, bottom=0.05, right=0.95, top=0.95, wspace=0.0, hspace=0.0)

    mini, maxi = int(minimum_nrg), int(incident_nrg)
    emis_nrg_axis = np.arange(mini, maxi, 1)
    lo_index = np.where(vortex_nrg_axis==mini)[0][0]
    hi_index = np.where(vortex_nrg_axis==maxi)[0][0]
    sum_spec_cut = sum_spec[lo_index:hi_index]
    ax.plot(emis_nrg_axis, sum_spec_cut, c='k', label='sum_spec_cut')
    #baseline_values = pks.baseline(sum_spec_cut, deg = 12)
    #ax.plot(emis_nrg_axis, baseline_values, '-', color='b', label='peakutils baseline')
    #background_data = get_background(emis_nrg_axis, sum_spec_cut)
    scale_dict = get_scale_dict(poss_emis_dict, vortex_nrg_axis, sum_spec, spread, offset, cutoff, exclude_list, include_list)
    print scale_dict 
    total = np.zeros((1, len(emis_nrg_axis)))
    print spread, offset 
    plt.legend(loc='upper left')
    fig.show(block=False)

    if mapme:
        try:
            map_fig = map_hdf5.mapme(fid, scale_dict, cutoff, include_list)
        except StandardError:
            print 'Mapping failed'

    plt.show()
    print 'EOM'

if __name__ == '__main__':
    main(*sys.argv[1:])

plt.close()
print 'EOP'
