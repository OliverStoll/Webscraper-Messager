import os
from time import sleep

from src.scraper import scrape_all_pages
from src.data_cleaner import filter_data
from src.messaging import send_messages_to_all_websites
from src.util.config import config
from undetected_chromedriver.v2 import Chrome


if __name__ == '__main__':
    # TODO: integrate other websites, when they work

    driver = Chrome(use_multiprocessing=True)
    df = scrape_all_pages(driver=driver, scraper_config=config['SCRAPER']['FREELANCE'])
    filtered_df = filter_data(df)
    filtered_df.to_csv('output/filtered.csv', index=False)
    driver.quit()
    driver = Chrome(use_multiprocessing=True)
    send_messages_to_all_websites(driver=driver, websites=['freelance'], df_path='output/filtered.csv')

    driver.quit()
