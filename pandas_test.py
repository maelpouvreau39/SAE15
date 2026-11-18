import pandas as pd
support = pd.read_csv(r"C:\Users\ninal\Downloads\data (1)\data\sup_support.txt", sep=";", dtype={"STA_NM_ANFR": str}) # change the acces path to your local path
print(support.shape)