import spectrum

print 'Start Test'

fid          = 'test_data/33B10F_1_zlayer_1.hdf5' 
minimum_nrg  = 2000.0 
incident_nrg = 17000.0
cutoff       = 2.5 
mapme        = False
mapme        = True
spread       = 110 
offset       = -20
include_list = ['Fe', 'Se', 'K', 'V', 'Ti', 'Cu']
exclude_list = 'all'
plot_indv    = False

spectrum.run(fid, minimum_nrg, incident_nrg, cutoff, mapme, spread, offset, include_list, exclude_list, plot_indv)

print 'End Test'

