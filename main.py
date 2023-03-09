import os
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


def click_ellipse_menu(tweet):
    raise NotImplementedError


def click_not_interested():
    """The ellipse menu opens outside the tweet scope, so this grabs it and clicks from the global page view"""
    raise NotImplementedError


def trigger_infinite_scroll():
    raise NotImplementedError


def main(profile_path: str, username: str, password: str):
    # Set up web driver
    options = webdriver.FirefoxOptions()
    options.add_argument("--profile=" + profile_path)
    driver = webdriver.Firefox(
        service=FirefoxService(GeckoDriverManager().install()), options=options
    )

    # Load twitter timeline
    # For You or Followed doesn't matter; promoted tweets are displayed on each.
    # Just make sure to disable Ad Block before loading
    # NOTE: This uses a pre-made profile that is already logged into Twitter. Might make the ability to log in on a base profile, but we'll see.
    driver.get("https://twitter.com/home")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "article[data-testid='tweet']")
        )
    )

    # Main Loop
    while True:
        # Get new Promoted Tweets
        tweets = get_tweets(driver)
        tweet_count = len(tweets)
        promoted_tweets = list(filter(is_promoted, tweets))

        logger.debug(
            f"Found {tweet_count} tweets and {len(promoted_tweets)} promoted tweets."
        )

        for tweet in promoted_tweets:
            print("in this loop")
            # Get the location of the ellipse menu
            menu = tweet.find_element(By.CSS_SELECTOR, 'div[data-testid="caret"]')
            menu_y = menu.location["y"]

            # Scroll to tweet
            actions = ActionChains(driver)
            actions.scroll_by_amount(delta_x=0, delta_y=menu_y)
            actions.move_to_element(menu)
            actions.perform()

            menu.click()

            actions.click()
            actions.perform()
            # Click Not Interested

            # Log Success or Failure
            # Thanks. Twitter will use this to make your timeline better.
            # Trigger infinite scroll
            # Repeat until interrupted

        # Presumably at this point there are no more visible Promoted tweets
        # Scroll to the bottom and get a fresh set to examine
        logger.debug("All tweets processed, triggering infinite scroll.")
        driver.find_element(By.TAG_NAME, "html").send_keys(Keys.END)
        WebDriverWait(driver, 10).until(lambda x: len(get_tweets(x)) > tweet_count)

        # NOTE: May want to periodically refresh the page to avoid memory issues from loading too many tweets


if __name__ == "__main__":
    load_dotenv()

    profile_path = os.getenv("PROFILE_PATH")
    twitter_username = os.getenv("TWITTER_USER")
    twitter_password = os.getenv("TWITTER_PASS")
    main(profile_path, twitter_username, twitter_password)
