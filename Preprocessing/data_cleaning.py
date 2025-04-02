import os
import pandas as pd
import re

file_path_thuoc = "D:\Medical ChatBotRAG\Medical data\medicine_data.csv"
file_path_benh = "D:\Chatbot RAG\Data\Raw data\disease_data.csv"
df_thuoc = pd.read_csv(file_path_thuoc)
df_benh = pd.read_csv(file_path_benh)

def data_columns_transform(df):

    df.drop(columns=["content_list", "content_container", "product_content","inner_div"],inplace=True,errors="ignore")

    df.rename(columns={
        "url": "URL",
        "heading": "Tên thuốc",
        "ingredient": "Thành phần",
        "usage": "Công dụng",
        "dosage": "Cách dùng",
        "adverse_effect": "Tác dụng phụ",
        "careful": "Lưu ý",
        "preservation": "Bảo quản"
    },inplace=True)


def cleaning_text(df):

    if "Tên thuốc" in df.columns:
        df["Tên thuốc"] = df["Tên thuốc"].apply(lambda x: re.sub(r'\s*là gì\?$', '', str(x), flags=re.IGNORECASE))
    
    df["Tên bệnh"] = df["Tên bệnh"].str.replace(": Nguyên nhân, triệu chứng, chẩn đoán và điều trị$", "", regex=True)

def drop_na(df):
    df = df.dropna()

data_columns_transform(df_thuoc)
cleaning_text(df_thuoc)
cleaning_text(df_benh)
drop_na(df_thuoc)
drop_na(df_benh)


