#!/usr/bin/python
import time
import Adafruit_GPIO.SPI as SPI
import MAX6675.MAX6675 as MAX6675
from datetime import datetime
from influxdb import InfluxDBClient
import queue
import threading
import numpy as np
from scipy import interpolate


# Configuracion de pines SPI en la rasberry
CLK = 25
CS  = 24
DO  = 18
sensor = MAX6675.MAX6675(CLK, CS, DO)


#funcion para determinar la perdida de energia
def Q_loss(T,f_cp,rho,A,u,Tb):
  dot_m = rho*A*u
  dot_Q = dot_m*f_cp(T)*((T+273.15)-Tb)/1000 # kW
  return dot_m, dot_Q

## funcion que permite leer el sensor de temperatura y realizar los calculos de inicio y termino de la purga.
def leer_sensor(C_temp,C_tiem,C_tiem1,C_tiem2,C_tempmax,C_salida,f_cp,rho,A,u,Tb,C_dotm,C_dotQ,C_dotmT,C_dotQT):
  #DEfinicion de variables iniciales
  temp_pas2=200
  temp_pas1=200
  temp_pas=200
  tiempo_inicio=0
  tiempo_final=0
  salida=0
  T_max=0.0
  T_max2=100.0
  dotm_total=0.0
  dotq_total=0.0
  dotm_total2=0.0
  dotq_total2=0.0
  dt1=datetime.now()
  dt2=datetime.now()
  n=0
  while True:
    #Lectura de sensor y tiempo de lectura
    temp = sensor.readTempC()
    dt = datetime.utcnow().isoformat(sep=' ', timespec='milliseconds')
    dt3=datetime.now()
    dot_m, dot_Q = Q_loss(temp,f_cp,rho,A,u,Tb)
    #ingreso a las colas
    C_temp.put(temp)
    C_tiem.put(dt)
    C_dotm.put(dot_m)
    C_dotQ.put(dot_Q)
    
    #calculos de inicio y termino de purga
    if salida==0 and (temp-temp_pas2)>7 and n>3:
      salida=1
      tiempo_inicio=dt
      dt0=datetime.now()
      dt4=dt0
    elif salida==1 and (temp-temp_pas2)<-1.5:
      salida=0
      tiempo_final=dt
      dt1=dt0
      dt2=datetime.now()
      dotm_total2=dotm_total*delta_t
      dotq_total2=dotq_total*delta_t
      T_max2=T_max
      f1=open('/home/ubuntu/Gasco/purga.txt','a')
      f1.write('Tiempo inicio: ' + str(tiempo_inicio)+' | Tiempo final: '+str(tiempo_final) + ' | Temperatura Maxima: '+str(T_max)+'\n')
      f1.close
      T_max=0.0
      dotm_total=0.0
      dotq_total=0.0
    
    #Calculo de temperatura maxima durante purga
    if salida==1 and T_max<temp:
      T_max=temp
    
    #Calculo de temperatura maxima durante purga
    if salida==1:
      delta_t=(dt3-dt4).total_seconds()
      if(delta_t>0):
        dotm_total=dotm_total+dot_m*delta_t
        dotq_total=dotq_total+dot_Q*delta_t
      dt4=dt3
      #print(dotm_total)
    
    #impresion de datos y escritura en archivo
    print('time: '+dt + ' | '+'Temperature: {0:0.2F}°C'.format(temp)+' | salida: '+ str(salida)+' | Tmax: ' + str(T_max))
    f=open('/home/ubuntu/Gasco/temperatura.txt','a')
    f.write(str(dt)+', {0:0.2F}'.format(temp)+', '+str(salida)+', '+str(T_max))
    f.write('\n')
    f.close()
    C_tiem1.put(dt1)
    C_tiem2.put(dt2)
    C_tempmax.put(T_max2)
    C_salida.put(salida)
    C_dotmT.put(dotm_total2)
    C_dotQT.put(dotq_total2)
    #actualizo lista de temperaturas pasadas
    temp_pas2=temp_pas1;
    temp_pas1=temp_pas;
    temp_pas=temp;
    n=n+1
    time.sleep(0.5)

#proceso que imprime los datos
def escribir_base_datos(C_temp,C_tiem,C_tiem1,C_tiem2,C_tempmax,C_salida,C_dotm,C_dotQ,C_dotmT,C_dotQT):
  while True:
    temperatura=C_temp.get()
    Tiempo=C_tiem.get()
    Tiempo_inicio_purga=C_tiem1.get()
    Tiempo_fin_purga=C_tiem2.get()
    temperatura_maxima=C_tempmax.get()
    salida=C_salida.get()
    Dot_m=C_dotm.get()
    Dot_Q=C_dotQ.get()
    Dot_mT=C_dotmT.get()
    Dot_QT=C_dotQT.get()
    #print(Dot_mT)
    #print('dot_m: '+str(Dot_m)+'dot_q: '+str(Dot_Q))
    client = InfluxDBClient(host='localhost', port=8086, database='Purga_caldera')
    json_payload = [{
          "measurement": "Temperatura",
          "tags": {
              "Caldera": "1",
          },
          "time": Tiempo,
          "fields": {
              "T": temperatura,
              "indicador": temperatura*salida,
              
          }
      },
      {
    "measurement": "Tiempo_purga",
    "tags": {
      "Caldera": "1",
        },
      "time": Tiempo,
      "fields": {
        "Temperatura_maxima": temperatura_maxima, 
        "hora_inicio": Tiempo_inicio_purga.hour,
        "minuto_inicio": Tiempo_inicio_purga.minute,
        "segundo_inicio": Tiempo_inicio_purga.second, 
        "hora_termino": Tiempo_fin_purga.hour,
        "minuto_termino": Tiempo_fin_purga.minute,
        "segundo_termino": Tiempo_fin_purga.second, 
                     
      }
    },
     {
    "measurement": "Perdida_purga",
    "tags": {
      "Caldera": "1",
        },
      "time": Tiempo,
      "fields": {
        "Masa de agua": Dot_m*salida, 
        "Energia perdida": Dot_Q*salida,
        "Masa de agua total": Dot_mT, 
        "Energia perdida total": Dot_QT,                  
      }
    }]
    
    try:
      client.write_points(json_payload, database='Purga_caldera', batch_size=10000, protocol='json', time_precision = 'ms')
    
    except(InfluxDBClientError, InfluxDBServerError):
      logger.exception('Failed to send metrics to influxdb') 
     
     
    time.sleep(0.2)
#seccion principal del codigo
#calculo para obtener curva cp
with open('/home/ubuntu/Gasco/cp_H2O.npy', 'rb') as f:
    Temps = np.load(f)
    cp    = np.load(f)
    f_cp   = interpolate.interp1d(Temps,cp)

#variables asociadas al calculo de energia
one_atm= 101325.0
D      = 20e-2              # Diameter of the exit pipe, m
A      = np.pi*D**2/4
Tb     = 273.15 + 20 # estimate temperature inside boiler
Pb     = 1.01*one_atm  # pressure inside boiler
Pout   = 1*one_atm
rho    = 1000.0 # 
# u      = 1 # m/s (typical) Change this for a model depending on the data
u      = np.sqrt(2*(Pb-Pout)/rho)   # this velocity will depend on the conditions of the boiler T and P. Check this
   
#crear achivos de buffet
f=open('/home/ubuntu/Gasco/temperatura.txt','w')
f.close
f1=open('/home/ubuntu/Gasco/purga.txt','w')
f1.close
f2=open('/home/ubuntu/Gasco/tiempos.txt','w')
f2.close

#colas de almacenamiento de datos
Cola_temperatura = queue.Queue()
Cola_tiempo = queue.Queue()
Cola_tiempo_pinit = queue.Queue() 
Cola_tiempo_pfin = queue.Queue()
Cola_temperatura_max = queue.Queue()
Cola_salida = queue.Queue()
Cola_dotm = queue.Queue()
Cola_dotq = queue.Queue()
Cola_dotmT = queue.Queue()
Cola_dotqT = queue.Queue()

hilo1 = threading.Thread(name='leer_sensor', 
                         target=leer_sensor,
                         args=(Cola_temperatura,Cola_tiempo,Cola_tiempo_pinit,Cola_tiempo_pfin,Cola_temperatura_max,Cola_salida,f_cp,rho,A,u,Tb,Cola_dotm,Cola_dotq,Cola_dotmT,Cola_dotqT),
                         daemon=True)

hilo2 = threading.Thread(name='escribir_base_datos',
                         target=escribir_base_datos,
                         args=(Cola_temperatura,Cola_tiempo,Cola_tiempo_pinit,Cola_tiempo_pfin,Cola_temperatura_max,Cola_salida,Cola_dotm,Cola_dotq,Cola_dotmT,Cola_dotqT))
hilo1.start()
hilo2.start()




  