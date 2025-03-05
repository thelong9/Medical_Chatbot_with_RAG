from os import listdir
from os.path import isfile, join

import pandas as pd
ROOT = '../data_comments'

if __name__ == '__main__':
    files = [f for f in listdir(ROOT) if isfile(join(ROOT, f))]
    for file in files:
        df = pd.read_csv(f'{ROOT}/{file}')
        df = df.drop(columns=['title', 'thank_count', 'created_at', 'customer_name', 'purchased_at', ])
        df.to_csv(f'processed_data/{file.replace('comments_data_','')}', index=False)
