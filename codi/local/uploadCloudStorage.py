import os
from google.cloud import storage
import time
import cv2

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'key_googleStorage.json'


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

# Función principal que llama a las demás, captura la camara y sube 1 de cada 5 frames al cloud storage
def uploadFrames():
    bucket_name = "eyetrackerimg"
    directory = "img/"
    client = storage.Client()
    delete_blobs(client, bucket_name, directory)
    count = 0
    frameCount = 0
    cap = cv2.VideoCapture(0)
    inicio = time.time()
    while True:
        _, frame = cap.read()

        if count % 5 == 0:
            source_file_name = f"frame{str(frameCount).zfill(5)}.jpg"
            cv2.imwrite(source_file_name, frame)
            frameCount += 1
            destination_blob_name = directory + source_file_name
            upload_blob(client, bucket_name, source_file_name, destination_blob_name)
            print(time.time() - inicio)
            inicio = time.time()

        cv2.imshow('Video', frame)
        count += 1

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    delete_frames_directory(os.getcwd(), "frame")

if __name__ == '__main__':
    uploadFrames()
