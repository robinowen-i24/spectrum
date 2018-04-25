import os
f = open('files.all', 'r')
for l in f.readlines():
    old_name = l.rstrip('\n')
    new_name = l[:-5]
    os.system('cp %s %s' %(old_name, new_name))
    
