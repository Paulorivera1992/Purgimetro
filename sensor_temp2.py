#!/usr/bin/python
# coding: utf8

import time
import Adafruit_GPIO.SPI as SPI
import MAX6675.MAX6675 as MAX6675
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style

style.use('fivethirtyeight')

fig = plt.figure()
ax1 = fig.add_subplot(111)

xs = []
ys = []

# Raspberry Pi software SPI configuration.
CLK = 25
CS  = 24
DO  = 18
sensor = MAX6675.MAX6675(CLK, CS, DO)

#crear achivo de buffet
f=open('temperatura.txt','w')
f.close

n=0

def animate(i):
    temp = sensor.readTempC()
    #dt = datetime.utcnow().isoformat(sep=' ', timespec='milliseconds')
    dt=time = datetime.utcnow().strftime("%H:%M:%S")
    print('time: '+dt + ' | '+'Temperature: {0:0.2F}°C'.format(temp))
    f=open('temperatura.txt','a')
    f.write('time: '+str(dt)+' | ')
    f.write('Temperature: {0:0.2F}'.format(temp))
    f.write('\n')
    f.close()
    n=len(ys)
    if(n>20):
      xs.pop(0)
      ys.pop(0)
      n=n-1 
    xs.append(dt)
    ys.append(temp)
    

    ax1.clear()
    ax1.plot(xs, ys)
    ax1.set_ylim([0, 100])
    for tick in ax1.get_xticklabels():
      tick.set_rotation(45)
    


ani = animation.FuncAnimation(fig, animate, interval=10)

plt.show()

# Loop printing measurements every second.
#print('Press Ctrl-C to quit.')
#while True:

  #time.sleep(0.5)