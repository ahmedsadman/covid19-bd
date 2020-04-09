import os
import json
import math
from tabula import read_pdf
import requests


class DataProvider:
    def __init__(self, dest=os.path.join("application", "provider", "mydata.pdf")):
        self.url = os.environ.get("REPORT_URL")
        self.dest = dest

    def download(self):
        data = requests.get(self.url)

        with open(self.dest, "wb") as f:
            f.write(data.content)

    def process_data(self, page=1):
        df = read_pdf(self.dest, pages=1)
        df = df[0]
        data = df.to_dict()
        result = []

        for (l, f) in zip(data["District/City"].values(), data["No. of case"].values()):
            if math.isnan(f) or (type(l) == float and math.isnan(l)):
                continue
            pair = (l, int(f))
            result.append(pair)

        return result

    def cleanup(self):
        os.remove(self.dest)

    def run_update(self):
        self.download()
        data = self.process_data()
        self.cleanup()
        return data
