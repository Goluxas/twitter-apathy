import os
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager

from dotenv import load_dotenv


def get_promoted_tweets(driver: webdriver) -> list:
    tweets = driver.find_elements(By.CSS_SELECTOR, "article[data-testid='tweet']")

    return filter(is_promoted, tweets)


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
        tweets = get_promoted_tweets(driver)
        print(list(tweets))
        # Click Not Interested
        # Log Success or Failure
        # Trigger infinite scroll
        # Repeat until interrupted

        # NOTE: May want to periodically refresh the page to avoid memory issues from loading too many tweets


if __name__ == "__main__":
    load_dotenv()

    profile_path = os.getenv("PROFILE_PATH")
    twitter_username = os.getenv("TWITTER_USER")
    twitter_password = os.getenv("TWITTER_PASS")
    main(profile_path, twitter_username, twitter_password)
