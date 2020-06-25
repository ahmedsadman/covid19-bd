import os
import json
import math
from bs4 import BeautifulSoup as bs
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import time
import urllib.parse as urlparser
from application.logger import Logger


class DataProvider:
    logger = Logger.create_logger(__name__)

    def __init__(self):
        self.stats_data_source = "https://corona.gov.bd/lang/en"
        self.district_report_url = os.environ.get("REPORT_URL")
        self.trans_table = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")

    def get_stats(self):
        """Fetch the latest statistics like total positive cases, deaths etc"""
        page = requests.get(self.stats_data_source)
        soup = bs(page.content, "html.parser")
        counts = soup.select(".live-update-box-wrap-h1>b")

        # process counts - replace bangla digits with english
        for i in range(len(counts)):
            # counts[i] = counts[i].text.translate(self.trans_table)
            counts[i] = int(counts[i].text)

        data_dict = {
            "positive_24": counts[0],
            "positive_total": counts[1],
            "death_24": counts[2],
            "death_total": counts[3],
            "recovered_24": counts[4],
            "recovered_total": counts[5],
            "test_24": counts[6],
            "test_total": counts[7],
        }

        self.logger.debug(data_dict)
        return data_dict

    def parse_district_data(self):
        """Parse the Google Sheets to get district data"""
        page = requests.get(self.district_report_url)
        soup = bs(page.content, "html.parser")
        table = soup.find("table")
        rows = table.find_all("tr")
        result = []

        for rindex, row in enumerate(rows):
            # ignore first two rows and last row because they are headers/totals
            if rindex < 2 or rindex == len(rows) - 1:
                continue

            data = []
            for col in row.find_all("td"):
                # ignore division names column
                if col.has_attr("rowspan"):
                    continue
                data.append(self.sanitize(col.text))

            result.append(data)

        return result

    def sanitize(self, s):
        """sanitize string:
        - by replacing invalid chars with correct ones
        - converting to int if applicable"""
        mapping = {"â€™": "'"}
        for key, val in mapping.items():
            s = s.replace(key, val)

        if s.isdigit():
            s = int(s)
        return s

    def sync_district_data(self):
        return self.parse_district_data()
