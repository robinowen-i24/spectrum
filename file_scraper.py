import os
import re
import sys
import h5py
import collections
import numpy as np

def bne():
    approximates = [100,61,23,12,9,60,100,11,68,26,15,100]
    f = open('lookup_tables/bne.dat','r')
    bne = collections.defaultdict(dict)
    for line in f.readlines():
        if line.startswith('b'):
            entry = line.rstrip().split()
            if entry[1] == 'No':
                edge_names_list = entry[3:]
            else:
                num  = int(entry[1])
                elem = entry[2]
                strings = entry[3:]
                abs_edges = []
                for s in strings:
                    if s == '-':
                        abs_edges.append(-1)                
                    else:
                        abs_edges.append(float(s))                
                for i,edge in enumerate(edge_names_list[:len(abs_edges)]):
                    bne[elem][edge] = abs_edges[i]

        elif line.startswith('e'):
            entry = line.rstrip().split()
            if entry[1] == 'No':
                emis_names_list = entry[3:]
            else:
                num  = int(entry[1])
                elem = entry[2]
                strings = entry[3:]
                emis_lines = []
                for counter,s in enumerate(strings):
                    if s == '-':
                        e,i = -1, 0
                    else:
                        e,i = s.split(',')
                        if i == '-':
                            i = approximates[counter] 
                    emis_lines.append( (float(e), float(i)) )
                num_of_emiss = len(emis_lines)
                for i,emis in enumerate(emis_names_list[:num_of_emiss]):
                    bne[elem][emis] = emis_lines[i]
    f.close()
    return bne, edge_names_list, emis_names_list

def get_per_tab_dict():
    dir = 'lookup_tables/'
    per_tab_dict = {}
    f = open(dir + 'periodic_table.csv', 'r')
    for line in f.readlines():
        [z, mass, long_name, short_name] = line.rstrip('\r\n').split(',')
        per_tab_dict[short_name.title()] = [long_name.title(), int(z), float(mass)]
    f.close()

    f = open(dir + 'pymol_colors.txt', 'r')
    for line in f.readlines():
        [long_name, r, g, b] = line.split()
        long_name = long_name.title()
        rgb = (float(r), float(g), float(b))
        for z, v in per_tab_dict.items():
           if long_name in v:
               v.append(rgb) 
    f.close()

    f = open('lookup_tables/mca_roi_conversion.txt', 'r')
    scale_list = []
    for line in f.readlines()[2:]:
        if line.startswith('#'):
            continue
        else:
            energy, chnl = [float(x) for x in line.split()]
            scale_list.append(energy / chnl)
    scale = np.array(scale_list).mean()
    print 'Scale from Channel to Energy:', scale
    f.close()
            
    f = open('lookup_tables/FluorescenceScanROILookupTable', 'r')
    for line in f.readlines():
        if line.startswith('#'):
            continue
        [Z_K, llm, hlm] = line.split(',')
        short_name = Z_K.split('_')[0].title()
        emission_line = Z_K.split('_')[1].title()
        llm = int(float(llm) / scale)
        hlm = int(float(hlm) / scale)
        per_tab_dict[short_name].append([emission_line, llm, hlm])
    f.close()
    return per_tab_dict
    f = open('lookup_tables/FluorescenceScanROILookupTable', 'r')

def get_gridscan_data(h5_full_path_fid):
    path = '/'.join(h5_full_path_fid.split('/')[:-1])
    if path == '':
        path = '.'
    h5_fid = h5_full_path_fid.split('/')[-1]
    print 'path', path
    print 'h5_fid', h5_fid
    moniker = h5_fid.split('zlayer')[0].rstrip('_')
    print 'moniker', moniker
    fid_list = []
    for fid in sorted(os.listdir(path)):
        if fid.endswith('.gridscan'):
	    if fid.startswith(moniker):
	        print '.gridscan file found', fid, '\n\n'
		fid_list.append(fid)
    if len(fid_list) != 1:
        print 'No .gridscan file found'
        return 0, 0
    else:
	gs_fid = fid_list[0]
	f = open(path+'/'+gs_fid, 'r')
	for line in f.readlines():
	    print line.rstrip()
	    if 'Grid dimensions' in line:
		z = re.findall('[+-]?\d+(?:\.\d+)?', line)
		xdim = int(z[0])
		ydim = int(z[1])
                x_step_size = float(z[2])
                y_step_size = float(z[3])
	    if 'Start' in line:
		z = re.findall('[+-]?\d+(?:\.\d+)?', line)
                x_start = float(z[0])
                y_start = float(z[1])
        return xdim, ydim, x_step_size, y_step_size, x_start, y_start

def get_h5py_data(fid): 
    h5f = h5py.File(fid, 'r')
    array = h5f['entry/instrument/detector/data'][:]
    h5f.close()
    return array

