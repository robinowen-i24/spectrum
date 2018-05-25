#!/usr/bin/python
import file_scraper
from emissions import get_emissions
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

def extents(f):
  #stolen from https://bl.ocks.org/fasiha/eff0763ca25777ec849ffead370dc907
  delta = f[1] - f[0]
  return [f[0] - delta/2, f[-1] + delta/2]

def shape_array(array, new_shape, sqz_dim=0, squeeze=True):
    orig_array = array[:]
    orig_shape = orig_array.shape
    print '\n', 40*'-', 'Original shape:', orig_shape 
    # Squeezing selects the middle dimension and 
    # reduces from (dim1, dim2, dim3) to (dim1, dim3)
    if squeeze == True:
        print 'Squeezing Array'
        if sqz_dim:
           dim = sqz_dim
        else:
           dim = 0
        try:
            select_array = array[:, dim, :]
            sqz_array = select_array.squeeze()
        except StandardError:
            print 'Squeezing Failed'
            return 0 
    try:
        (new_shape[0] * new_shape[1]) == sqz_array.shape[0]
        print 'Reshaping From:', sqz_array.shape 
        dim0 = new_shape[0]
        dim1 = new_shape[1]
        dim2 = orig_shape[-1]
        if squeeze == True:
            shaped_array = sqz_array.reshape(dim1, dim0, dim2)
        else:
            shaped_array = sqz_array.reshape(dim1, dim0, orig_shape[1], dim2)
        print '            To:', shaped_array.shape
	print 'Format appears: (Y,  X,  Channel) in array'
        return shaped_array

    except StandardError:
        print 'Failed to Reshape'
        f_list = get_factor_list(int(array.shape[0]))
        choice = raw_input('Would you like to pick a different array shape (y/n)? ')
        if choice == 'y' or choice == '':
            user_input = raw_input('Type grid hape- x,y -here seperated by a comma ')
	    if user_input == '':
	        (a,b) = f_list[-1]
	    else:
                a, b = user_input.split(',')
            user_shape = [int(a), int(b)]
	    print 'Using:', user_shape
            return shape_array(orig_array, user_shape)
        else:
            return 0

def slice_and_sum_array(array, window):
    dim0 = array.shape[0]
    dim1 = array.shape[1]
    dim2 = array.shape[2]
    array.reshape((dim1,dim0,dim2))
    lo, hi = window     
    #print 'slice', part_array.shape
    part_array = array[:, :, lo:hi]
    #print 'sum', part_array.shape
    part_array = part_array.sum(axis=2)
    #print 'Flip Every Other Line'
    part_array[1::2, :] = part_array[1::2, ::-1]
    return part_array 

def get_factor_list(value):
    'Here are a a list of possible factors for', value
    factor_list = []
    for i in range(1, int(value**0.5)+1):
        if value % i == 0:
            factor_list.append((i, int(value / i)))

    for factor in factor_list:
        print factor
    return factor_list

def mapme(fid, scale_dict, cutoff, include_list):
    elem_list = []
    scale_list = []
    print 'CUTOFF =', cutoff
    for line_name, scale in scale_dict.items():
        if scale >= cutoff:
            elem_list.append(line_name)
            scale_list.append(scale)
    xbox, ybox = get_factor_list(len(elem_list))[-1]

    if len(elem_list) > 16:
        print 'Too Long'
        xbox, ybox = 5,5 

    xdim, ydim, x_step_size, y_step_size, x_start, y_start = file_scraper.get_gridscan_data(fid)
    print '\tData from .gridscan file'
    print '\tGrid Dimensions', xdim, ydim
    print '\tStep Sizes', x_step_size, y_step_size
    print '\tStart Position', x_start, y_start
    spacex = np.linspace(x_start, x_start+(xdim*(x_step_size/1000.)))
    spacey = np.linspace(y_start, y_start+(xdim*(x_step_size/1000.)))
    aspect = float(y_step_size)/float(x_step_size)
    print 15*aspect, 15*(1./aspect)

    per_tab_dict = file_scraper.get_per_tab_dict()

    array = file_scraper.get_h5py_data(fid)
   
    #shp_array = shape_array(array, [xdim,ydim])
    shp_array = shape_array(array, [xdim,ydim])# - 15.0  
    print 'shaped array', shp_array.shape
    result_array = shp_array 

    # Try mean subtraction?
    #mean_sub_array = shp_array - shp_array.mean(axis=2, keepdims=True) 
    #print 'mean_sub    ', mean_sub_array.shape
    #result_array = mean_sub_array 

    print 'result      ', result_array.shape
    print 'slicing out channels'
    slc_array_list = []
    print 'element_list =', elem_list
    print 'element_list =', elem_list, '+', include_list
    print include_list
    #elem_list = elem_list + include_list
    for elem in elem_list:
        print elem
	emission_line = get_emissions(per_tab_dict, elem)
        print elem
        llm, hlm = emission_line[1], emission_line[2]
        print elem
	Z = elem.split('_')[0] 
        print elem, '\t', emission_line
        slc_array = slice_and_sum_array(result_array, [llm, hlm])
        slc_array_list.append(slc_array)

    fig, axs2 = plt.subplots(xbox, ybox, figsize=((15/aspect), 15), facecolor='0.3', edgecolor='k')
    #fig, axs2 = plt.subplots(xbox, ybox, facecolor='0.3', edgecolor='k')
    #fig, axs2 = plt.subplots(xbox, ybox, facecolor='0.3', edgecolor='k')
    axs2 = axs2.ravel()
    print 'Plotting'
    for i, elem in enumerate(elem_list):
	Z = elem.split('_')[0] 
	ray = slc_array_list[i]
        pymol_c =  per_tab_dict[Z][3]
        w2k = [(0, 0, 0), pymol_c]
        ct = LinearSegmentedColormap.from_list('ctest', w2k, N=300)
	#axs2[i].imshow(ray, cmap=ct, interpolation='nearest')
	axs2[i].imshow(ray, aspect='equal', extent=extents(spacex)+extents(spacey), origin='upper', cmap=ct, interpolation='nearest', vmin=0)
	axs2[i].set_title(elem, y=0.9, color='0.8', loc='left')
	#axs2[i].set_xticks([])
	#axs2[i].set_yticks([])

    fig.subplots_adjust(left=0.05,bottom=0.05,right=0.95,top=0.95,wspace=0.00,hspace=0.0)

    #xfid = fid.split('/')[-1]
    #'/dls/i24/data/2017/nr16818-47/processing/GoldDigger_170512'
    #output_fid = xfid[:-5] + '%s.png' %time.strftime("_%Y%m%d_%H%M%S")
    #print 'Saved in /Snapshots'
    #print output_fid
    #plt.savefig(output_fid, dpi=400, bbox_inches='tight', pad_inches=0)
    return fig
