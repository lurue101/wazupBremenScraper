import requests
from bs4 import BeautifulSoup
import json
import re


class BaseScraper:

    def request_soup_page(self, url: str) -> BeautifulSoup:
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        return soup

    def events_to_json(self, events: list[dict], output_file_path: str):
        if output_file_path[-5:] != ".json":
            output_file_path += ".json"
        with open(output_file_path, "w") as outfile:
            json.dump(events, outfile)

    def match_date(self, date_text: str):
        match = re.search(r"(\d+\.\d+\.\d+)", date_text)
        return match.group()

    def scrape_events_meta(self) -> list[dict]:
        raise NotImplementedError("Implement this in every class")

    def export_scraped_events_as_json(self):
        raise NotImplementedError("Implement this in every class")


class KukoonScraper(BaseScraper):

    def scrape_events_meta(self) -> list[dict]:
        soup = self.request_soup_page("https://kukoon.de/de/events")
        events = []
        for event_item in soup.find_all("div", class_="event-item"):
            event = {}

            # Get the author(s)
            author_s = event_item.find("div", class_="card-title").find(
                "div", class_="h6-subtitle d-flex"
            )
            event["author_s"] = author_s.text.strip() if author_s else None

            # Get the event name and URL
            title_tag = event_item.find("div", class_="card-title").find("a")
            event["title"] = title_tag.text.strip()
            event["url"] = "https://kukoon.de" + title_tag["href"]

            # Get the date and time
            meta_info = event_item.find("div", class_="meta-info-short")
            date_time = meta_info.find_all("div")

            event["date"] = self.match_date(date_time[0].text.strip())
            event["time"] = date_time[1].find("time").text.strip()
            event["org"] = "Kukoon"
            events.append(event)
        return events


class LagerhausScraper(BaseScraper):

    def scrape_events_meta(self) -> list[dict]:
        soup = self.request_soup_page("https://kulturzentrum-lagerhaus.de/lagerhaus")
        events = []

        # Find all event items
        for event_item in soup.find_all("div", id="artikel"):
            event = {}

            # Get the event name and URL
            title_tag = event_item.find("h1").find("a")
            event["title"] = title_tag.text.strip()
            event["url"] = title_tag["href"]

            # Get the date and time
            date_tag = event_item.find("span", id="datum_global")
            time_tag = date_tag.find_next("span", class_="zeit")
            event["date"] = date_tag.text.strip()
            event["time"] = time_tag.text.strip()
            if event["time"][:2] == "/ ":
                event["time"] = event["time"][2:]

            # Get the description
            description_tag = (
                event_item.find("div", id="artikeltext").find_all("p")[-1].text.strip()
            )
            event["description"] = (
                description_tag.text.strip()
                if description_tag
                else "No description available"
            )
            event["org"] = "Lagerhaus"
            events.append(event)
        return events
