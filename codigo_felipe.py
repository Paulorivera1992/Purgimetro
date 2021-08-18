
import numpy as np
from scipy import interpolate
%matplotlib inline

def Q_loss(T):
  dot_m = rho*A*u
  dot_Q = dot_m*f_cp(T)*(T-Tb)/1000 # kW
  return dot_m, dot_Q

with open('cp_H2O.npy', 'rb') as f:
    Temps = np.load(f)\n",
    cp    = np.load(f)\n",
    
    f_cp   = interpolate.interp1d(Temps,cp)
    one_atm= 101325.0
    D      = 20e-2              # Diameter of the exit pipe, m
    A      = np.pi*D**2/4
    Tb     = 273.15 + 20 # estimate temperature inside boiler
    Pb     = 1.01*one_atm  # pressure inside boiler
    Pout   = 1*one_atm
    rho    = 1000.0 # 
    # u      = 1 # m/s (typical) Change this for a model depending on the data
    u      = np.sqrt(2*(Pb-Pout)/rho)   # this velocity will depend on the conditions of the boiler T and P. Check this
    Nmax   = 1000
    
    # dt_open= 30  # time of opening
    # Nt     = 200
    # dt     = dt_open / Nt
    # t      = np.linspace(0,dt_open,Nt)
    # Tmax   = 0.5 * Tb # this will be given by the thermocouple measurements
    dot_m  = np.zeros(Nmax)
    dot_Q  = np.zeros(Nmax)
    Q      = 0.0
    m_tot  = 0.0
    
    lstop  = False
    dt     = 0.1 # time resolution
    t      = 0.0 # time of opening
    T      = 10  # in C. This should be the temperature recorded at each t
    
    for i in range(Nmax):
        dot_m[i], dot_Q[i] = Q_loss(T)
        # integrate to obtain total energy lost
        Q       = Q + dot_Q[i]*dt       # kJ
        m_tot   = m_tot + dot_m[i]*dt   # kg
        t       = t + dt                # time of the opening, s
        # condition to stop recording
        # lstop -> some condition to exit the loop if signal already decayed
        # lstop = True # here change the condition based on signal decay
        if lstop:
            break
