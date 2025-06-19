#!/usr/bin/python
# NGUYEN Anh Quan
# SEVESTRE HUGO
# 2B1


#3,7 V == 100%
#
from math import*

import serial
import time
import os

class Robot_deplacement:

    def __init__(self):
        self.__port = serial.Serial('/dev/ttyAMA0', 230400)
        # Tension maximale de la batterie (100%)
        self.max_voltage = 3.7
        # Tension minimale de la batterie (0%)
        self.min_voltage = 2.5
        
    def writeCommand(self,command):
        self.__port.write(b'#')
        self.__port.write(command)
        self.__port.write(b'!')
        
    def readData(self):
        chaine = self.__port.readline()
        pos1 = chaine.find(b'$')
        pos2 = chaine.find(b'\n')
        chaine = chaine[pos1+1:pos2]
        return chaine

    def forward(self,speed):
        """
                move forward mrpi1
                parameter : 0 to 100
                Exemple:
                >> forward(20)
        """
        if speed > -1 and speed < 101:
            speed = str(speed)
            self.__port.write(b"#MF,")
            speed = bytes(speed, 'utf-8')
            self.__port.write(speed)
            self.__port.write(b"!")
        else:
            print("error speed value")

    def motorRight(self, direction, speed):
        """
        motor right control
        parameter 1 : direction (0 or 1)
        parameter 2 : speed ( 0 to 100)     
        Exemple:
        >> motorRight(1, 50)
        """
        dir = bytes(str(direction), 'utf-8')
        pwm = bytes(str(speed), 'utf-8')
        self.__port.write(b"#MOTR,")
        self.__port.write(dir)
        self.__port.write(b",")
        self.__port.write(pwm)
        self.__port.write(b"!")

    def motorLeft(self, direction, speed):
        """
                motor left control
                parameter 1 : direction (0 or 1)
                parameter 2 : speed ( 0 to 100)     
                Exemple:
                >> motorLeft(1, 50)
        """
        dir = bytes(str(direction), 'utf-8')
        pwm = bytes(str(speed), 'utf-8')
        self.__port.write(b"#MOTL,")
        self.__port.write(dir)
        self.__port.write(b",")
        self.__port.write(pwm)
        self.__port.write(b"!")

    # retourne la vitesse du moteur gauche
    def motorLeftSpeed(self):
        liste = []
        value = 0
        self.__port.flushInput() # reset serial receive buffer
        self.writeCommand(b"MLS")
        value = self.readData()
        value = float(value) 
        return (value)
    
    # retourne la vitesse du moteur droit
    def motorRightSpeed(self):
        liste = []
        value = 0
        self.__port.flushInput() # reset serial receive buffer
        self.writeCommand(b"MRS")
        value = self.readData()
        value = float(value) 
        return (value)
    
    def motorsDisable(self):
        self.writeCommand(b"MDI")

    # retourne le volt initial
    def battery(self):
        """
            Read battery tension
            return le pourcentage restant
            faire un produit en croix afin de posséder le pourcentage restant dans le robot
            exemple: 
            ici 100% = 3.7 volts
            la fonction nous retourne 2.7 volts
            le pourcentage est de 72.97%
            Exemple:
            >> battery()
            faire une fonction while qui permet d'appeler la fonction à chaque fois arondire la valeur à un entier sur une interfaces ihm
            avec un time.sleep(1) entre chaque appelle de la fonction

        """
        # liste = []
        # value = 0
        # fin : bool = False
        # while not fin:
        #     time.sleep(1)
        #     self.__port.flushInput() # reset serial receive buffer
        #     self.writeCommand(b"BAT")
        #     value = self.readData()
        #     pourcentage_restant = ((100*float(value))/3.7)
        #     if pourcentage_restant <= 10:
        #         fin = True
        #     print(int(pourcentage_restant))
        # msg = f'il reste moins de {int(pourcentage_restant)}% il faut le recharger vite '
        # return msg

        while True:
            # Lecture de la tension
            voltage = self.read_voltage()
            # Calcul du pourcentage
            percentage = ((voltage - self.min_voltage) / (self.max_voltage - self.min_voltage)) * 100
            # Assure que le pourcentage est entre 0 et 100
            percentage = max(0, min(100, percentage))
            # Affichage du pourcentage arrondi
            print(f"Batterie restante: {round(percentage)}%")
            # Délai de 1 seconde avant la prochaine lecture
            time.sleep(1)