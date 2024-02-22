import pandas as pd
import json
df = pd.read_csv('cleaned_booking_iasi.csv')

def parseJSON(json_file):
    output = f'''Oras: {json_file.get("city")}\n
Data check-in: {json_file.get("checkin")}\n
Data check-out: {json_file.get("checkout")}\n
Numar nopti: {json_file.get("nights")}\n\n\n'''
    return output

    
info = ''
with open ('transmit.json','r') as json_file:
    recv_data = json.load(json_file)
    info = parseJSON(recv_data)

with open ('extracted_data_booking_iasi.txt','w') as file:
    file.write("INFORMATII DESPRE CAUTARE:\n")
    file.write(info)
    preturi = df["Pret"].str.replace("lei","").astype(float)

    avg_price = preturi.mean().round(2)
    min_price = preturi.min().round(2)
    max_price = preturi.max().round(2)
    total_price = preturi.sum().round(2)


    min_price_hotel = df.loc[preturi.idxmin()]["Nume Hotel"]
    max_price_hotel = df.loc[preturi.idxmax()]["Nume Hotel"]
    file.write("PRETURI:\n")
    file.write(f"Media preturilor locuintelor din Iasi este : {avg_price} lei\n")
    file.write(f"Locuinta '{min_price_hotel[:-1]}' are pretul minim: {min_price} lei\n")
    file.write(f"Locuinta '{max_price_hotel[:-1]}' are pretul maxim: {max_price} lei\n")
    file.write(f"Totalul preturilor locuintelor din Iasi este: {total_price} lei\n\n")


    ratings = df["Rating"].str.replace(",",".").astype(float)

    avg_rating = ratings.mean().round(2)
    min_rating = ratings.min().round(2)
    max_rating = ratings.max().round(2)

    min_rating_hotel = df.loc[ratings.idxmin()]["Nume Hotel"]
    max_rating_hotel = df.loc[ratings.idxmax()]["Nume Hotel"]
    file.write("RATING-URI:\n")
    file.write(f"Media rating-urilor locuintelor din Iasi este : {avg_rating}\n")
    file.write(f"Cea mai slaba evaluata locuinta din Iasi este '{min_rating_hotel[:-1]}' cu nota {min_rating}\n")
    file.write(f"Cea mai bine evaluata locuinta din Iasi este '{max_rating_hotel[:-1]}' cu nota {max_rating}\n\n")


    evals = df["Nr Evaluari"].astype(int)

    avg_evals = evals.mean().round(2)
    min_evals = evals.min().round(2)
    max_evals = evals.max().round(2)

    min_evals_hotel = df.loc[evals.idxmin()]["Nume Hotel"]
    max_evals_hotel = df.loc[evals.idxmax()]["Nume Hotel"]

    file.write("EVALUARI:\n")
    file.write(f"In medie, o locuinta din Iasi are {avg_evals} evaluari\n")
    file.write(f"Cea mai putin evaluata locuinta din Iasi, cu {min_evals} evaluari este '{min_evals_hotel[:-1]}'\n")
    file.write(f"Cea mai evaluata locuinta din Iasi, cu {max_evals} evaluari este '{max_evals_hotel[:-1]}'\n\n")

    #TODO Create recommendations
    pret_wgt = 0.4
    rating_wgt = 0.4
    evals_wgt = 0.2
    df['pret_normalizat'] = (preturi - preturi.min()) / (preturi.max() - preturi.min())    
    df['rating_normalizat'] = (ratings - ratings.min()) / (ratings.max() - ratings.min())    
    df['evals_normalizat'] = (evals - evals.min()) / (evals.max() - evals.min())    

    df['scor'] = (
        pret_wgt * df['pret_normalizat'] + 
        rating_wgt * df['rating_normalizat'] + 
        evals_wgt * df['evals_normalizat']
    ).round(2)
    df = df.sort_values(by='scor', ascending=False)
    recom = df[['Nume Hotel', 'Pret', 'Rating', 'Nr Evaluari', 'scor']]  
    recom.to_csv('recomandari.csv',index=False)
