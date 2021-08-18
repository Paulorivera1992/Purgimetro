#!/usr/bin/python
# coding: utf8

import time
import Adafruit_GPIO.SPI as SPI
import MAX6675.MAX6675 as MAX6675
from datetime import datetime

# Raspberry Pi software SPI configuration.
CLK = 25
CS  = 24
DO  = 18
sensor = MAX6675.MAX6675(CLK, CS, DO)

#crear achivo de buffet
f=open('temperatura.txt','w')
f.close

f1=open('purga.txt','w')
f1.close

# Loop printing measurements every second.
print('Press Ctrl-C to quit.')
n=1
temp_pas2=200
temp_pas1=200
temp_pas=200
tiempo_inicio=0
tiempo_final=0
salida=0
T_max=0
while True:
  temp = sensor.readTempC()
  dt = datetime.utcnow().isoformat(sep=' ', timespec='milliseconds')
  f=open('temperatura.txt','a')

  if salida==0 and (temp-temp_pas2)>7:
    salida=1
    tiempo_inicio=dt
  elif salida==1 and (temp-temp_pas2)<-1:
    tiempo_final=dt
    f1=open('purga.txt','a')
    f1.write('Tiempo inicio: ' + str(tiempo_inicio)+' | Tiempo final: '+str(tiempo_final) + ' | Temperatura Maxima: '+str(T_max)+'\n')
    f1.close
    T_max=0
    salida=0
    
  
  if salida==1 and T_max<temp:
    T_max=temp
    
  print('time: '+dt + ' | '+'Temperature: {0:0.2F}°C'.format(temp)+' | salida: '+ str(salida)+' | Tmax: ' + str(T_max))
  f.write(str(dt)+', {0:0.2F}'.format(temp)+', '+str(salida)+', '+str(T_max))
  f.write('\n')
  f.close()
  print(str(temp-temp_pas2))
  temp_pas2=temp_pas1;
  temp_pas1=temp_pas;
  temp_pas=temp;
  time.sleep(0.5)