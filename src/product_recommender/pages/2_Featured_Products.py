import streamlit as st
import requests
import pandas as pd
import numpy as np
from PIL import Image
from io import BytesIO
from azure.storage.blob import BlobServiceClient
import logging


def display_data(df_rat, df_vfm, df_com):
    df_rat = df_rat.sample(10, weights="Scaled Rating")
    df_vfm = df_vfm.sample(10, weights="VFM")
    df_com = df_com.sample(10, weights="composite")

    tab1, tab2, tab3 = st.tabs(["Best Products by Rating", "Best Products by Value for Money", "Best Products by Composite Rating"])
    
    with tab1:
        for i in range(len(df_rat)):
            col1, col2 = st.columns([4, 1])
            col1.write(f"""{i+1}. [{df_rat.iloc[i, 1]}]({df_rat.iloc[i, 2]})  
                        **Platform** : {df_rat.iloc[i, 0]}  
                        **Price** : {df_rat.iloc[i, 3]} Rs.  
                        **Rating** : {round(df_rat.iloc[i, 8], 2)}  
                        **Value for Money** : {round(df_rat.iloc[i, 9], 2)}  
                        **Composite Rating** : {round(df_rat.iloc[i, 10], 2)}  
            

                    """)
            r = requests.get(df_rat.iloc[i, 7])
            img = Image.open(BytesIO(r.content))
            width, height = img.size
            resize_len = width if width >= height else height
            img = img.resize((resize_len, resize_len))
            col2.image(img)

    with tab2:
        for i in range(len(df_vfm)):
            col1, col2 = st.columns([4, 1])
            col1.write(f"""{i+1}. [{df_vfm.iloc[i, 1]}]({df_vfm.iloc[i, 2]})  
                        **Platform** : {df_vfm.iloc[i, 0]}                      
                        **Price** : {df_vfm.iloc[i, 3]} Rs.  
                        **Rating** : {round(df_vfm.iloc[i, 8], 2)}  
                        **Value for Money** : {round(df_vfm.iloc[i, 9], 2)}  
                        **Composite Rating** : {round(df_vfm.iloc[i, 10], 2)}  
            

                    """)
            r = requests.get(df_vfm.iloc[i, 7])
            img = Image.open(BytesIO(r.content))
            width, height = img.size
            resize_len = width if width >= height else height
            img = img.resize((resize_len, resize_len))
            col2.image(img)

    with tab3:
        for i in range(len(df_com)):
            col1, col2 = st.columns([4, 1])
            col1.write(f"""{i+1}. [{df_com.iloc[i, 1]}]({df_com.iloc[i, 2]})  
                        **Platform** : {df_com.iloc[i, 0]}  
                        **Price** : {df_com.iloc[i, 3]} Rs.  
                        **Rating** : {round(df_com.iloc[i, 8], 2)}  
                        **Value for Money** : {round(df_com.iloc[i, 9], 2)}  
                        **Composite Rating** : {round(df_com.iloc[i, 10], 2)}  
            

                    """)
            r = requests.get(df_com.iloc[i, 7])
            img = Image.open(BytesIO(r.content))
            width, height = img.size
            resize_len = width if width >= height else height
            img = img.resize((resize_len, resize_len))
            col2.image(img)

logger = logging.getLogger('azure.core.pipeline.policies.http_logging_policy').setLevel(logging.WARNING)

connection_string = st.secrets["database_connection"]["connection_string"]
container_name = st.secrets["database_connection"]["container_name"]
masterSearchFileName = st.secrets["database_connection"]["masterSearchFileName"]
blob_service_client = BlobServiceClient.from_connection_string(connection_string)
container_client = blob_service_client.get_container_client(container=container_name)

downlodData = container_client.download_blob(masterSearchFileName).readall()
keydict = pd.read_json(BytesIO(downlodData), dtype={"Search":str, "Time":np.float32, "Key":str})
keyList = keydict.drop_duplicates(subset=["Search"]).loc[:,"Key"].values

keyListInt = [int(i.split("_")[0]) for i in keyList]

resultFileName = "projects/productRecommendor/data/store/config.json"
lastDate = container_client.download_blob(resultFileName).readall()
    
newKeyList = [j[0] for j in zip(keyList, keyListInt) if j[1]>int(lastDate)]

FileName = "projects/productRecommendor/data/store/data_rat.json"
downlodData = container_client.download_blob(FileName).readall()
df_rat = (pd.read_json(BytesIO(downlodData), 
                       dtype={"platform":str,"Desc":str,"Link":str,"Price":int,"Rating":float,
                              "Raters":int,"Reviewers":int,"img_url":str,
                              "Scaled Rating":float,"VFM":float,"composite":float}))

FileName = "projects/productRecommendor/data/store/data_vfm.json"
downlodData = container_client.download_blob(FileName).readall()
df_vfm = (pd.read_json(BytesIO(downlodData), 
                       dtype={"platform":str,"Desc":str,"Link":str,"Price":int,"Rating":float,
                              "Raters":int,"Reviewers":int,"img_url":str,
                              "Scaled Rating":float,"VFM":float,"composite":float}))

FileName = "projects/productRecommendor/data/store/data_com.json"
downlodData = container_client.download_blob(FileName).readall()
df_com = (pd.read_json(BytesIO(downlodData), 
                       dtype={"platform":str,"Desc":str,"Link":str,"Price":int,"Rating":float,
                              "Raters":int,"Reviewers":int,"img_url":str,
                              "Scaled Rating":float,"VFM":float,"composite":float}))


if len(newKeyList) > 0:
    df = pd.DataFrame(columns=['platform', 'Desc', 'Link', 'Price', 'Rating', 'Raters', 'Reviewers', 'img_url'])
    for key in newKeyList:
        resultFileName = "projects/productRecommendor/data/result/"+key+".json"
        downlodData = container_client.download_blob(resultFileName).readall()
        df_ = (pd.read_json(BytesIO(downlodData), 
                            dtype={"platform":str,"Desc":str,"Link":str,"Price":int,"Rating":float,
                                "Raters":int,"Reviewers":int,"img_url":str, 
                                "Scaled Rating":float,"VFM":float,"composite":float}))
        df = pd.concat([df, df_])
    
    df_rat = pd.concat([df_rat, df]).drop_duplicates("Link")
    df_vfm = pd.concat([df_vfm, df]).drop_duplicates("Link")
    df_com = pd.concat([df_com, df]).drop_duplicates("Link")

    df_rat = (df_rat.sort_values(['Scaled Rating', 'composite', 'VFM', 'Raters', 'Reviewers'], axis=0, ascending=False)
              .iloc[:1000].reset_index(drop=True))
    df_vfm = (df_vfm.sort_values(['VFM', 'composite', 'Scaled Rating', 'Raters', 'Reviewers'], axis=0, ascending=False)
              .iloc[:1000].reset_index(drop=True))
    df_com = (df_com.sort_values(['composite', 'Scaled Rating', 'VFM', 'Raters', 'Reviewers'], axis=0, ascending=False)
              .iloc[:1000].reset_index(drop=True))
    
    resultFileName = "projects/productRecommendor/data/store/data_rat.json"
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=resultFileName)
    _ = blob_client.upload_blob(df_rat.to_json(), overwrite=True)
    
    resultFileName = "projects/productRecommendor/data/store/data_vfm.json"
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=resultFileName)
    _ = blob_client.upload_blob(df_vfm.to_json(), overwrite=True)
    
    resultFileName = "projects/productRecommendor/data/store/data_com.json"
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=resultFileName)
    _ = blob_client.upload_blob(df_com.to_json(), overwrite=True)
    
    resultFileName = "projects/productRecommendor/data/store/config.json"
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=resultFileName)
    _ = blob_client.upload_blob(str(max(keyListInt)), overwrite=True)
    

if st.button("Refresh"):
    display_data(df_rat, df_vfm, df_com)
    st.stop()

display_data(df_rat, df_vfm, df_com)