from ntscraper import Nitter
import re
import time
import pickle
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

# Function to extract username from the Twitter link
def extract_username(url):
    match = re.search(r"https://x.com/([^/]+)", url)
    if match:
        return match.group(1)
    else:
        raise ValueError("Invalid URL format. Please enter a URL in the format: https://x.com/username")

# Function to fetch tweets with retries
def fetch_tweets_with_retry(username, max_retries=3):
    scraper = Nitter(log_level=1, skip_instance_check=False)
    attempt = 0
    while attempt < max_retries:
        try:
            tweets = scraper.get_tweets(username, mode="user", number=50)
            if 'tweets' in tweets:
                return tweets
            else:
                print("No tweets found or error fetching tweets.")
        except Exception as e:
            print(f"An error occurred: {e}")
        attempt += 1
        time.sleep(5)  # Wait before retrying
    return None

# Function to initialize the Selenium WebDriver
def initialize_driver():
    # Define user agent
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"

    # Set Chrome options
    options = webdriver.ChromeOptions()
    options.add_argument(f'user-agent={user_agent}')
    options.add_argument("--start-maximized")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument("--disable-extensions")
    options.add_argument("--proxy-server='direct://'")
    options.add_argument("--proxy-bypass-list=*")
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')

    # Path to chromedriver.exe
    driver_path = r"C:\Users\ravin\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"

    # Initialize the ChromeDriver service
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=options)
    return driver

# Function to load cookies from the pickle file
def load_cookies(driver, filepath):
    if os.path.exists(filepath):
        with open(filepath, 'rb') as file:
            cookies = pickle.load(file)
            # Ensure we are on the correct domain
            driver.get('https://x.com/')
            for cookie in cookies:
                if cookie['domain'] not in ['x.com', '.x.com']:
                    continue
                driver.add_cookie(cookie)

# Function to report a tweet
def report_tweet(driver, tweet_url):
    driver.get(tweet_url)
    time.sleep(3)

    try:
        # Click on the "More" button (three dots)
        more_button_xpath = '//button[@aria-label="More" and @role="button"]'
        more_button = driver.find_element(By.XPATH, more_button_xpath)
        more_button.click()
        time.sleep(3)

        # Click on the "Report" button from the dropdown
        report_button_xpath = "//div[@role='menuitem']//span[contains(text(), 'Report')]"
        report_button = driver.find_element(By.XPATH, report_button_xpath)
        report_button.click()
        time.sleep(3)

        # Select the "Hate" option
        hate_radio_button_xpath = "//label//span[contains(text(), 'Hate')]/ancestor::label//input[@type='radio']"
        hate_radio_button = driver.find_element(By.XPATH, hate_radio_button_xpath)
        hate_radio_button.click()  # Click the radio button
        time.sleep(3)

        # Click the "Next" button
        next_button = driver.find_element(By.CSS_SELECTOR, "button[data-testid='ChoiceSelectionNextButton']")
        next_button.click()
        time.sleep(3)

        # Select the "Dehumanization" radio button
        dehumanization_radio_button_xpath = "//label//span[contains(text(), 'Dehumanization')]/ancestor::label//input[@type='radio']"
        dehumanization_radio_button = driver.find_element(By.XPATH, dehumanization_radio_button_xpath)
        dehumanization_radio_button.click()  # Click the "Dehumanization" radio button
        time.sleep(3)

        # Click the "Submit" button
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[data-testid='ChoiceSelectionNextButton']")
        submit_button.click()  # Click the "Submit" button
        time.sleep(3)

    except Exception as e:
        print(f"An error occurred while reporting the tweet: {e}")

def main():
    url = input("Enter user link: ")

    # Extract the username from the URL
    try:
        username = extract_username(url)
    except ValueError as e:
        print(e)
        return

    # Fetch the latest tweets from the specified user with retries
    tweets = fetch_tweets_with_retry(username)
    if tweets is None:
        return

    # Filter out only the tweets that are not retweets and not pinned
    non_retweet_non_pinned_links = [
        tweet['link'] for tweet in tweets['tweets'] if not tweet['is-retweet'] and not tweet['is-pinned']
    ]

    if not non_retweet_non_pinned_links:
        print("No non-retweet, non-pinned tweets found.")
        return

    # Initialize the Selenium WebDriver
    driver = initialize_driver()

    try:
        # Navigate to the target domain
        driver.get('https://x.com/')
        time.sleep(3)  # Allow time for the page to load

        # Try to load cookies if they exist
        if os.path.exists('twitter_cookies.pkl'):
            load_cookies(driver, 'twitter_cookies.pkl')
            driver.refresh()  # Refresh to apply cookies
            time.sleep(3)

        # Report each tweet
        for tweet_url in non_retweet_non_pinned_links[:20]:  # Process only the first 20 tweets
            report_tweet(driver, tweet_url)

    finally:
        # Close the browser after actions are completed
        driver.quit()

if __name__ == "__main__":
    main()
