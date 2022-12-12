import streamlit as st
from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
from PIL import Image
from io import BytesIO

search_for = st.text_input(label='Search for:', value='')
# search_for = "honey"
search_for = search_for.replace(' ', '%20')

if search_for != '':

    base_link = ("https://www.flipkart.com/search?q=" + search_for + 
                "&sort=popularity&p%5B%5D=facets.fulfilled_by%255B%255D%3DPlus%2B%2528FAssured%2529" +
                "&p%5B%5D=facets.rating%255B%255D%3D4%25E2%2598%2585%2B%2526%2Babove" +
                "&p%5B%5D=facets.availability%255B%255D%3DExclude%2BOut%2Bof%2BStock")

    df_list = []
    style = ''
    progress = 0.0
    page = 0
    my_bar = st.progress(int(progress))
    while progress < 100:
        page = page + 1
        if page == 10:
            my_bar.progress(100)
            break
        link = base_link+"&page="+str(page)
        html_text = requests.get(link).text
        soup = BeautifulSoup(html_text, "html.parser")
        # print("\n\nPage :", page)
        # print("link:")
        # print(link, "\n\n")
        for row in soup.find_all('div', class_='_13oc-S'):
            if style == '':
                style = row.find('div')['style']
            
            if style == 'width:100%':
                descrs = row.find('div', class_='_4rR01T').text
                prodLink = 'https://www.flipkart.com' + (row.find('a', class_='_1fQZEK')['href'].split('?')[0])
                price = int(row.find('div', class_='_30jeq3 _1_WHN1').text[1:].replace(',', ''))
                ratebox = row.find('div', class_='_3LWZlK')
                if ratebox == None:
                    continue
                rating = float(ratebox.text)
                rateData = row.find('span', class_="_2_R_DZ").text
                raters = int(rateData.split()[0].replace(',',''))
                if raters < 30:
                    continue
                reviewers = int(rateData.split()[3].replace(',',''))
                img_url = row.find('img', class_="_396cs4")['src']
                df_list.append([descrs, prodLink, price, rating, raters, reviewers, img_url])
                progress = progress + (100/(168))
                my_bar.progress(int(progress) if int(progress)<100 else 100)
                continue
                
            elif style == 'width:25%':
                prods = row.find_all('div', class_='_4ddWXP')
                if len(prods) > 0:
                    for prod in prods:
                        header = prod.find('a', class_='s1Q9rs')
                        descrs = header['title']
                        prodLink = 'https://www.flipkart.com' + (header['href'].split('?')[0])
                        pricebox = prod.find('div', class_='_30jeq3')
                        if pricebox == None:
                            continue
                        price = int(pricebox.text[1:].replace(',', ''))
                        ratebox = prod.find('div', class_="_3LWZlK")
                        if ratebox == None:
                            continue
                        rating = float(ratebox.text)
                        raters = int(prod.find('span', class_="_2_R_DZ").text[1:-1].replace(',',''))
                        if raters < 30:
                            continue
                        img_url = prod.find('img', class_="_396cs4")['src']
                        df_list.append([descrs, prodLink, price, rating, raters, np.nan, img_url])
                        progress = progress + (100/(160))
                        my_bar.progress(int(progress) if int(progress)<100 else 100)
                else:
                    prods = row.find_all('div', class_='_1xHGtK _373qXS')
                    for prod in prods:
                        header = prod.find('a', class_='IRpwTa')
                        descrs = header['title']
                        prodLink = 'https://www.flipkart.com' + (header['href'].split('?')[0])
                        price = int(prod.find('div', class_='_30jeq3').text[1:].replace(',', ''))
                        # sleep(1.5)
                        prod_text = requests.get(prodLink).text
                        prod_soup = BeautifulSoup(prod_text, "html.parser")
                        ratebox = prod_soup.find('div', class_='_3LWZlK _3uSWvT')
                        if ratebox == None:
                            continue
                        rating = float(ratebox.text)
                        rateData = prod_soup.find('span', class_="_2_R_DZ")
                        if rateData == None:
                            continue
                        raters = int(rateData.text.split()[0].replace(',',''))
                        if raters < 30:
                            continue
                        reviewers = int(rateData.text.split()[3].replace(',',''))
                        img_url = prod.find('img', class_="_2r_T1I")['src']
                        df_list.append([descrs, prodLink, price, rating, raters, reviewers, img_url])
                        progress = progress + (100/(160))
                        my_bar.progress(int(progress) if int(progress)<100 else 100)
                
                
    df = pd.DataFrame(df_list, columns=['Desc', 'Link', 'Price', 'Rating', 'Raters', 'Reviewers', 'img_url'])
    df = df.drop_duplicates(subset=['Price', 'Rating', 'Raters'])
    df['Scaled Rating'] = df['Rating']*(1 - np.power(1.06, -1*df['Raters']))
    df['VFM'] = (df['Scaled Rating']/(df['Scaled Rating'].mean()))*(np.sqrt(df['Price'].mean()))/np.sqrt(df['Price'])
    df['composite'] = ((df['Scaled Rating']/(df['Scaled Rating'].mean())) * (np.sqrt(df['VFM'])/(np.sqrt(df['VFM'].mean()))))
    df_rat = df.sort_values(['Scaled Rating', 'Raters', 'Reviewers', 'composite', 'VFM'], axis=0, ascending=False).head(5)
    df_vfm = df.sort_values(['VFM', 'Raters', 'Reviewers', 'composite', 'Scaled Rating'], axis=0, ascending=False).head(5)
    df_com = df.sort_values(['composite', 'Raters', 'Reviewers', 'Scaled Rating', 'VFM'], axis=0, ascending=False).head(5)

    st.subheader("Best Products by Rating")
    for i in range(len(df_rat)):
        col1, col2 = st.columns([4, 1])
        col1.write(f"""{i+1}. [{df_rat.iloc[i, 0]}]({df_rat.iloc[i, 1]})  
                    **Price** : {df_rat.iloc[i, 2]} Rs.  
                    **Rating** : {round(df_rat.iloc[i, 7], 2)}  
                    **Value for Money** : {round(df_rat.iloc[i, 8], 2)}  
                    **Composite Rating** : {round(df_rat.iloc[i, 9], 2)}  
        

                """)
        r = requests.get(df_rat.iloc[i, 6])
        img = Image.open(BytesIO(r.content))
        width, height = img.size
        resize_len = width if width >= height else height
        img = img.resize((resize_len, resize_len))
        col2.image(img)
        

    st.subheader("Best Products by Value for Money")
    for i in range(len(df_vfm)):
        col1, col2 = st.columns([4, 1])
        col1.write(f"""{i+1}. [{df_vfm.iloc[i, 0]}]({df_rat.iloc[i, 1]})  
                    **Price** : {df_vfm.iloc[i, 2]} Rs.  
                    **Rating** : {round(df_vfm.iloc[i, 7], 2)}  
                    **Value for Money** : {round(df_vfm.iloc[i, 8], 2)}  
                    **Composite Rating** : {round(df_vfm.iloc[i, 9], 2)}  
        

                """)
        r = requests.get(df_vfm.iloc[i, 6])
        img = Image.open(BytesIO(r.content))
        width, height = img.size
        resize_len = width if width >= height else height
        img = img.resize((resize_len, resize_len))
        col2.image(img)

    st.subheader("Best Products by Composite Rating")
    for i in range(len(df_com)):
        col1, col2 = st.columns([4, 1])
        col1.write(f"""{i+1}. [{df_com.iloc[i, 0]}]({df_rat.iloc[i, 1]})  
                    **Price** : {df_com.iloc[i, 2]} Rs.  
                    **Rating** : {round(df_com.iloc[i, 7], 2)}  
                    **Value for Money** : {round(df_com.iloc[i, 8], 2)}  
                    **Composite Rating** : {round(df_com.iloc[i, 9], 2)}  
        

                """)
        r = requests.get(df_com.iloc[i, 6])
        img = Image.open(BytesIO(r.content))
        width, height = img.size
        resize_len = width if width >= height else height
        img = img.resize((resize_len, resize_len))
        col2.image(img)

    st.subheader("Entire Data Extract")
    st.dataframe(df[['Desc', 'Link', 'Price', 'Rating', 'Raters', 'Reviewers', 'Scaled Rating', 'VFM', 'composite']])
