from cctbx.eltbx import henke, sasaki

def get_fp_fdp(args):
    assert len(args) == 2
    element = args[0]
    energy = float(args[1])

    for inelastic_scattering in (henke.table, sasaki.table):
      t = inelastic_scattering(element)
      fp_fdp = t.at_ev(energy)
      print fp_fdp.fp(), fp_fdp.fdp()
    
    inelastic_scattering = sasaki.table 
    print dir(sasaki.table)
    print type(inelastic_scattering)
    print sasaki.table(element).at_ev(energy).fp()
    print sasaki.table(element).at_ev(energy).fdp()
    print sasaki.table(element).label()
    print sasaki.table(element).atomic_number()
    
