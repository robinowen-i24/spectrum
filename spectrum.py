#!/dls_sw/apps/dials/dials-v1-9-0/build/bin/dials.python

import map_hdf5
import file_scraper
from emissions import possible_emissions
import fitting_tools as ft

import sys
import argparse
import numpy as np
from os.path import isfile 
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from matplotlib.colors import LinearSegmentedColormap
#import peakutils as pks

def argparser():
    parser = argparse.ArgumentParser(description='SPECTRUM \n\
                                                  Fluoresence spectra analysis and element mapping \n\
                                                  https://github.com/DarrenSherrell/spectrum')
    parser.add_argument('input_file', metavar='fid', type=str,
                        help='hdf5 file location, i.e. /path/to/my/file.hdf5')
    parser.add_argument('-ie', '--incident_energy',  type=int, default = 20000,
                        help='incident energy of beam, defualt=20000')
    parser.add_argument('-me', '--minimum_energy',  type=int, default = 2000,
                        help='mimimum energy cutoff for fluoresence spectra, defualt=2000')
    parser.add_argument('-i', '--include_list',  type=str, nargs='+', default = [],
                        help='list of elements to include i.e. Fe K Ni')
    parser.add_argument('-e', '--exclude_list',  type=str, nargs='+', default = [],
                        help='list of elements to exclude i.e. Os W Ti or all')
    parser.add_argument('-o', '--offset',  type=float, default = -20.0,
                        help='fluoresence peak offset, defualt=-20.0')
    parser.add_argument('-s', '--spread',  type=float, default = 110.0,
                        help='spread/width of fluoresence peaks, defualt=110')
    parser.add_argument('-c', '--scale_cutoff',  type=float, default = 2.5,
                        help='minimum scale cutoff to remove incorrect peaks, defualt=2.5')
    parser.add_argument('-mp', '--mapme',  type=str, default='True',
                        help='flag to run element mapping on data, default=True')
    parser.add_argument('-indv', '--plot_indv',  type=bool, default=False, choices=[True, False],
                        help='If you wish to see the individual spectrum from each point in the grid')
    args=parser.parse_args() 
    if args.scale_cutoff <= 0.0:
       parser.error("scale_cutoff cannot be < = 0. No elements removed")
    if args.incident_energy <= args.minimum_energy:
       parser.error("Incident energy must be greater than minimum energy")
    if args.input_file.endswith('.hdf5'):
       if isfile(args.input_file):
           pass
       else:
          parser.error("File does not exist")
    else:
         parser.error("File type should be hdf5, file does not end in hdf5")
    return args                                      

def get_sum_spectrum(fid, plot_indv):
    print fid 
    full_file_array = file_scraper.get_h5py_data(fid)

    indv_spectra_array = full_file_array[:,0,:]
    if plot_indv == True:
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
    
    spectrum_sum_scal_mapped = spectrum_sum_scal_mapped - 8.0 
    return one_ev_energy_axis, spectrum_sum_scal_mapped

def get_scale(curve, data):
    results_list = []
    scale_list = []
    c_idx = np.where(curve == np.max(curve))[0][0]
    d_idx = np.where(data == np.max(data))[0][0]
    peak_pos_err = np.abs(c_idx-d_idx)
    # remove or understand
    #if np.abs(c_idx - d_idx) > 7000:
    #   print 'WARNING THIS HAPPENED'
    #   return 0.0
    for pos_scale in np.linspace(0,9999,10001):
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
    
def get_scale_dict(poss_emis_dict, vortex_nrg_axis, sum_spec, spread, offset, cutoff, exclude_list, include_list):
    per_tab_dict = file_scraper.get_per_tab_dict()
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    fig.subplots_adjust(left=0.05, bottom=0.05, right=0.95, top=0.95, wspace=0.0, hspace=0.0)
    ax.plot(vortex_nrg_axis, sum_spec, c='w', lw=1)
    scale_dict = {}
    
    if 'all' in exclude_list:
        exclude_list = set.difference(set(per_tab_dict.keys()), set(include_list))
    
    print 'EXCLUDE LIST', exclude_list
    print '\nINCLUDE LIST', include_list
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

        amp_list = []
        mu_list = []
        for line_type in poss_emis_dict[elem].keys():
            emis_line, rel_int = poss_emis_dict[elem][line_type]
            if emis_line == -1.0:
		continue
            if int(emis_line) not in emis_nrg_axis :
                continue
            else:
               amp_list.append(rel_int)
               mu_list.append(emis_line)

        params_list = amp_list + mu_list 
        base = ft.base_spectra(emis_nrg_axis, params_list, spread, offset) 
        if len(amp_list) == 0:
            continue
        else:
            scale_result = get_scale(base, sum_spec_cut)
	    if scale_result < cutoff and elem not in include_list:
                continue
		#scale_dict[elem] = 0.0
	    else: 
                print elem, '\t', scale_result, '\t', amp_list, mu_list, 'cutoff', cutoff
	        scale_dict[elem] = scale_result
                #ax.plot(emis_nrg_axis, base, c=elem_color)
                ax.plot(emis_nrg_axis, scale_result*base, c=elem_color,lw=3, label=elem)
                ax.plot(emis_nrg_axis, sum_spec_cut, c='k')
                x = emis_nrg_axis[np.argmax(base)]
                y = max(scale_result*base)
                ax.annotate(elem, xy=(x,y), xycoords='data', xytext=(2,2), textcoords='offset points', color=elem_color, fontsize=15)
    return scale_dict

def run(fid, minimum_nrg, incident_nrg, cutoff, mapme, spread, offset, include_list, exclude_list, plot_indv):
    poss_emis_dict = possible_emissions(incident_nrg, minimum_nrg)
    #Get the Sum Spectra vs Energy from the hdf5 file
    vortex_nrg_axis, sum_spec = get_sum_spectrum(fid, plot_indv)

    mini, maxi = int(minimum_nrg), int(incident_nrg)
    emis_nrg_axis = np.arange(mini, maxi, 1)
 
    plot_sum_spec = 0 
    if plot_sum_spec == 1: 
        fig = plt.figure()
        ax = fig.add_subplot(1,1,1, axisbg='0.2')
        fig.subplots_adjust(left=0.05, bottom=0.05, right=0.95, top=0.95, wspace=0.0, hspace=0.0)
        lo_index = np.where(vortex_nrg_axis==mini)[0][0]
        hi_index = np.where(vortex_nrg_axis==maxi)[0][0]
        sum_spec_cut = sum_spec[lo_index:hi_index]
        ax.plot(emis_nrg_axis, sum_spec_cut, c='r', label='sum_spec_cut')
        baseline_values = pks.baseline(sum_spec_cut, deg = 12)
        ax.plot(emis_nrg_axis, baseline_values, '-', color='b', label='peakutils baseline')
        background_data = ft.get_background(emis_nrg_axis, sum_spec_cut)

    scale_dict = get_scale_dict(poss_emis_dict, vortex_nrg_axis, sum_spec, spread, offset, cutoff, exclude_list, include_list)
    print scale_dict 
    total = np.zeros((1, len(emis_nrg_axis)))
    print spread, offset 
    if mapme == 'True' or mapme == True:
        try:
            map_fig = map_hdf5.mapme(fid, scale_dict, cutoff, include_list)
        except StandardError:
            print 'Mapping failed'
    plt.show()

def main(args):
    fid          = args.input_file
    minimum_nrg  = args.minimum_energy
    incident_nrg = args.incident_energy
    cutoff       = args.scale_cutoff
    mapme        = args.mapme
    spread       = args.spread
    offset       = args.offset
    include_list = args.include_list
    exclude_list = args.exclude_list
    plot_indv    = args.plot_indv
    for arg in vars(args):
        print arg, getattr(args, arg)
    run(fid, minimum_nrg, incident_nrg, cutoff, mapme, spread, offset, include_list, exclude_list, plot_indv)
    print 'EOM'

if __name__ == '__main__':
    args = argparser()
    main(args)
    #main(*sys.argv[1:])

plt.close()
print 'EOP'
