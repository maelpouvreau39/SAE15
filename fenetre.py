import tkinter as tk
from tkinter import ttk
REGIONS = {
    "Auvergne-Rhône-Alpes": ["01","03","07","15","26","38","42","43","63","69","73","74"],
    "Bourgogne-Franche-Comté": ["21","25","39","58","70","71","89","90"],
    "Bretagne": ["22","29","35","56"],
    "Centre-Val de Loire": ["18","28","36","37","41","45"],
    "Corse": ["2A","2B"],
    "Grand Est": ["08","10","51","52","54","55","57","67","68","88"],
    "Hauts-de-France": ["02","59","60","62","80"],
    "Île-de-France": ["75","77","78","91","92","93","94","95"],
    "Normandie": ["14","27","50","61","76"],
    "Nouvelle-Aquitaine": ["16","17","19","23","24","33","40","47","64","79","86","87"],
    "Occitanie": ["09","11","12","30","31","32","34","46","48","65","66","81","82"],
    "Pays de la Loire": ["44","49","53","72","85"],
    "Provence-Alpes-Côte d'Azur": ["04","05","06","13","83","84"],
    "Guadeloupe": ["971"],
    "Martinique": ["972"],
    "Guyane": ["973"],
    "La Réunion": ["974"],
    "Mayotte": ["976"],
}
def filtrer_et_afficher(region, exploitant, tech):
     print(region, exploitant, tech)
     
def creer_carte():
    pass  # on mettra le filtre + folium ici plus tard
#window 
fenetre = tk.Tk()
#title of the window
fenetre.title("Filtres de la carte")
#menu of the regions to apply the filters
tk.Label(fenetre, text="Région :", font=("Arial", 15)).pack()
menu_region = ttk.Combobox(fenetre, values=["Toutes"] + list(REGIONS.keys()), state="readonly")
#add the default value to the menu
menu_region.set("Toutes")
menu_region.pack(pady=5)
tk.Label(fenetre, text="Exploitants :", font=("Arial", 15)).pack()
menu_exploitants = ttk.Combobox(fenetre, values=["Tous", "Orange", "SFR", "Bouygues" , "Free"], state ="readonly")
menu_exploitants.set("Tous")
menu_exploitants.pack(pady=5)
tk.Label(fenetre, text="Technologies :", font=("Arial" , 15)).pack()
menu_tech = ttk.Combobox(fenetre, values=["Toutes", "2G","3G", "4G", "5G"], state="readonly")
menu_tech.set("Toutes")
menu_tech.pack(pady=5)
tk.Button(fenetre, text="Afficher la carte", command=creer_carte).pack()



#create the map with the filters applied
fenetre.mainloop()