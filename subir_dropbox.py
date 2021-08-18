import sched
import dropbox
import random
import time
from datetime import datetime

scheduler = sched.scheduler(time.time, time.sleep)



#Sube archivo
def subir_archivo():
  dt = datetime.utcnow().isoformat(sep=' ', timespec='milliseconds')
  #Autenticaci0on
  token = "EyEi1WNUbhMAAAAAAAAAAZs1d6Bu-WWhlsciraFg0QM0dxqwybK7fDbvWg5hqf4B"
  dbx = dropbox.Dropbox(token)

  #Obtiene y muestra la informacion del usuario
  user = dbx.users_get_current_account()
  #print(user)
  with open("temperatura.txt", "rb") as f:
    dbx.files_upload(f.read(), '/temperatura-'+dt+'.txt', mute = True)

  #crear achivo de buffet
  f=open('temperatura.txt','w')
  f.close
  #
  #print('time: '+dt)

subir_archivo()
while True:
  scheduler.enter(300, 1, subir_archivo)
  scheduler.run()
