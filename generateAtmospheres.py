# -*- coding: utf-8 -*-
import numpy as np

#temperatures = np.arange(10**3.3, 10**5.3, 10**.02)
temperatures = np.logspace(3.3, 5.3, 57)
#for i in range(len(temperatures)):temperatures[i] = int(temperatures[i])
    
pressure = np.logspace(-4, 8, 25)
#for i in range(len(Nh)):Nh[i] = int(Nh[i])

#i = 0
for temp in temperatures:
    i = 0
    table=[]
    for p in pressure:
        concentration=p/(1.38*10**-16*temp)
	if ( concentration < 2.e19 ):
	    table.append([len(pressure)*100-i*100, temp, 0, concentration, 1])
            i += 1
	else:
	    break
    np.savetxt('T' + str(temp).split('.')[0] + '.atm', table, fmt = '%.2f %.2f  %.5e  %.5e %.5f')
