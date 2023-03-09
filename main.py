import os
import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
from dotenv import load_dotenv
from loguru import logger


def get_tweets(driver: webdriver) -> list:
    tweets = driver.find_elements(By.CSS_SELECTOR, "article[data-testid='tweet']")

    return tweets


def is_promoted(tweet) -> bool:
    spans = tweet.find_elements(By.CSS_SELECTOR, "span")

    return any("Promoted" in span.text for span in spans)


def get_not_interested_element(driver):
    """The ellipse menu opens outside the tweet scope, so this grabs it and clicks from the global page view"""
    dropdown = driver.find_element(By.CSS_SELECTOR, "div[data-testid='Dropdown']")
    spans = dropdown.find_elements(By.TAG_NAME, "span")

    return [span for span in spans if span.text.upper() == "NOT INTERESTED IN THIS AD"][0]


def check_for_success(driver):
    # NOTE: After more than one ad has been marked, will this still work?
    article = driver.find_element(By.CSS_SELECTOR, 'article[role="article"][tabindex="-1"]')
    spans = article.find_elements(By.TAG_NAME, "span")

    # Success message:
    # Thanks. Twitter will use this to make your timeline better.
    return any(span.text.upper == "THANKS. TWITTER WILL USE THIS TO MAKE YOUR TIMELINE BETTER." for span in spans)


def main(profile_path: str, username: str, password: str):
    # Set up web driver
    options = webdriver.FirefoxOptions()
    options.add_argument("--profile=" + profile_path)
    driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)

    # Load twitter timeline
    # For You or Followed doesn't matter; promoted tweets are displayed on each.
    # Just make sure to disable Ad Block before loading
    # NOTE: This uses a pre-made profile that is already logged into Twitter. Might make the ability to log in on a base profile, but we'll see.
    driver.get("https://twitter.com/home")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "article[data-testid='tweet']")))

    # Main Loop
    # A count of ads marked not interested
    boring_ads = 0
    while True:
        # Get new Promoted Tweets
        tweets = get_tweets(driver)
        tweet_count = len(tweets)
        promoted_tweets = list(filter(is_promoted, tweets))

        logger.debug(f"Found {tweet_count} tweets and {len(promoted_tweets)} promoted tweets.")

        for tweet in promoted_tweets:
            print("in this loop")
            # Get the location of the ellipse menu
            menu = tweet.find_element(By.CSS_SELECTOR, 'div[data-testid="caret"]')
            menu_y = menu.location["y"]
            current_scroll = driver.execute_script("return window.pageYOffset + window.innerHeight")
            # TODO: replace 50 with menu element height or more
            to_move = menu_y - current_scroll + 100

            # Scroll to tweet
            actions = ActionChains(driver)
            actions.scroll_by_amount(0, to_move)
            actions.perform()

            # Open ellipse menu
            menu.click()

            # Click Not Interested
            # Next TODO: Popup menu may go above this, so select the Not interested in this ad <span> and move to it
            not_interested = get_not_interested_element(driver)
            # actions.move_to_element(not_interested)
            actions.click(not_interested)
            actions.perform()

            # Log Success or Failure
            if check_for_success(driver):
                logger.info("Another uninteresting ad has been squelched")
                boring_ads += 1
            else:
                logger.info("Something went wrong and the ad ignored being told it was uninteresting.")

        # Presumably at this point there are no more visible Promoted tweets
        # Scroll to the bottom and get a fresh set to examine
        logger.debug("All tweets processed, triggering infinite scroll.")
        driver.find_element(By.TAG_NAME, "html").send_keys(Keys.END)
        time.sleep(5)
        # the below needs some tuning so that the next set has finished loading before we proceed
        # WebDriverWait(driver, 10).until(lambda x: len(get_tweets(x)) > tweet_count)

        # NOTE: May want to periodically refresh the page to avoid memory issues from loading too many tweets
        # Seems like Twitter maintains a constant max of about 10-20 tweets, so we can ignore that!


if __name__ == "__main__":
    load_dotenv()

    profile_path = os.getenv("PROFILE_PATH")
    twitter_username = os.getenv("TWITTER_USER")
    twitter_password = os.getenv("TWITTER_PASS")
    main(profile_path, twitter_username, twitter_password)
