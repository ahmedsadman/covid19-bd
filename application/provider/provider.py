import os
import json
import math
from tabula import read_pdf
from bs4 import BeautifulSoup as bs
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import time
import urllib.parse as urlparser


class DataProvider:
    def __init__(self, dest=os.path.join("application", "provider", "mydata.pdf")):
        self.website = "http://www.iedcr.gov.bd"
        self.url = urlparser.urljoin(self.website, self.get_url())
        self.dest = dest

    def get_stats(self):
        """Fetch the latest statistics like total positive cases, deaths etc"""
        page = requests.get(self.website)
        soup = bs(page.content, "html.parser")
        table = soup.find("table")
        rows = table.find_all("tr")

        positive_24 = rows[3].find_all("td")[-1].text
        positive_total = rows[4].find_all("td")[-1].text
        test_total = rows[2].find_all("td")[-1].text
        test_24 = rows[1].find_all("td")[-1].text

        centers = soup.select("center>h3")
        centers = [c.text for c in centers if c.text.isdigit()]

        recovered_24 = centers[0]
        recovered_total = centers[1]
        death_24 = centers[2]
        death_total = centers[3]

        data_dict = {
            "positive_24": int(positive_24),
            "positive_total": int(positive_total),
            "recovered_24": int(recovered_24),
            "recovered_total": int(recovered_total),
            "death_24": int(death_24),
            "death_total": int(death_total),
            "test_total": int(test_total),
            "test_24": int(test_24),
        }

        return data_dict

    def get_url(self):
        """Fetch the URL which points to the report file"""
        a_text = os.environ.get("REPORT_TEXT")  # text to search in anchor tag

        s = requests.Session()
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount("http://", HTTPAdapter(max_retries=retries))

        page = s.get(self.website)

        if page.status_code == 200:
            soup = bs(page.content, "html.parser")
            link = soup.find("a", text=a_text)["href"]
            return link

        return None

    def download(self):
        s = requests.Session()
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount("http://", HTTPAdapter(max_retries=retries))
        data = s.get(self.url)

        with open(self.dest, "wb") as f:
            f.write(data.content)

    def populate(self, district_label, count_label, data):
        """Populate the result array with processed data"""
        result = []
        for (l, f) in zip(data[district_label].values(), data[count_label].values()):
            if (type(f) == float and math.isnan(f)) or (
                type(l) == float and math.isnan(l)
            ):
                continue

            # check the count can be converted to int, otherwise it's invalid
            try:
                int(f)
            except ValueError:
                continue

            pair = (l, int(f))
            result.append(pair)
        return result

    def process_data(self, page=1):
        df = read_pdf(self.dest, pages=1)
        data = df[0].to_dict()
        keys = list(data.keys())

        district_label = keys[int(os.environ.get("DISTRICT_LABEL_INDEX"))]
        count_label = keys[int(os.environ.get("COUNT_LABEL_INDEX"))]
        result = self.populate(district_label, count_label, data)

        # we also look at some alternatve columns, as it might also
        # contain some missed data (due to bad parsing/bad PDF formatting)
        district_label = keys[int(os.environ.get("DISTRICT_LABEL_INDEX_ALT"))]
        count_label = keys[int(os.environ.get("COUNT_LABEL_INDEX_ALT"))]
        result += self.populate(district_label, count_label, data)  # concat array

        return result

    def cleanup(self):
        os.remove(self.dest)

    def sync_district_data(self):
        print("LINK: ", self.url)
        self.download()
        data = self.process_data()
        self.cleanup()
        return data
