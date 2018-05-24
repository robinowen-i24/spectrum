import file_scraper
from math import exp
import collections
from pprint import pprint
from itertools import product as iproduct

def test_emissions(incident_nrg, minimum_nrg=2000.0):
    incident_nrg = float(incident_nrg)
    poss_dict = {}
    bne_dict, edge_names_list, emis_names_list = file_scraper.bne()
     
    poss_absorber_list = []
    for elem in bne_dict.keys():
        for key in bne_dict[elem].keys():
            if key in edge_names_list:
                if minimum_nrg < bne_dict[elem][key] < incident_nrg:
                    #print elem, key, bne_dict[elem][key], minimum_nrg, bne_dict[elem][key], incident_nrg
                    poss_absorber_list.append([elem,key])
   
    emis_dict = collections.defaultdict(dict)
    for elem,key in poss_absorber_list:
        if key.startswith('K'):
            try:
                emis_dict[elem]['ka1'] = bne_dict[elem]['ka1']
            except:
                j=0
            try:
                emis_dict[elem]['ka2'] = bne_dict[elem]['ka2']
            except:
                j=0
            try:
                emis_dict[elem]['kb1'] = bne_dict[elem]['kb1']
            except:
                j=0
            try:
                emis_dict[elem]['kb2'] = bne_dict[elem]['kb2']
            except:
                j=0
            try:
                emis_dict[elem]['kb3'] = bne_dict[elem]['kb3']
            except:
                j=0
        elif key.startswith('L2'):
            try:
                emis_dict[elem]['lb1'] = bne_dict[elem]['lb1']
            except:
                j=0
            try:
                emis_dict[elem]['lg1'] = bne_dict[elem]['lg1']
            except:
                j=0
        elif key.startswith('L3'):
            try:
                emis_dict[elem]['la1'] = bne_dict[elem]['la1']
            except:
                j=0
            try:
                emis_dict[elem]['la2'] = bne_dict[elem]['la2']
            except:
                j=0
            try:
                emis_dict[elem]['lb2'] = bne_dict[elem]['lb2']
            except:
                j=0
            try:
                emis_dict[elem]['l1'] = bne_dict[elem]['l1']
            except:
                j=0
        elif key.startswith('M5'):
            try:
                emis_dict[elem]['ma1'] = bne_dict[elem]['ma1']
            except:
                j=0
    for elem, d in emis_dict.items():
        for k, v in d.items():
            if v[0] < minimum_nrg: 
               emis_dict[elem].pop(k)
        if emis_dict[elem] == {}:
               emis_dict.pop(elem)
    return emis_dict

def get_emissions(per_tab_dict, elem):
    thing = elem.split('_')[0]
    print elem, '------------->', per_tab_dict[thing]
    try:
        edge = elem.split('_')[1]
    except StandardError:
        edge = 'K'
    elem = elem.split('_')[0]
    if edge == 'K':
        emis_line = per_tab_dict[elem][4]
    elif edge == 'L1' or edge == 'L':
        emis_line = per_tab_dict[elem][4]
    elif edge == 'L2':
        emis_line = per_tab_dict[elem][5]
    elif edge == 'L3':# or edge == 'L':
        emis_line = per_tab_dict[elem][6]
    return emis_line

def get_possible_absorptions(elements, bne_dict, edge_names_list, minimum_energy, incident_energy):
    possible_absorbs = []
    for elem in elements:
        for key in bne_dict[elem].keys():
            if minimum_energy > bne_dict[elem][key]:
               continue
            elif incident_energy <= bne_dict[elem][key]:
               continue
            elif key not in edge_names_list:
               continue
            else:
                possible_absorbs.append([elem, key]) 
    return possible_absorbs
   
def get_allowed_emissions(bne_dict, incident_energy, minimum_energy, edge_names_list): 
    elements = [elem for elem in bne_dict.keys()]
    transitions = {'K': ['ka1', 'ka2', 'kb1', 'kb2', 'kb3'], 'L1':'None', 'L2':['lb1','lg1'] ,'L3':['la1','la2','lb2', 'l1'], 'M5':['ma1']}
    possible_absorptions = get_possible_absorptions(elements, bne_dict, edge_names_list, minimum_energy, incident_energy)
    possible_emissions = []
    for elem, absorb in possible_absorptions:
        for key in bne_dict[elem].keys():
            try:
               allowed_transitions = transitions[str(absorb.split('(')[0])]
               if key in allowed_transitions: 
                  if  bne_dict[elem][key][0] < minimum_energy:
                      continue
                  else:
                           possible_emissions.append([elem, key])
               else:
                 continue
            except:
                 continue
    return possible_emissions
    
def possible_emissions(incident_energy, minimum_energy=2000.0): 
    incident_nrg = float(incident_energy)
    bne_dict, edge_names_list, emis_names_list = file_scraper.bne()
    allowed_emissions_list = get_allowed_emissions(bne_dict, incident_energy, minimum_energy, edge_names_list) 
    emis_dict = collections.defaultdict(dict)
    for elem, key in allowed_emissions_list:
        try:
           emis_dict[elem][key]
        except:
           emission_energy, relative_intensity = bne_dict[elem][key]
           transmission_intensity = probability_of_transmission(emission_energy, relative_intensity)
           emis_dict[elem][key] = (emission_energy, transmission_intensity)
    return emis_dict

def probability_of_transmission(emission_energy, relative_intensity):
    air_density=0.001225 #g/cm^3
    detector_distance = 7  #attenuation length in cm
    coefficient = file_scraper.lookup_attenuation_coefficient(emission_energy)
    intensity_det_dist = relative_intensity * exp(-coefficient*air_density*detector_distance)
    return intensity_det_dist 
    
if __name__ == '__main__': 
   incident_energies = [12000, 4000, 8000, 20000, 17500, 100000, 0, 100000]
   minimum_energies = [2000,  8000, 4000,  2000,  5000,      0, 0,  50000]
   for i_e, m_e in zip(incident_energies, minimum_energies):
       test_dict = test_emissions(i_e, m_e)
       emis_dict = possible_emissions(i_e, m_e)
       assert test_dict == emis_dict
   print 'EOP'
