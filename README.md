# SAE15
Refer to requirement.txt to find out which file extensions need to be installed

Place the supplied data folders next to sae15_anfr.py so that the code can retrieve the data automatically

When the code is launched, the remote control takes around 19–20 seconds to start up

How does the code work?
When you run the code, a Tkinter window appears, this is the filter selection interface Simply select the filters you want, then click ‘Generate Map’, and a world map displaying the entire database will appear, but only according to your predefined filters.

Step-by-step instructions:

1) Run the code
2) Wait for the data to load
3) Choose your filters in the Tkinter window that has opened
4) Click ‘Generate map’
5) Open the map.html file 
6) Explore the map using your settings!


# Code structure

All the code is in one unique Python file, it is organised in a few main parts:

**Data**: finds the ANFR files given by the teacher, reads them and prepares them
**Filters**: keeps only the data that matches the user's choices
**Outputs**: builds the HTML pages of the project from the filtered data
**Interface**: the Tkinter window used as a remote control to choose the filters

## How it works (in big)

1. The program finds and reads the ANFR data files with pandas (if placed correctly)
2. The data is cleaned and the tables are linked together with their IDs based on the database
3. Everything stays in memory so that the filters are quick and a one time long loading is required at the first launch, unless the python cache is cleaned
4. The user chooses filters in the Tkinter window (region,4G or 5G or again operators)
5. The program keeps the matching data and generates the HTML pages then opens them in the browser
