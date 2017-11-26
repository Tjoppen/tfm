from math import *
import subprocess
import numpy

# 30..10 meters:
# Best so far: S = 4.900000, LD = 300.000000 -> eff = 30.317641 %
# Best so far: S = 5.900000, LD = 320.000000 -> eff = 30.589368 %
# Best so far: S = 6.700000, LD = 280.000000 -> eff = 32.362550 %
# No better configuration inside S = [6.7, 9.9], LD = [250, 320]

# 40..10 meters:
# Best so far: S = 7.200000, LD = 0.000000 -> eff = 24.915042 %
# Best so far: S = 9.900000, LD = 0.000000 -> eff = 26.521995 %
# Best so far: S = 40.000000, LD = 0.000000 -> eff = 42.874596 %

# 80..10 meters:
# Best so far: S = 50.000000, LD = 0.000000 -> eff = 10.879498 %

# 160..19 meters:
# Best so far: S = 40.000000, LD = 0.000000 -> eff = 3.001190 %
# Best so far: S = 110.000000, LD = 0.000000 -> eff = 3.170590 %
# With H=20 meters:
# Best so far: S = 80.000000, LD = 0.000000 -> eff = 28.613019 %

best = None
besteff = None
for S in numpy.arange(40, 200.0, 5):   # separation
  #for LD in numpy.arange(250, 400, 10):  # balancing resistor
  for LD in list(numpy.arange(0, 1000, 100)) + list(numpy.arange(1000,10000,1000)):  # balancing resistor
    #LD = 0
    #LD = 300 #was best for L = 0.1 .. 1.5
    print('S = %f, LD = %f' % (S, LD))

    effs = []
    # If I were a bit more competent with NEC2 I'd do a frequency sweep + SWR measurement inside it
    # For now I calculate one frequency at a time and associated SWR for each input parameter set
    for f in \
        list(numpy.arange( 1.810,  2.000, 0.020)) +\
        list(numpy.arange( 3.500,  3.800, 0.020)) +\
        list(numpy.arange( 7.000,  7.200, 0.010)) +\
        list(numpy.arange(10.100, 10.150, 0.010)) +\
        list(numpy.arange(14.000, 14.350, 0.050)) +\
        list(numpy.arange(18.068, 18.168, 0.010)) +\
        list(numpy.arange(21.000, 21.450, 0.050)) +\
        list(numpy.arange(24.890, 24.990, 0.050)) +\
        list(numpy.arange(28.000, 29.700, 0.100)):

      # Input power and impedance -> voltage
      P  = 5
      Z0 = 800
      V  = sqrt(P*Z0*2)

      h = 0.05    # height of feed/load
      H = 6.0     # height of antenna
      d = 0.001   # wire diameter

      deck = '''CM Terminated folded monopole
CE
GW  1  1   0         0         0         0         0         {h}      {d}
GW  2  20  0         0         {h}       0         0         {H}      {d}
GW  3  10  0         0         {H}       {S}       0         {H}      {d}
GW  4  20  {S}       0         {h}       {S}       0         {H}      {d}
GW  5  1   {S}       0         0         {S}       0         {h}      {d}
GE  1
LD  0  5    1    1  {LD}       0         0
GN  1  0    0    0  0          0         0         0         0         0       
FR  0  1    0    0  {f}        0         0         0         0         0       
EX  0  1    1    0  {V}        0         0         0         0         0       
RP  0  37  72  1000  0         0         5.00E+00  5.0E+02  0         0       
EN
    '''.format(h=h, d=d, H=H, S=S, LD=LD, f=f, V=V)

      fil = open('temp.nec', 'w')
      fil.write(deck)
      fil.close()
      subprocess.call(['nec2c','-i','temp.nec'])

      with open('temp.out', 'r') as fil:
        for line in fil:
          #print(line)
          if 'ANTENNA INPUT PARAMETERS' in line:
            a = next(fil)
            b = next(fil)
            c = next(fil)
            cc = c.split()
            ZA = float(cc[6])+1j*float(cc[7])
          if 'POWER BUDGET' in line:
            input_power = next(fil)
            rad_power   = next(fil)
            struct_loss = next(fil)
            net_loss    = next(fil)
            efficiency  = float(next(fil).split()[2])/100.0

      # Reflected power ratio
      Pr = (abs(Z0-ZA)/abs(Z0+ZA))**2

      # Assume all reflected power is lost
      eff_tot = efficiency*(1-Pr)
      effs.append(eff_tot)
      #print('f = %2.3f: %.2f %%' % (f, eff_tot*100))

    meff = min(effs)
    if besteff is None or meff > besteff:
      besteff = meff
      best = (S,LD)
      print('Best so far: S = %f, LD = %f -> eff = %f %%' % (S, LD, meff*100))

