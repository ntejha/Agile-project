import pandas as pd
import os

def load_csv(file):
    if not os.path.exists(file):
        df = pd.DataFrame()
        df.to_csv(file, index=False)
    return pd.read_csv(file)

def append_csv(file, data, columns=None):
    df = load_csv(file)
    new_entry = pd.DataFrame([data], columns=columns if columns else df.columns)
    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_csv(file, index=False)

def update_campaign(file, title, amount):
    df = load_csv(file)
    idx = df[df['title'] == title].index
    if not idx.empty:
        df.at[idx[0], 'raised'] = int(df.at[idx[0], 'raised']) + int(amount)
        df.to_csv(file, index=False)
