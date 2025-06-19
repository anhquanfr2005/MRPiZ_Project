from tkinter import *
from socket import *
import time
from PIL import Image, ImageTk  # Assurez-vous d'avoir Pillow installé
import json
from typing import Tuple, List, Dict

class IHM_Robot11(Tk):
    def __init__(self):
        """
        Initialise l'interface graphique pour la commande du robot.
        """
        Tk.__init__(self)

        self.__client_tcp: IHM_Robot11

        # Partie connexion
        self.__fen_connexion: Frame
        self.__label_ip: Label
        self.__entree_ip_serveur: Entry
        self.__label_port: Label
        self.__entree_port_serveur: Entry
        self.__btn_connexion: Button

        # Partie message
        self.__fen_echange: Frame
        self.__entree_msg_client: Entry
        self.__btn_envoyer: Button
        self.__text_msg_serveur: Text

        # Partie commande
        self.__fen_commande: Frame
        self.__canvas: Canvas
        self.__canvas1: Canvas

        # instanciation
        # Partie connexion
        self.title('IHM Robot11')
        self.__fen_connexion = Frame(self, borderwidth=10, relief="groove")
        self.__label_ip = Label(self.__fen_connexion, text="ip serveur")
        self.__entree_ip_serveur = Entry(self.__fen_connexion, width=15)
        self.__entree_ip_serveur.insert(index=0, string="10.15.141.1")
        self.__btn_connexion = Button(self.__fen_connexion, text="connexion", background="green", borderwidth=5, command=self.connexion)
        self.__label_port = Label(self.__fen_connexion, text="port serveur")
        self.__entree_port_serveur = Entry(self.__fen_connexion, width=10)
        self.__entree_port_serveur.insert(index=0, string="5000")

        self.__fen_connexion.grid(row=0, column=0, columnspan=2, pady=20, sticky=E + W)
        self.__btn_connexion.grid(row=0, column=2, sticky=W, padx=20)
        self.__label_ip.grid(row=0, column=0, padx=25, sticky=W)
        self.__entree_port_serveur.grid(row=1, column=1, sticky=W)
        self.__label_port.grid(row=1, column=0, padx=25, sticky=W)
        self.__entree_ip_serveur.grid(row=0, column=1, sticky=W)

        # Configurer la grille pour que les colonnes s'étendent
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)  # Ajout de la colonne 2 pour le bouton de connexion

        # Partie message
        self.__fen_echange = Frame(self, borderwidth=10, relief="groove")
        self.__text_msg_serveur = Text(self.__fen_echange, width=40, height=25, borderwidth=1)
        self.__entree_msg_client = Entry(self.__fen_echange, width=40, borderwidth=1)
        self.__btn_envoyer = Button(self.__fen_echange, text="envoyer", command=self.envoyer)

        self.__fen_echange.grid(row=1, column=0, sticky=N + S + E + W, padx=5)
        self.__entree_msg_client.grid(row=3, column=0, sticky=W)
        self.__btn_envoyer.grid(row=3, column=1, padx=10, sticky=W)
        self.__text_msg_serveur.grid(row=4, column=0, columnspan=2, sticky=W)
        self.__btn_envoyer.config(state=DISABLED)

        self.protocol("WM_DELETE_WINDOW", self.arret_via_X)

        # Partie commande
        self.__fen_commande = Frame(self, borderwidth=10, relief="groove")
        self.__fen_commande.grid(row=1, column=1, sticky=N + S + E + W, padx=20)

        # Création du Canvas pour les boutons ovales
        self.__canvas1 = Canvas(self.__fen_commande, width=300, height=100)
        self.__canvas1.grid(row=0, column=0, columnspan=10)

        # Dessiner les ovales pour les boutons Automatique et Manuel
        self.auto_button = self.__canvas1.create_oval(20, 20, 140, 80, fill='lightblue', outline='blue', tags="auto")
        self.manuel_button = self.__canvas1.create_oval(160, 20, 280, 80, fill='lightgreen', outline='green', tags="manuel")

        # Ajouter le texte sur les ovales
        self.__canvas1.create_text(80, 50, text="Automatique", font=("Arial", 12), tags="auto_text")
        self.__canvas1.create_text(220, 50, text="Manuel", font=("Arial", 12), tags="manuel_text")

        # Lier les événements de clic
        self.__canvas1.tag_bind("auto", "<Button-1>", self.auto_command)
        self.__canvas1.tag_bind("manuel", "<Button-1>", self.manuel_command)

        # Position initiale du robot
        self.robot_x = 150
        self.robot_y = 150

        # Charger l'image du robot
        self.robot_image = Image.open("robot.png")  # Remplacez par le chemin de votre image
        self.robot_image = self.robot_image.resize((35, 35), Image.LANCZOS)  # Redimensionner l'image
        self.robot_photo = ImageTk.PhotoImage(self.robot_image)

        # Création du Canvas pour afficher le robot
        self.__canvas = Canvas(self.__fen_echange, width=400, height=400, bg='white')
        self.__canvas.grid(row=4, column=3, columnspan=10, pady=15,padx=40)

        # Dessiner l'image du robot sur le Canvas
        self.robot_id = self.__canvas.create_image(self.robot_x, self.robot_y, image=self.robot_photo)

        # Autres boutons de commande
        self.__btn_haut = Button(self.__fen_commande, text="Haut", width=15, height=2,command=self.touche_avancer)
        self.__btn_bas = Button(self.__fen_commande, text="Bas", width=15, height=2,command=self.touche_reculer)
        self.__btn_droite = Button(self.__fen_commande, text="Droite", width=15, height=2,command=self.touche_droite)
        self.__btn_gauche = Button(self.__fen_commande, text="Gauche", width=15, height=2,command=self.touche_gauche)
        self.__btn_quitter = Button(self.__fen_commande, text="Quitter", background="red", command=self.quitter, width=15, height=2)
        self.__btn_arret = Button(self.__fen_commande, text="Arret", width=15, height=2,command=self.touche_arret)

        self.__btn_haut.grid(row=1, column=1, pady=15)
        self.__btn_bas.grid(row=2, column=1)
        self.__btn_droite.grid(row=2, column=3, padx=15)
        self.__btn_gauche.grid(row=2, column=0, padx=15)
        self.__btn_arret.grid(row=4, column=1, pady=20)
        self.__btn_quitter.grid(row=3, column=1, columnspan=2, pady=20)
        self.__btn_quitter.config(state=DISABLED)

        # Configurer la grille pour que les colonnes s'étendent
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Désactivation de la fenêtre commande
        self.disable(self.__fen_commande)

        # Lier les touches du clavier
        for e in ["z", "q", "s", "d", "x"]:
            self.bind('<KeyPress-%s>' % e, self.press)
            self.bind('<KeyRelease-%s>'%e ,self.release)

        self.mainloop()

    def touche_avancer(self) -> None:
        """
        Gère l'action d'avancer le robot. Envoie la commande correspondante au serveur.
        """
        direc = "z"
        self.envoyer(direc)  # Envoyer la direction au serveur

    def touche_reculer(self) -> None:
        """
        Gère l'action de reculer le robot. Envoie la commande correspondante au serveur.
        """
        direc = "s"
        self.envoyer(direc)  # Envoyer la direction au serveur

    def touche_gauche(self) -> None:
        """
        Gère l'action de déplacement à gauche du robot. Envoie la commande correspondante au serveur.
        """
        direc = "q"
        self.envoyer(direc)  # Envoyer la direction au serveur

    def touche_droite(self) -> None:
        """
        Gère l'action de déplacement à droite du robot. Envoie la commande correspondante au serveur.
        """
        direc = "d"
        self.envoyer(direc)  # Envoyer la direction au serveur

    def touche_arret(self) -> None:
        """
        Gère l'arrêt du robot. Envoie la commande correspondante au serveur.
        """
        direc = "x"
        self.envoyer(direc)  # Envoyer la direction au serveur

    def connexion(self) -> None:
        """
        Établit la connexion TCP avec le serveur en utilisant l'adresse IP et le port fournis.
        Active les fonctionnalités de l'interface si la connexion est réussie.
        """
        try:
            print("connexion en cours")
            self.__ip_serveur = self.__entree_ip_serveur.get()
            self.__port_serveur = int(self.__entree_port_serveur.get())
            # instanciation du client TCP
            addr_serveur = (self.__ip_serveur, self.__port_serveur)
            self.__client_tcp: socket = socket(family=AF_INET, type=SOCK_STREAM)
            self.__client_tcp.connect(addr_serveur)
            print("connexion ok")
        except Exception as ex:
            print("erreur de connexion : ", ex)
        else:
            self.__btn_connexion.config(state=DISABLED)
            self.__btn_envoyer.config(state=NORMAL)
            self.__btn_quitter.config(state=NORMAL)
            self.enable(self.__fen_commande)  # Activer la fenêtre de commande après connexion
            self.enable(self.__fen_echange)  # Activer la fenêtre d'échange après connexion

    def recevoir(self) -> str:
        """
        Reçoit un message du serveur via la connexion TCP.

        Returns:
            str: Le message reçu du serveur.
        """
        tab_octet = self.__client_tcp.recv(1024)
        msg_serveur = tab_octet.decode(encoding="utf-8")
        return msg_serveur

    def envoyer(self, msg=None) -> None:
        """
        Envoie un message au serveur via la connexion TCP.

        Args:
            msg (str, optional): Le message à envoyer. Si aucun message n'est fourni,
            le contenu de l'entrée utilisateur sera envoyé.
        """
        try:
            if msg is None:
                msg = self.__entree_msg_client.get()
            if msg != "":
                self.__entree_msg_client.delete(0, END)
                self.__client_tcp.send(msg.encode(encoding="utf-8"))
                tab_octet = self.__client_tcp.recv(1024)
                chaine = tab_octet.decode(encoding="utf-8")
                self.__text_msg_serveur.insert(INSERT, chaine)
        except Exception as ex:
            self.__text_msg_serveur.insert(INSERT, "Erreur d'envoi : vous n'êtes pas connecté au robot\n")

    def arret(self) -> None:
        """
        Ferme la connexion TCP avec le serveur.
        """
        self.__client_tcp.close()

    def quitter(self) -> None:
        """
        Envoie une commande de fin au serveur et ferme l'application.
        """
        msg_fin: str = "/fin/"
        self.__client_tcp.send(msg_fin.encode(encoding="utf-8"))
        self.arret()
        self.__btn_connexion.config(state=NORMAL)
        self.__btn_envoyer.config(state=DISABLED)
        self.__btn_quitter.config(state=DISABLED)
        self.__entree_port_serveur.config(state=NORMAL)
        self.__entree_ip_serveur.config(state=NORMAL)
        self.disable(self.__fen_commande)  # Désactiver la fenêtre de commande après déconnexion
        
    def move_robot(self, direction: str) -> None:
        """
        Met à jour la position du robot en fonction de la direction donnée.

        Args:
            direction (str): La direction du déplacement ('z', 's', 'q', 'd').
        """
        # Déplacer le robot en fonction de la direction
        if direction == "z":  # Avancer
            self.robot_y -= 10
        elif direction == "s":  # Reculer
            self.robot_y += 10
        elif direction == "q":  # Gauche
            self.robot_x -= 10
        elif direction == "d":  # Droite
            self.robot_x += 10

        # Mettre à jour la position de l'image du robot sur le Canvas
        self.__canvas.coords(self.robot_id, self.robot_x, self.robot_y)
        self.__text_msg_serveur.insert(INSERT, f"Déplacement: {direction}\n")
        self.update_trajet()  # Mettre à jour le tracé

    def update_trajet(self):
        """
        Met à jour les informations affichées sur la position actuelle du robot.
        """
        # Effacer le contenu précédent
        self.__text_msg_serveur.delete(1.0, END)
        # Afficher la nouvelle position
        self.__text_msg_serveur.insert(INSERT, f"Position actuelle: ({self.robot_x}, {self.robot_y})\n")

    def arret_via_X(self) -> None:
        """
        Gère la fermeture de l'application via la fermeture de la fenêtre.
        Envoie une commande de fin au serveur avant de détruire l'interface.
        """
        try:
            msg_fin: str = "/fin/"
            self.__client_tcp.send(msg_fin.encode(encoding="utf-8"))
            self.arret_serveur()
        except Exception as ex:
            self.arret_serveur()

    def arret_serveur(self) -> None:
        """
        Ferme la connexion TCP avec le serveur et détruit la fenêtre.
        """
        try:
            self.__client_tcp.close()
            self.destroy()
        except Exception as ex:
            self.destroy()

    def action_evt(self, event: Event) -> Event:
        """
        Gère un événement général et envoie une commande au serveur.

        Args:
            event (Event): L'événement à traiter.

        Returns:
            Event: L'événement reçu.
        """
        print(event)
        self.envoyer()

    def press(self, event):
        """
        Gère les pressions sur les touches du clavier pour le déplacement du robot.

        Args:
            event: L'événement du clavier.
        """
        # Gérer les touches du clavier pour déplacer le robot
        direction = event.keysym
        self.move_robot(direction)
        self.envoyer(direction)  # Envoyer la direction au serveur

    def release(self, event : Event) -> Event :
        """
        Gère le relâchement des touches du clavier pour arrêter le robot.

        Args:
            event (Event): L'événement du clavier.

        Returns:
            Event: L'événement reçu.
        """
        arret = "x"
        direction = event.keysym
        self.move_robot(arret)
        self.envoyer(arret)  # Envoyer la direction au serveur
        

    def disable(self, frame: Frame) -> None:
        """
        NE PAS MODIFIER LE METHODE
        Désactive tous les widgets enfants d'un cadre.
        Args:
            frame (Frame): Le cadre dont les widgets enfants doivent être désactivés.
        """
        for child in frame.winfo_children():
            child.configure(state='disabled')

    def enable(self, frame: Frame) -> None:
        """
        NE PAS MODIFIER LE METHODE
        Active tous les widgets enfants d'un cadre.
        Args:
            frame (Frame): Le cadre dont les widgets enfants doivent être activés.
        """
        for child in frame.winfo_children():
            child.configure(state='normal')

    def auto_command(self, event):
        """
        Exécute la commande automatique.

        Args:
            event: L'événement associé à la commande automatique.
        """
        print("Commande Automatique exécutée")
        # Ajoutez ici le code pour gérer la commande automatique

    def manuel_command(self, event):
        """
        Exécute la commande manuelle.

        Args:
            event: L'événement associé à la commande manuelle.
        """
        print("Commande Manuel exécutée")
        # Ajoutez ici le code pour gérer la commande manuelle

if __name__ == "__main__":
    mon_ihm: IHM_Robot11
    mon_ihm = IHM_Robot11()