# Retrieving & Wrangling Data
import requests  # Version 2.27.1
from bs4 import BeautifulSoup  # Version 4.11.1
import pandas as pd  # Version 1.4.2
from datetime import date  # Built-in Python library

# Code refactor
import logging  # Built-in Python library


def scrape_srf_daily_news(url):
    """
    This function takes in the URL from the SRF news page.
    It scrapes this page and returns a dataframe with information on the day's news teasers.

    Required arguments:
    - URL: string, the SRF website to be scraped
    """
    # Request the page's html script
    page = requests.get(url)

    # Then parse it
    soup = BeautifulSoup(page.content, "html.parser")

    # Get the different elements
    teaser_lists = soup.find_all("div",
                                 class_="js-teaser-data")
    kickers = soup.find_all("span", class_="teaser__kicker-text")
    titles = soup.find_all("span", class_="teaser__title")
    leads = soup.find_all("p", class_="teaser__lead")

    # Iterate through the elements and extract the relevant information
    news_snippet_dict = {
        "time_published": [],
        "kicker": [],
        "title": [],
        "lead": []
    }

    for (teaser_list, kicker, title, lead) in zip(teaser_lists, kickers, titles, leads):
        news_snippet_dict["time_published"].append(teaser_list.get("data-date-published"))
        news_snippet_dict["kicker"].append(kicker.get_text())
        news_snippet_dict["title"].append(title.get_text())
        news_snippet_dict["lead"].append(lead.get_text())

    news_snippets_df = pd.DataFrame(news_snippet_dict)

    # Turn the publishing time into a timestamp
    news_snippets_df["time_published"] = pd.to_datetime(news_snippets_df["time_published"])

    # Select only news from this day
    news_snippets_df = news_snippets_df[news_snippets_df["time_published"].dt.date ==
                                        date.today()]

    return news_snippets_df


def main(url, folder_path, filename):
    """
    This function combines the scraping and saving functions.
    It logs the progress and prints out info messages.
    """
    # Start logging
    logger = logging.getLogger(__name__)

    # Scrape the data
    todays_news_df = scrape_srf_daily_news(url=url)
    logger.info('Data retrieved')

    # Save it
    todays_news_df.to_csv(f"{folder_path}/{filename}")
    logger.info('File saved')


if __name__ == '__main__':
    # Define the required arguments
    srf_news_site = "https://www.srf.ch/news/das-neueste"
    data_folder = "./data/raw"
    file = f"{date.today()}_srf_news_snippets.csv"

    # Configure the logging
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # Run the main function
    main(url=srf_news_site, folder_path=data_folder, filename=file)
