""" File that cleans the data and merges all dataframes of the individual scraped websites into one in /output """
# TODO: make the filtering customizable via the config file

import os

import pandas as pd
import numpy as np

from src.util.config import config


def filter_data(df):
    # drop all full duplicates and rows with missing links (not starting with http)
    df.drop_duplicates(inplace=True)
    df = df[df['link'].str.startswith('http')]

    # keep all values that either are "Remote" or nan for the remote column
    df = df[df['remote'].isin(['Remote', np.nan])]
    df.drop(columns=['remote'], inplace=True)

    # filter for negative keywords
    for keyword in config['NEGATIVE_KEYWORDS']:
        df = df[~df["title"].str.contains(keyword, case=False)]

    # drop unnecessary columns
    df.drop(columns=['start', 'location'], inplace=True)

    return df


def merge_dfs():
    """ merge all dataframes as one in /output """
    df = pd.DataFrame()
    for file in os.listdir('output/websites'):
        if file.endswith('.csv'):
            df = pd.concat([df, pd.read_csv(f'output/websites/{file}')])

    df.drop_duplicates(inplace=True)
    df.to_csv('output/all.csv', index=False)

    return df


if __name__ == '__main__':
    df = merge_dfs()
    filtered_df = filter_data(df)
    filtered_df.to_csv('output/filtered.csv', index=False)