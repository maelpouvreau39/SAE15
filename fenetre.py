import tkinter as tk
from tkinter import ttk

def creer_carte():
    pass  # on mettra le filtre + folium ici plus tard
#window 
fenetre = tk.Tk()
#title of the window
fenetre.title("Filtres de la carte")
#menu of the regions to apply the filters
tk.Label(fenetre, text="Région :", font=("Arial", 15)).pack()
menu_region = ttk.Combobox(fenetre, values=["Toutes", "Bretagne", "Normandie"], state="readonly")
#add the default value to the menu
menu_region.set("Toutes")
menu_region.pack(pady=5)
tk.Label(fenetre, text="Exploitants :", font=("Arial", 15)).pack()
menu_exploitants = ttk.Combobox(fenetre, values=["Tous", "Orange", "SFR", "Bouygues"], state ="readonly")
menu_exploitants.set("Tous")
menu_exploitants.pack(pady=5)
tk.Button(fenetre, text="Afficher la carte", command=creer_carte).pack()



#create the map with the filters applied
fenetre.mainloop()