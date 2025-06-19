from socket import *
import time, os
import json
from typing import Tuple, List, Dict
from Robot_11 import *
from threading import *
from mrpiZ_lib import *

class Classe_Serveur:

    # Définition des constantes pour les directions et vitesses
    A_GAUCHE: int = 1
    A_DROITE: int = -1

    AVANT: int = 0
    ARRIERE: int = 1
    ARRET: int = 0

    VITESSE_MAX: int = 100
    VITESSE_MIN: int = 25
    VITESSE_STOP: int = 0

    def __init__(self):
        """
        Initialise les attributs nécessaires pour le serveur et le contrôle du robot.
        Définit les paramètres de vitesse et initialise les capteurs et moteurs du robot.
        """
        # Variables pour la gestion des sockets
        self.socket_ecoute: socket
        self.port_ecoute: int
        self.socket_echange: socket
        self.msg_client: str
        self.msg_serveur: str
        self.tab_octets: bytearray
        self.addr_client: tuple[str, int]
        
        # Variables pour le contrôle du robot
        self.deplacement: Robot_deplacement
        self.fin: bool
        self.vitesse_gauche: int
        self.vitesse_droite: int
        self.vitesse_g_stop: int
        self.vitesse_d_stop: int
        self.sens_gauche: int
        self.sens_droit: int

        # Initialisation des vitesses
        self.vitesse_gauche = self.VITESSE_MAX
        self.vitesse_droite = self.VITESSE_MAX
        self.vitesse_g_stop = self.VITESSE_STOP
        self.vitesse_d_stop = self.VITESSE_STOP

        # Initialisation des autres attributs
        self.deplacement = Robot_deplacement()
        self.port_ecoute = 5000  # Port d'écoute pour le serveur
        self.fin = False  # Indicateur pour arrêter le serveur

    def demarrer_serveur(self):
        """
        Démarre le serveur en écoutant sur le port spécifié.
        Accepte une connexion client et traite les messages reçus pour contrôler le robot.
        Les messages clients peuvent être des commandes de mouvement ou un signal pour terminer.
        """
        # Création et configuration du socket d'écoute
        self.socket_ecoute = socket(family=AF_INET, type=SOCK_STREAM)
        self.socket_ecoute.bind(("", self.port_ecoute))  # Écoute sur toutes les adresses disponibles
        self.socket_ecoute.listen(1)
        print("serveur echo en écoute sur le port", self.port_ecoute)
        try:
            # Attente d'un client distant
            print("... en attente d'un client ...")
            self.socket_echange, self.addr_client = self.socket_ecoute.accept()
            print("nouveau client", self.addr_client)
            while not self.fin:
                # Réception d'un message du client
                self.tab_octets = self.socket_echange.recv(1024)
                self.msg_client = self.tab_octets.decode(encoding="utf-8")
                if self.msg_client == "fin":
                    self.fin = True  # Fin de la communication si le client envoie "fin"
                print("message du client :", self.msg_client)
                
                # Préparation du message du serveur (simple écho pour le moment)
                self.msg_serveur = f"//{self.msg_client}//"

                try:
                    # Lecture des valeurs des capteurs
                    p1 = proxSensor(2)
                    p2 = proxSensor(3)
                    p3 = proxSensor(4)
                    print(p1, p2, p3)  # Affichage des valeurs des capteurs
                except KeyboardInterrupt:
                    pass

                # Gestion du mouvement en fonction des capteurs
                self.gerer_mouvement(p1, p2, p3)

                # Récupération des vitesses des moteurs
                gauche = self.deplacement.motorLeftSpeed()
                droite = self.deplacement.motorRightSpeed()

                # Préparation du message contenant les informations des capteurs et moteurs
                liste_dict = list()
                liste_dict.append({"capteurs": [p1, p2, p3],
                                   "vitesse gauche": gauche,
                                   "vitesse droite": droite,
                                   "touche detecte": self.msg_serveur})
                self.msg_serveur = json.dumps(liste_dict)

                # Envoi du message au client
                self.tab_octets = self.msg_serveur.encode(encoding="utf-8")
                self.socket_echange.send(self.tab_octets)

            # Fin de la communication avec le client
            print("dernier message du client :", self.socket_echange.recv(255).decode(encoding="utf-8"))
        except KeyboardInterrupt:
            pass
        finally:
            # Fermeture des sockets
            self.socket_ecoute.close()
            self.socket_echange.close()

    def gerer_mouvement(self,p1,p2,p3):
        """
        Gère le mouvement du robot en fonction des capteurs de proximité et des commandes du client.
        
        Args:
            p1 (int): Valeur du capteur de proximité 1.
            p2 (int): Valeur du capteur de proximité 2.
            p3 (int): Valeur du capteur de proximité 3.
        
        Les commandes possibles incluent :
        - 'z': Avancer
        - 's': Reculer
        - 'd': Tourner à droite
        - 'q': Tourner à gauche
        - 'x': Arrêter
        Les mouvements sont ajustés en fonction des obstacles détectés par les capteurs.
        """

        # Indicateurs pour les mouvements en fonction des obstacles détectés
        deplacement = p2 > 100
        deplacementd = p1 > 100
        deplacementg = p3 > 100

        # Gestion des commandes du client
        if self.msg_client == "z" and deplacement:
            # Avancer
            self.sens_gauche = self.AVANT
            self.sens_droit = self.AVANT
            self.deplacement.motorLeft(self.sens_gauche, self.vitesse_gauche)
            self.deplacement.motorRight(self.sens_droit, self.vitesse_droite)
        elif self.msg_client == "s":
            # Reculer
            self.sens_gauche = self.ARRIERE
            self.sens_droit = self.ARRIERE
            self.deplacement.motorLeft(self.sens_gauche, self.vitesse_gauche)
            self.deplacement.motorRight(self.sens_droit, self.vitesse_droite)
        elif self.msg_client == "d" and deplacementg:
            # Tourner à droite
            self.sens_gauche = self.AVANT
            self.sens_droit = self.ARRIERE
            self.deplacement.motorLeft(self.sens_gauche, self.vitesse_gauche)
            self.deplacement.motorRight(self.sens_droit, self.vitesse_droite)
        elif self.msg_client == "q" and deplacementd:
            # Tourner à gauche
            self.sens_gauche = self.ARRIERE
            self.sens_droit = self.AVANT
            self.deplacement.motorLeft(self.sens_gauche, self.vitesse_gauche)
            self.deplacement.motorRight(self.sens_droit, self.vitesse_droite)
        elif self.msg_client == "x":
            # Arrêter
            self.sens_gauche = self.ARRET
            self.sens_droit = self.ARRET
            self.deplacement.motorLeft(self.sens_gauche, self.vitesse_g_stop)
            self.deplacement.motorRight(self.sens_droit, self.vitesse_d_stop)

if __name__ == "__main__":
    # Création et démarrage du serveur
    serveur = Classe_Serveur()
    serveur.demarrer_serveur()