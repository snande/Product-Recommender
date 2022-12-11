import streamlit as st
from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
from time import sleep

search_for = "jewellery for women"
search_for = search_for.replace(' ', '%20')

base_link = ("https://www.flipkart.com/search?q=" + search_for + 
             "&sort=popularity&p%5B%5D=facets.fulfilled_by%255B%255D%3DPlus%2B%2528FAssured%2529" +
             "&p%5B%5D=facets.rating%255B%255D%3D4%25E2%2598%2585%2B%2526%2Babove" +
             "&p%5B%5D=facets.availability%255B%255D%3DExclude%2BOut%2Bof%2BStock")

df_list = []
style = ''
progress = 0.0
page = 0
while progress < 100:
    page = page + 1
    link = base_link+"&page="+str(page)
    html_text = requests.get(link).text
    soup = BeautifulSoup(html_text)
    print("\n\nPage :", page)
    print("link:")
    print(link, "\n\n")
    for row in soup.find_all('div', class_='_13oc-S'):
        if style == '':
            style = row.find('div')['style']
        
        if style == 'width:100%':
            descrs = row.find('div', class_='_4rR01T').text
            prodLink = 'https://www.flipkart.com' + (row.find('a', class_='_1fQZEK')['href'].split('?')[0])
            price = int(row.find('div', class_='_30jeq3 _1_WHN1').text[1:].replace(',', ''))
            rating = float(row.find('div', class_='_3LWZlK').text)
            rateData = row.find('span', class_="_2_R_DZ").text
            raters = int(rateData.split()[0].replace(',',''))
            if raters < 30:
                continue
            reviewers = int(rateData.split()[3].replace(',',''))
            df_list.append([descrs, prodLink, price, rating, raters, reviewers])
            progress = progress + (100/(168))
            print('Progress :', progress, '%')
            continue
            
        elif style == 'width:25%':
            prods = row.find_all('div', class_='_4ddWXP')
            if len(prods) > 0:
                for prod in prods:
                    header = prod.find('a', class_='s1Q9rs')
                    descrs = header['title']
                    prodLink = 'https://www.flipkart.com' + (header['href'].split('?')[0])
                    price = int(prod.find('div', class_='_30jeq3').text[1:].replace(',', ''))
                    ratebox = prod.find('div', class_="_3LWZlK")
                    if ratebox == None:
                        continue
                    rating = float(ratebox.text)
                    raters = int(prod.find('span', class_="_2_R_DZ").text[1:-1].replace(',',''))
                    if raters < 30:
                        continue
                    df_list.append([descrs, prodLink, price, rating, raters, np.nan])
                    progress = progress + (100/(160))
                    print('Progress :', progress, '%')
            else:
                prods = row.find_all('div', class_='_1xHGtK _373qXS')
                for prod in prods:
                    header = prod.find('a', class_='IRpwTa')
                    descrs = header['title']
                    prodLink = 'https://www.flipkart.com' + (header['href'].split('?')[0])
                    price = int(prod.find('div', class_='_30jeq3').text[1:].replace(',', ''))
                    sleep(1.5)
                    prod_text = requests.get(prodLink).text
                    prod_soup = BeautifulSoup(prod_text)
                    rating = float(prod_soup.find('div', class_='_3LWZlK _3uSWvT').text)
                    rateData = prod_soup.find('span', class_="_2_R_DZ")
                    if rateData == None:
                        continue
                    raters = int(rateData.text.split()[0].replace(',',''))
                    if raters < 30:
                        continue
                    reviewers = int(rateData.text.split()[3].replace(',',''))
                    df_list.append([descrs, prodLink, price, rating, raters, reviewers])
                    progress = progress + (100/(160))
                    print('Progress :', progress, '%')
            
            
df = pd.DataFrame(df_list, columns=['Desc', 'Link', 'Price', 'Rating', 'Raters', 'Reviewers'])
df['Scaled Rating'] = df['Rating']*(1 - np.power(1.06, -1*df['Raters']))
df['VFM'] = df['Scaled Rating']*(np.sqrt(df['Price'].mean()))/np.sqrt(df['Price'])
df['composite'] = ((df['Scaled Rating']) * (np.sqrt(df['VFM'])))
df_vfm = df.sort_values('VFM', axis=0, ascending=False).head(10)
df_rat = df.sort_values('Scaled Rating', axis=0, ascending=False).head(10)
df_com = df.sort_values('composite', axis=0, ascending=False).head(10)
