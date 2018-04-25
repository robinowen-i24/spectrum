import file_scraper
import collections

def possible_emissions(incident_nrg, minimum_nrg=2000.0):
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
        elif key.startswith('L1'):
            try:
                emis_dict[elem]['l1'] = bne_dict[elem]['l1']
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
        elif key.startswith('M1'):
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
