import os
from google.cloud import storage
import time
import cv2
import funcEyetracker
import pickle

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'key_googleStorage.json'

# Función que descarga archivos de un bucket del cloud storage
def download_blob(storage_client, nombre_bucket, ruta_foto_en_bucket, ruta_local):
    #storage_client = storage.Client()
    bucket = storage_client.get_bucket(nombre_bucket)
    blob = bucket.blob(ruta_foto_en_bucket)
    blob.download_to_filename(ruta_local)

# Función que cuenta cuantos archivos hay con el prefijo frame en el bucket
def frame_count(client, bucket_name, directorio):
    #client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=directorio)
    count = 0
    for blob in blobs:
        if not blob.name.endswith('/'):
            count += 1

    return count

# Función que comprueba si un frame ya existe en el directorio actual
def frame_exist(nombre_archivo):
    archivos = os.listdir('.')
    if nombre_archivo in archivos:
        return True
    else:
        return False

# Función que borra el frame anterior
def delete_old_frame(actual_frame):
    for archivo in os.listdir(os.getcwd()):
        if archivo.startswith("frame") and archivo != actual_frame:
            ruta_completa = os.path.join(os.getcwd(), archivo)
            os.remove(ruta_completa)

# Función que interpreta la acción del coche dependiendo de las direcciones de los ojos
def accion(eyePositionRight, eyePositionLeft):
    if eyePositionRight == 'CENTER':
        if eyePositionLeft == 'CENTER':
            dir = 'CENTER'
        elif eyePositionLeft == 'RIGHT':
            dir = 'RIGHT'
        elif eyePositionLeft == 'LEFT':
            dir = 'LEFT'
        elif eyePositionLeft == 'CLOSED':
            dir = 'BREAK'

    elif eyePositionRight == 'RIGHT':
        if eyePositionLeft == 'CENTER':
            dir = 'RIGHT'
        elif eyePositionLeft == 'RIGHT':
            dir = 'RIGHT'
        elif eyePositionLeft == 'LEFT':
            dir = 'CENTER'
        elif eyePositionLeft == 'CLOSED':
            dir = 'BREAK'

    elif eyePositionRight == 'LEFT':
        if eyePositionLeft == 'CENTER':
            dir = 'LEFT'
        elif eyePositionLeft == 'RIGHT':
            dir = 'CENTER'
        elif eyePositionLeft == 'LEFT':
            dir = 'LEFT'
        elif eyePositionLeft == 'CLOSED':
            dir = 'BREAK'

    elif eyePositionRight == 'CLOSED':
        if eyePositionLeft == 'CLOSED':
            dir = 'STOP'
        else:
            dir = 'BACKWARDS'

    return dir

# Función que sube archivos a un bucker del cloud storage
def upload_blob(storage_client, bucket_name, source_file_name, destination_blob_name):

    #storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)

    print(f"Archivo {source_file_name} cargado como {destination_blob_name} en el bucket {bucket_name}.")

# Función que vacía el contenido del bucket
def delete_blobs(client, bucket_name, directorio):
    #client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=directorio)
    inicio = time.time()
    for blob in blobs:
        if not blob.name.endswith('/'):
            blob.delete()

    print("TIEMPO:", time.time() - inicio)
    print(f"Se han borrado todos los objetos en el directorio {directorio} del bucket {bucket_name}.")

# Función que borra todos los archivos que empiecen por un prefijo en el directorio que se le pasa por parámetro
def delete_frames_directory(directorio, prefijo):
    for archivo in os.listdir(directorio):
        if archivo.startswith(prefijo):
            ruta_completa = os.path.join(directorio, archivo)
            os.remove(ruta_completa)

    print(f"Frames eliminados en el directorio: {directorio}")

# Función que borra todos los archivos de tipo pickle
def delete_pickles(prefix):
    for archivo in os.listdir(os.getcwd()):
        if archivo.startswith(prefix):
            ruta_completa = os.path.join(os.getcwd(), archivo)
            os.remove(ruta_completa)


def delete_pickles_bucket(client, bucket_nombre, directorio, archivo_a_mantener):
    #client = storage.Client()
    bucket = client.get_bucket(bucket_nombre)
    blobs = bucket.list_blobs(prefix=directorio)

    for blob in blobs:
        if blob.name != directorio + archivo_a_mantener:
            blob.delete()




# Función principal descarga el último frame, obtiene la acción que ha de realizar el coche y la sube al google storage
def main():
    bucket_name = "eyetrackerimg"
    directory = "mov/"
    client = storage.Client()
    delete_blobs(client, bucket_name, directory)
    fileCount = 0
    while True:
        lastFrameCount = frame_count(client, "eyetrackerimg", "img/") - 1
        lastFrame = f"frame{str(lastFrameCount).zfill(5)}.jpg"
        if frame_exist(lastFrame):
            continue

        download_blob(client, 'eyetrackerimg', f'img/{lastFrame}', f'{lastFrame}')
        delete_old_frame(lastFrame)
        frame = cv2.imread(lastFrame)
        # frame = np.array(frame)
        eyePositionRight, eyePositionLeft = funcEyetracker.eyeTracker(frame)
        print(f'RIGHT:{eyePositionRight},LEFT:{eyePositionLeft}')
        dir = accion(eyePositionRight, eyePositionLeft)
        print(dir)
        source_file_name = f"dir{str(fileCount).zfill(5)}.pickle"
        with open(f'./{source_file_name}', 'wb') as archivo:
            pickle.dump(dir, archivo)

        fileCount += 1
        destination_blob_name = directory + source_file_name
        upload_blob(client, bucket_name, source_file_name, destination_blob_name)
        delete_pickles_bucket(client, bucket_name, directory, source_file_name)
        delete_pickles('dir')


if __name__ == '__main__':
    main()
