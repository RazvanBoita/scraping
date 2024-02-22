from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
from datetime import date
import re
import json


date_format = r'^\d{4}-\d{2}-\d{2}$'


def checkValidDate(myDate):
    year, month, day = myDate.split('-')
    year = int(year)
    month = int(month)
    day = int(day)
    input_date = date(year,month,day)
    today = date.today()
    return input_date>=today

def checkCorrectDates(checkin, checkout):
    inyear, inmonth, inday = checkin.split('-')
    outyear, outmonth, outday = checkout.split('-')
    inyear, inmonth, inday = int(inyear),int(inmonth),int(inday)
    outyear, outmonth, outday = int(outyear),int(outmonth),int(outday)
    indate = date(inyear,inmonth,inday)
    outdate = date(outyear,outmonth,outday)
    return outdate>indate

while True:
    checkin = input("Enter the check-in date(YYYY-MM-DD): ")
    checkout = input("Enter the check-out date(YYYY-MM-DD): ")
    if re.match(date_format,checkin) and re.match(date_format,checkout):
        print("Checking your dates...")
        if checkValidDate(checkin) * checkValidDate(checkout) * checkCorrectDates(checkin, checkout) !=0:
            break
        elif checkValidDate(checkin)==0: print(f"Data de check-in trebuie sa fie dupa {date.today()}")
        elif checkValidDate(checkout)==0: print(f"Data de check-out trebuie sa fie dupa {date.today()}")
        elif checkCorrectDates(checkin, checkout)==0:
            print("Data de check-in trebuie sa fie inainte de data de check-out!")
    else: print("Please enter correct dates(with the format YYYY-MM-DD)")

print("Dates are correct, fetching results...This might take some time")

def trimNrFromtext(description):
    #input is something like: In Iasi au fost gasite 415 proprietati, output: 415
    i = 0
    while not description[i].isdigit():
        i+=1
    output = ""
    while description[i].isdigit():
        output += description[i]
        i+=1
    return output


check_url = "https://www.booking.com/searchresults.ro.html?label=iasi-ro-RPFIEorp_Hlbh7jFMAxNMAS379608404872%3Apl%3Ata%3Ap1%3Ap2%3Aac%3Aap%3Aneg%3Afi%3Atiaud-2007787596709%3Akwd-323684599876%3Alp1011828%3Ali%3Adec%3Adm%3Appccp%3DUmFuZG9tSVYkc2RlIyh9YcUc3ZfdbbfEHZ2_wTDb1e4&aid=1610697&ss=Ia%C5%9Fi&ssne=Ia%C5%9Fi&ssne_untouched=Ia%C5%9Fi&lang=ro&sb=1&src_elem=sb&src=city&dest_id=-1161664&dest_type=city&checkin={}&checkout={}&group_adults=2&no_rooms=1&group_children=0&sb_travel_purpose=leisure&selected_currency=RON&offset=0"
check_url = check_url.format(checkin,checkout)
# print(check_url)

driver = webdriver.Chrome()

driver.get(check_url)
check_src = driver.page_source
soup = BeautifulSoup(check_src,"html.parser")


description = soup.find("h1",{'class':'f6431b446c d5f78961c3'})
results = int(trimNrFromtext(description.text))
print(f"Found {results} hotels")

base_url = "https://www.booking.com/searchresults.ro.html?label=iasi-ro-RPFIEorp_Hlbh7jFMAxNMAS379608404872%3Apl%3Ata%3Ap1%3Ap2%3Aac%3Aap%3Aneg%3Afi%3Atiaud-2007787596709%3Akwd-323684599876%3Alp1011828%3Ali%3Adec%3Adm%3Appccp%3DUmFuZG9tSVYkc2RlIyh9YcUc3ZfdbbfEHZ2_wTDb1e4&aid=1610697&ss=Ia%C5%9Fi&ssne=Ia%C5%9Fi&ssne_untouched=Ia%C5%9Fi&lang=ro&sb=1&src_elem=sb&src=city&dest_id=-1161664&dest_type=city&checkin={}&checkout={}&group_adults=2&no_rooms=1&group_children=0&sb_travel_purpose=leisure&selected_currency=RON&offset={}"
hotels_count=0

with open("booking_iasi.csv",'w',newline='',encoding='utf-8') as file:
    csvwriter = csv.writer(file)
    csvwriter.writerow(['Nume Hotel', 'Pret','Rating','Nr Evaluari']) 
    # results//25+1
    for i in range(0, 1):
        offset_val = i * 25
        curr_url = base_url.format(checkin, checkout, offset_val)
        driver.get(curr_url)

        WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.CLASS_NAME, 'f6431b446c')))

        page_source = driver.page_source

        soup = BeautifulSoup(page_source, "html.parser")

        prices = soup.findAll('span', {'data-testid': 'price-and-discounted-price', 'aria-hidden': 'true', 'class': 'f6431b446c fbfd7c1165 e84eb96b1f'})
        hotels = soup.findAll('div', {'data-testid': 'title', 'class': 'f6431b446c a15b38c233'})
        ratings = soup.findAll('div', {'class':"a3b8729ab1 d86cee9b25"})
        evals = soup.findAll('div',{'class':'abf093bdfe f45d8e4c32 d935416c47'})
        for hotel,price,rating,eval in zip(hotels,prices,ratings,evals):
            csvwriter.writerow([hotel.text,price.text,rating.text,trimNrFromtext(eval.text)])

    driver.quit()


year, month, day = checkin.split('-')
year, month, day = int(year), int(month), int(day)
date1 = date(year,month,day)

year, month, day = checkout.split('-')
year, month, day = int(year), int(month), int(day)
date2 = date(year,month,day)

delta = date2-date1
nights = delta.days


data_to_transmit = {
    'city': 'Iasi',
    'results': results,
    'checkin': checkin,
    'checkout': checkout,
    'nights' : nights
}

with open ('transmit.json','w') as json_file:
    json.dump(data_to_transmit,json_file)