import os
import pandas as pd


data_folder = "D:\Medical ChatBotRAG\Medical data"
output_file = "D:\Medical ChatBotRAG\Medical data\medicine_data.csv"

all_medicine_data = []

for file in os.listdir(data_folder):
    if file.endswith(".csv"):
        file_path = os.path.join(data_folder, file)

        df = pd.read_csv(file_path, encoding="utf-8")

        medicine_type = file.replace(".csv", "").replace("_", " ").title()

        df["Loại thuốc"] = medicine_type

        all_medicine_data.append(df)

final_df = pd.concat(all_medicine_data, ignore_index=True)

final_df.to_csv(output_file, index=False)

