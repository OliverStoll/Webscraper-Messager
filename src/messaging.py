""" File that contains the messaging logic, to send (bulk) messages to the scraped & filtered listings """

import pandas as pd
from selenium.webdriver.common.by import By
from time import sleep

from src.util.config import config
from src.scraper import open_link_with_cookies


def perform_messaging_actions(driver, actions):
    """
    Perform a series of customizable actions to send the message. The actions are specified in the config file.

    Currently, the following actions are supported:
    - click: click on an element.
        - Gracefully fails, if action does not contain 'required'.
    - click_all: click on a list of elements
    - scroll_to: scroll to a certain amount of pixels
    - text_input: enter text into an input field.
        - Takes either 'input_text' or 'input_file' (res/documents) as input.
    - dropdown: first clicks on a dropdown, then selects an option
    """

    for action in actions:
        if 'selector' in action:
            elements = driver.find_elements(by=By.CSS_SELECTOR, value=action['selector'])
        if action['action'] == 'click':
            try:
                elements[0].click()
            except Exception as e:
                if 'required' in action:
                    raise Exception(action['selector'] if 'selector' in action else None, e)
        if action['action'] == 'click_all':
            for element in elements:
                element.click()
        if action['action'] == 'scroll_to':
            driver.execute_script(f"window.scrollTo(0, {action['amount']});")
            sleep(1)
        if action['action'] == 'text-input':
            if 'input_file' in action:
                with open(f"res/documents/{action['input_file']}", 'r') as f:
                    text = f.read()
            elif 'input_text' in action:
                text = action['input_text']
            else:
                raise Exception('No text input specified')
            elements[0].send_keys(text)
        if action['action'] == 'dropdown':
            elements[0].click()
            sleep(1)
            driver.find_element(By.CSS_SELECTOR, action['option']).click()


def send_message_to_detail_page(driver, message_config, link):
    """
    Send a message to a link (detail page), using the specified actions in the message_config. \n
    Also extracts the content of the detail page.
    Raises an exception if the message could not be sent.
    """
    open_link_with_cookies(driver=driver, link=link)
    if 'sleep_before' in message_config:
        sleep(message_config['sleep_before'])

    # check if element indicates that the project is already applies
    if 'already_applied' in message_config:
        try:
            element = driver.find_element(By.CSS_SELECTOR, message_config['already_applied'])
            if element:
                raise Exception('Already applied')
        except:
            pass

    # extract the content of the detail page
    content = driver.find_element(By.CSS_SELECTOR, message_config['content_selector']).text

    # TODO: use a python module to detect the language

    # perform all actions to send the message
    try:
        perform_messaging_actions(driver, message_config['actions'])
    except Exception as e:
        raise Exception(e)

    # sleep to give the page time to register the message
    if 'sleep_after' in message_config:
        sleep(message_config['sleep_after'])


def send_all_messages_for_website(driver, website_df, message_config):
    """ Send a message to all links in the dataframe. Only handles one website/message-config at a time. """
    success_counter = 0

    print(f"Sending messages to {len(website_df)} links.")
    if 'max_messages' in message_config:
        print(f"Max successful messages: {message_config['max_messages']}")

    for index, row in website_df.iterrows():
        try:
            send_message_to_detail_page(driver, message_config, row['link'])
            success_counter += 1
        except Exception as e:
            print('ERROR: Could not send message', row['link'], e)
        finally:
            print(f"{index+1}/{len(website_df)} messages sent. Successful: {success_counter}")
        if 'max_messages_successful' in message_config and success_counter >= message_config['max_messages_successful']:
            break
        if 'max_messages_total' in message_config and index >= message_config['max_messages_total']:
            break

    print(f"Sent {success_counter} messages")


def send_messages_to_all_websites(websites, df_path, driver):
    """ Send a message to all links in the dataframe. Handles all websites/message-configs at once. """

    df = pd.read_csv(df_path)
    for website in websites:
        website_df = df[df['website'].isin(websites)]
        message_config = config['MESSAGER'][website.upper()]
        send_all_messages_for_website(driver, website_df=website_df, message_config=message_config)


if __name__ == '__main__':
    websites = ['freelance']
    send_messages_to_all_websites(websites=websites, df_path='output/filtered.csv')