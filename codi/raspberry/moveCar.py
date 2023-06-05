import os
from google.cloud import storage
import time
import pickle
import RPi.GPIO as GPIO

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'key_googleStorage.json'

# ultrasonidos
# Configuración de los pines GPIO
GPIO.setmode(GPIO.BCM)
GPIO_TRIGGER = [5]  # Pines TRIG de los sensores
GPIO_ECHO = [18]  # Pines ECHO de los sensores
DISTANCIA_MINIMA = 20  # Distancia mínima para generar la notificación
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

def pickle_exist(nombre_archivo):
    archivos = os.listdir('.')
    if nombre_archivo in archivos:
        return True
    else:
        return False


def delete_old_pickle(actual_frame):
    for archivo in os.listdir(os.getcwd()):
        if archivo.startswith("dir") and archivo != actual_frame:
            ruta_completa = os.path.join(os.getcwd(), archivo)
            os.remove(ruta_completa)

def medir_distancia(sensor_index):
    # Enviar un pulso ultrasónico para el sensor especificado
    GPIO.output(GPIO_TRIGGER[sensor_index], True)
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER[sensor_index], False)

    # Registrar el tiempo de inicio y finalización del eco
    start_time = time.time()
    end_time = time.time()

    while GPIO.input(GPIO_ECHO[sensor_index]) == 0:
        start_time = time.time()

    while GPIO.input(GPIO_ECHO[sensor_index]) == 1:
        end_time = time.time()

    # Calcular la duración del eco
    duration = end_time - start_time

    # Calcular la distancia (velocidad del sonido: 34300 cm/s)
    distance = (duration * 34300) / 2

    return distance

def main():
    client = storage.Client()

    #incializar cosas de los motores
    in1 = 24
    in2 = 23
    en = 25
    in3 = 17
    in4 = 27
    enB = 22
    temp1 = 1

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(in1, GPIO.OUT)
    GPIO.setup(in2, GPIO.OUT)
    GPIO.setup(en, GPIO.OUT)
    GPIO.output(in1, GPIO.LOW)
    GPIO.output(in2, GPIO.LOW)
    GPIO.setup(in3, GPIO.OUT)
    GPIO.setup(in4, GPIO.OUT)
    GPIO.setup(enB, GPIO.OUT)
    GPIO.output(in3, GPIO.LOW)
    GPIO.output(in4, GPIO.LOW)

    p = GPIO.PWM(en, 1000)
    p2 = GPIO.PWM(enB, 1000)
    p.start(75)
    p2.start(25)

    cont_stop = 0



    while True:
        try:
            #while True:
            for i in range(1):
                distancia = medir_distancia(i)
                print("Distancia del sensor %d: %.2f cm" % (i + 1, distancia))
                if distancia < DISTANCIA_MINIMA:
                    print("¡Alerta! Distancia inferior a %d cm detectada por el sensor %d" % (
                    DISTANCIA_MINIMA, i + 1))
                    GPIO.output(in1, GPIO.LOW)
                    GPIO.output(in2, GPIO.LOW)
                    GPIO.output(in3, GPIO.LOW)
                    GPIO.output(in4, GPIO.LOW)
            time.sleep(1)

        except KeyboardInterrupt:
            print("Programa interrumpido por el usuario")
        #finally:
            #GPIO.cleanup()

        if distancia > DISTANCIA_MINIMA:
            inicioT = time.time()
            bucket = client.get_bucket("eyetrackerimg")
            blobs = bucket.list_blobs(prefix="mov/")
            for blob in blobs:
                lastDir = blob.name.replace("mov/", '')
            if pickle_exist(lastDir):
                continue
            blob = bucket.blob(f'mov/{lastDir}')
            blob.download_to_filename(f'{lastDir}')
            delete_old_pickle(lastDir)

            with open(lastDir, 'rb') as archivo:
                x = pickle.load(archivo)

            print("DIR:", dir)
            print("tiempo TOTALLLLLL:", time.time() - inicioT)

            if x == 'CENTER':
                print("run")
                p.ChangeDutyCycle(75)  # velocidad l=25 m=50 h=75
                p2.ChangeDutyCycle(25)
                if (temp1 == 1):
                    GPIO.output(in1, GPIO.HIGH)
                    GPIO.output(in2, GPIO.LOW)
                    GPIO.output(in3, GPIO.HIGH)
                    GPIO.output(in4, GPIO.LOW)
                    print("forward")
                    x = 'z'

            elif x == 'STOP':
                cont_stop += 1
                if cont_stop >= 2:
                    print("stop")
                    GPIO.output(in1, GPIO.LOW)
                    GPIO.output(in2, GPIO.LOW)
                    GPIO.output(in3, GPIO.LOW)
                    GPIO.output(in4, GPIO.LOW)
                x = 'z'
            else:
                if cont_stop > 0:
                    cont_stop -= 1
                if x == 'CENTER':
                    print("forward")
                    GPIO.output(in1, GPIO.HIGH)
                    GPIO.output(in2, GPIO.LOW)
                    GPIO.output(in3, GPIO.HIGH)
                    GPIO.output(in4, GPIO.LOW)
                    temp1 = 1
                    x = 'z'

                elif x == 'BACKWARDS':
                    print("backward")
                    GPIO.output(in1, GPIO.LOW)
                    GPIO.output(in2, GPIO.HIGH)
                    GPIO.output(in3, GPIO.LOW)
                    GPIO.output(in4, GPIO.HIGH)

                    temp1 = 0
                    x = 'z'
                elif x == 'RIGHT':  # contando que in1 y in2 controlan los motores de la izquierda
                    print("right")
                    p.ChangeDutyCycle(100)
                    p2.ChangeDutyCycle(5)  # motores de la derecha giran mas lento para girar el coche
                    GPIO.output(in2, GPIO.LOW)
                    GPIO.output(in1, GPIO.HIGH)
                    GPIO.output(in4, GPIO.LOW)
                    GPIO.output(in3, GPIO.HIGH)

                elif x == 'LEFT':  # contando que in1 y in2 controlan los motores de la izquierda
                    print("left")
                    p.ChangeDutyCycle(5)  # motores de la izquierda giran mas lento para girar el coche
                    p2.ChangeDutyCycle(100)
                    GPIO.output(in2, GPIO.LOW)
                    GPIO.output(in1, GPIO.HIGH)
                    GPIO.output(in4, GPIO.LOW)
                    GPIO.output(in3, GPIO.HIGH)
                else:
                    GPIO.cleanup()
                    print("<<<  wrong data  >>>")
                    break

            """elif x == 'l':
                print("low")
                p.ChangeDutyCycle(25)
                x = 'z'
    
            elif x == 'm':
                print("medium")
                p.ChangeDutyCycle(50)
                x = 'z'
    
            elif x == 'h':
                print("high")
                p.ChangeDutyCycle(75)
                x = 'z'"""



if __name__ == '__main__':
    main()
