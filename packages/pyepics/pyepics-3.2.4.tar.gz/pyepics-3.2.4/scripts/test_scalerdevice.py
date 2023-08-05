import time
import numpy as np
import epics
from epics.devices import Scaler

s = Scaler('13IDC:scaler1')

s.CountTime(0.2)

def Read(s):
    return np.array(s.Read(), dtype='i8')
    
for i in range(100):
    s.Count(wait=True)
    c1 = Read(s)
    time.sleep(0.25)
    c2 = Read(s)
    if (c1-c2).sum() != 0:
        print 'Error: ', c1, c2
    else:
        print 'OK: ', c1
