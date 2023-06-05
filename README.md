# Telekinator

![Telekinator](/Imatges/ResultatsFinals/Final1.jpg)

## Continguts
- [Introducció](#introducció)
- [Requeriments](#requeriments)
- [Components](#components)
- [Esquema Hardware](#esquema-hardware)
- [Esquema Software](#esquema-software)
- [Resultats finals](#resultats-finals)
  - [Vídeo demo](#vídeo-demo)
- [Autors](#autors)
### Accessos ràpids
- [Models](/Models)
- [Codi](/codi)
  - [Local](/codi/local)
  - [Maquina Virtual](/codi/maquinaVirtual)
  - [Raspberry](/codi/raspberry)
- [Imatges](/Imatges)
  - [Esquemes](/Imatges/Esquemes)
  - [Models](Imatges/Models)
  - [Resultats Finals](/Imatges/ResultatsFinals)
- [Documentacio](/documentacio)

## Introducció
L'objectiu principal d'aquest projecte és desenvolupar un cotxe teledirigit que es pugui controlar mitjançant el seguiment ocular. La finalitat és proporcionar una solució de mobilitat per a persones que tenen dificultats per controlar el cotxe utilitzant les mans, com aquelles amb discapacitats físiques. Per aconseguir això, es faran servir tecnologies de seguiment ocular i sistemes de control de moviment per traduir els moviments oculars de l'usuari en senyals de moviment per al cotxe.

El cotxe teledirigit es mourà utilitzant una càmera que es troba al cotxe i una altra en un portàtil. L’usuari podrà veure la vista en primera persona del cotxe, i a través de la càmera del portàtil, controlar el moviment del cotxe mitjançant moviments oculars específics. Per exemple, si l'usuari mira cap a la dreta, el cotxe es mourà cap a la dreta. A més, el cotxe comptarà amb un sistema de detecció de proximitat per evitar col·lisions i garantir la seguretat de l'usuari i del cotxe.

El projecte requerirà habilitats de programació i coneixements de tecnologies de seguiment ocular i sistemes de control de moviment per desenvolupar un programari que tradueixi els moviments oculars de l’usuari en senyals de moviment per al cotxe. El resultat final serà un cotxe teledirigit innovador i fàcil de controlar per a aquells que prefereixen fer servir la mirada en lloc d'un control remot convencional, especialment per a aquells amb discapacitats físiques que els impedeixin controlar el cotxe d'una altra manera.
## Requeriments
Les llibreries necessàries per aquest projecte son:
- [Google cloud storage](https://pypi.org/project/google-cloud-storage/)
- [Mediapipe](https://pypi.org/project/mediapipe/)
- [RPi.GPIO](https://pypi.org/project/RPi.GPIO/)
- [OpenCV](https://pypi.org/project/opencv-python/)
- [Numpy](https://numpy.org/install/)
## Components
-	1 Raspberry pi 3 model B v1.2
-	1 Sensor d’ultrasons HC-SR04
-	4 Micro Motors DC
-	1 Controladora de motor L298N
-	1 Càmera per raspberry pi 3 model B v1.2
-	1 Tarjeta MicroSD
-	4 Piles 1,5V
-	1 Portapiles (4 piles)
-	1 Batería 5V
-	1 Cable batería
## Esquema Hardware
![EsquemaHardware](/Imatges/Esquemes/EsquemaHardware.png)
- Portapiles i 4 piles de 1,5V connectats al positiu (VCC) i negatiu (GND) de la controladora L298N
- GND de la controladora connectat a un GND de la raspberry.
- 2 motors connectats en paral·lel a les sortides out1 i out2 de la controladora.
- 2 motors connectats en paral·lel a les sortides out3 i out4 de la controladora.
- Entrades In1, In2, In3, In4, EnA, EnB de la controladora connectats als pins GPIO 24, 23, 17, 27, 25 i 22 de la raspberry respectivament.
- Pins de trigger i echo del sensor d’ultrasons (hc-sr04) connectats als pins GPIO 5 i 18 de la raspberry respectivament.
- Pins de GND i VCC del sensor d’ultrasons connectats a un pin de GND i VCC de la raspberry.
## Esquema Software
![EsquemaSoftware](/Imatges/Esquemes/EsquemaSoftware.png)
- Mòdul Eye-tracker: Aquest mòdul és l’encarregat de reconèixer l’acció que ha de fer el cotxe segons el moviment ocular. Primer, el que es rep per la càmera es puja al Google Cloud Storage, després, dins d’una màquina virtual de Google, descarreguem l’últim frame pujat y utilitzem una funció eyetracker que farà el reconeixement facial del frame, reconeixerà la posició dels ulls, també la direcció de la mirada, interpretarà la direcció i la convertirà en l’acció que farà el cotxe teledirigit, la qual la pujarà al Cloud Storage.

- Mòdul Sensor: Aquest mòdul es l’encarregat de evitar les col·lisions del cotxe amb l’entorn. Primer es rep el que capta en sensor, després es reconeix la distància que separa el cotxe de l’obstacle i es fa una interpretació per donar una acció al cotxe.

- Mòdul Acció: Aquest mòdul és l’encarregat de fer que el cotxe faci l’acció donada. Primer, es fixa en l’ordre enviat per el mòdul sensor, si l’ordre es parar-se a causa d’un obstacle, el cotxe es pararà y no farà res més, però en cas contrari, es descarregarà l’acció de enviada pel mòdul Eye-tracker y el cotxe farà l’acció donada.
## Resultats finals
![Telekinator1](/Imatges/ResultatsFinals/Final1.jpg)
![Telekinator2](/Imatges/ResultatsFinals/Final2.jpg)
### Vídeo demo
[![Vídeo demo](https://img.youtube.com/vi/ZdBP9RJG0WA/0.jpg)](https://youtube.com/watch?v=ZdBP9RJG0WA)

## Autors
Raul Ochoa

Jheremmy Matienzo

Oriol Cano
