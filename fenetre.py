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
EXPLOITANTS = ["ORANGE" ,"SFR","BOUYGUES TELECOM","FREE MOBILE"]

tous_les_departements = []
for liste in REGIONS.values():
    tous_les_departements = tous_les_departements + liste
tous_les_departements.sort()

def changer_region(event):
    # Called when the user chooses a region:
    # the department menu only shows the departments of this region
    region = menu_region.get()
    if region == "Toutes":
        menu_departement["values"] = ["Tous"] + tous_les_departements
    else:
        menu_departement["values"] = ["Tous"] + REGIONS[region]
    menu_departement.set("Tous")

def creer_carte():
    region = menu_region.get()
    departement = menu_departement.get()
    exploitant = menu_exploitants.get()
    tech = menu_tech.get()
    sup_id = entry_sup_id.get() # on mettra le filtre + folium ici plus tard
    if sup_id == "":
            sup_id = "Tous"
    
        # 3) For now, we only print the choices.
        # Later: filter the data with pandas, then create the folium map.
        # Warning: Corsica postal codes start with "20",
        # and overseas departments (971...) have 3 digits.
    print("Région :", region)
    print("Département :", departement)
    print("Exploitant :", exploitant)
    print("Technologie :", tech)
    print("SUP_ID :", sup_id)
#window 
fenetre = tk.Tk()
#title of the window
fenetre.title("Filtres de la carte")
#menu of the regions to apply the filters, readonly means that the user cannot write in the menu, only select an option 
tk.Label(fenetre, text="Région :", font=("Arial", 15)).pack()
menu_region = ttk.Combobox(fenetre, values=["Toutes"] + list(REGIONS.keys()), state="readonly")
#add the default value to the menu
menu_region.set("Toutes")
menu_region.pack(pady=5)
tk.Label(fenetre, text="Departements :", font=("Arial", 15)).pack()
menu_departement = ttk.Combobox(fenetre, values=["Tous"] + [num for sublist in REGIONS.values() for num in sublist], state="readonly")
menu_departement.set("Tous")
menu_departement.pack(pady=5)
tk.Label(fenetre, text="Exploitants :", font=("Arial", 15)).pack()
menu_exploitants = ttk.Combobox(fenetre, values=["Tous", "Orange", "SFR", "Bouygues" , "Free"], state ="readonly")
menu_exploitants.set("Tous")
menu_exploitants.pack(pady=5)
tk.Label(fenetre, text="Technologies :", font=("Arial" , 15)).pack()
menu_tech = ttk.Combobox(fenetre, values=["Toutes", "2G","3G", "4G", "5G"], state="readonly")
menu_tech.set("Toutes")
menu_tech.pack(pady=5)   
tk.Label(fenetre, text="SUP_ID :", font=("Arial", 15)).pack()
entry_sup_id = tk.Entry(fenetre)
entry_sup_id.pack(pady=5)
menu_region.bind("<<ComboboxSelected>>", changer_region)
tk.Button(fenetre, text="Afficher la carte", command=creer_carte).pack()

#create the map with the filters applied
fenetre.mainloop()