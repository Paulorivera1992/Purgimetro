#!/usr/bin/python
# coding: utf8

import time
import Adafruit_GPIO.SPI as SPI
import MAX6675.MAX6675 as MAX6675
from datetime import datetime
from influxdb import InfluxDBClient

# Raspberry Pi software SPI configuration.
CLK = 25
CS  = 24
DO  = 18
sensor = MAX6675.MAX6675(CLK, CS, DO)

dt = datetime.utcnow().isoformat(sep=' ', timespec='milliseconds')
dt1=datetime.now()
dt2=datetime.now()
T_max2=100.00
client = InfluxDBClient(host='localhost', port=8086)
client.switch_database('Purga_caldera')
client.create_retention_policy('awesome_policy', '10d', 10, default=True)
json_payload2 = [{
  "measurement": "Tiempo_purga",
  "tags": {
    "Caldera": "1",
    },
    "time": dt,
    "fields": {
      "hora_inicio": dt1.hour,
      "minuto_inicio": dt1.minute,
      "segundo_inicio": dt1.second, 
      "hora_termino": dt2.hour,
      "minuto_termino": dt2.minute,
      "segundo_termino": dt2.second, 
      "Temperatura_maxima": T_max2,                
      }
    }]

client.write_points(json_payload2)

#crear achivo de buffet
f=open('/home/ubuntu/Gasco/temperatura.txt','w')
f.close

f1=open('/home/ubuntu/Gasco/purga.txt','w')
f1.close

f2=open('/home/ubuntu/Gasco/tiempos.txt','w')
f2.close
# Loop printing measurements every second.
#print('Press Ctrl-C to quit.')
n=1
temp_pas2=200
temp_pas1=200
temp_pas=200
tiempo_inicio=0
tiempo_final=0
salida=0
T_max=0
n=0
while True:
  tiempo=datetime.now()
  temp = sensor.readTempC()
  dt = datetime.utcnow().isoformat(sep=' ', timespec='milliseconds')
  f=open('/home/ubuntu/Gasco/temperatura.txt','a')

  if salida==0 and (temp-temp_pas2)>7 and n>3:
    salida=1
    tiempo_inicio=dt
    dt0=datetime.now()
  elif salida==1 and (temp-temp_pas2)<-1:
    salida=0
    tiempo_final=dt
    dt1=dt0
    dt2=datetime.now()
    T_max2=T_max
    f1=open('/home/ubuntu/Gasco/purga.txt','a')
    f1.write('Tiempo inicio: ' + str(tiempo_inicio)+' | Tiempo final: '+str(tiempo_final) + ' | Temperatura Maxima: '+str(T_max)+'\n')
    f1.close
    T_max=0
    
    
  
  if salida==1 and T_max<temp:
    T_max=temp
    
  print('time: '+dt + ' | '+'Temperature: {0:0.2F}°C'.format(temp)+' | salida: '+ str(salida)+' | Tmax: ' + str(T_max))
  f.write(str(dt)+', {0:0.2F}'.format(temp)+', '+str(salida)+', '+str(T_max))
  f.write('\n')
  f.close()
 # print(str(temp-temp_pas2))
  temp_pas2=temp_pas1;
  temp_pas1=temp_pas;
  temp_pas=temp;
  tiempo1=datetime.now()-tiempo
  #print(tiempo1)
  tiempo2=datetime.now()
#############################################################  
  client = InfluxDBClient(host='localhost', port=8086, database='Purga_caldera')
  tiempo3=datetime.now()-tiempo2
  #print(tiempo3)
  tiempo4=datetime.now()
  json_payload = [{
          "measurement": "Temperatura",
          "tags": {
              "Caldera": "1",
          },
          "time": dt,
          "fields": {
              "T": temp,
              "indicador": 100*salida,
              
          }
      },
      {
  "measurement": "Tiempo_purga",
  "tags": {
    "Caldera": "1",
    },
    "time": dt,
    "fields": {
      "Temperatura_maxima": T_max2, 
      "hora_inicio": dt1.hour,
      "minuto_inicio": dt1.minute,
      "segundo_inicio": dt1.second, 
      "hora_termino": dt2.hour,
      "minuto_termino": dt2.minute,
      "segundo_termino": dt2.second, 
                     
      }
    }]

  
  
  try:
    client.write_points(json_payload, database='Purga_caldera', batch_size=10000, protocol='json', time_precision = 'ms')
  
  #except InfluxDBClientError as e:
   # print(e.code)
    
  tiempo5=datetime.now()-tiempo4
  #print(tiempo2)
  f2=open('/home/ubuntu/Gasco/tiempos.txt','a')
  f2.write('Tiempo calculos: ' + str(tiempo1)+' | Tiempo conexion ifluxdb: '+str(tiempo3) + ' | Tiempo guardado: '+str(tiempo5)+'\n')
  f2.close
  n=n+1
  time.sleep(0.4)