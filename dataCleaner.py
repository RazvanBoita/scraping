import pandas as pd

df = pd.read_csv("booking_iasi.csv")

df["Pret"] = df["Pret"].astype(str)

def formatare_pret(pret):
    try:
        pret_bun = int(''.join(filter(str.isdigit,pret)))
        return pret_bun
    except ValueError:
        return pret

df["Pret"] = df["Pret"].apply(formatare_pret)    
df["Nume Hotel"]=df["Nume Hotel"].astype(str)+" "
df["Pret"] = df["Pret"].astype(str) + ' lei'

df.to_csv('cleaned_booking_iasi.csv', index=False)