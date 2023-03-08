from pathlib import Path

from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager


def get_promoted_tweets() -> list:
    raise NotImplementedError


def is_promoted(tweet) -> bool:
    raise NotImplementedError


def click_ellipse_menu(tweet):
    raise NotImplementedError


def click_not_interested():
    """The ellipse menu opens outside the tweet scope, so this grabs it and clicks from the global page view"""
    raise NotImplementedError


def trigger_infinite_scroll():
    raise NotImplementedError


def main():
    # Set up web driver
    driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))

    # Load twitter timeline
    # For You or Followed doesn't matter; promoted tweets are displayed on each.
    # Just make sure to disable Ad Block before loading
    driver.get("https://twitter.com/home")

    # Main Loop

    # Get new Promoted Tweets
    # Click Not Interested
    # Log Success or Failure
    # Trigger infinite scroll
    # Repeat until interrupted

    # NOTE: May want to periodically refresh the page to avoid memory issues from loading too many tweets
    pass


if __name__ == "__main__":
    main()
