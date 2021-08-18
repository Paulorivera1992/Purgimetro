import numpy as np
from scipy import interpolate
import time
from datetime import datetime

with open('cp_H2O.npy', 'rb') as f:
    Temps = np.load(f)
    cp    = np.load(f)
    print(Temps)
    print(cp)
    f_cp   = interpolate.interp1d(Temps,cp)
    print(f_cp(0.1))
    

dt1=datetime.now()
time.sleep(2)
dt2=datetime.now()

print((dt2-dt1).total_seconds())