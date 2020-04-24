from flask import current_app as app, request
from application.models import District, Meta, Stat
from application.provider import DataProvider


@app.route("/", methods=["GET"])
def info():
    return {
        "title": "Covid-19 District Wise Data (Bangladesh) - API For Public usage",
        "description": "This pulls data from IEDCR published reports",
        "author_name": "Sadman Muhib Samyo",
        "author_github": "github.com/ahmedsadman",
    }


@app.route("/district", methods=["GET"])
def get_district_data():
    data = District.get_all()

    return {
        "data": [d.serialize() for d in data],
        "updated_on": Meta.get_last_district_sync(),
    }


@app.route("/stats", methods=["GET"])
def get_stats():
    stat = Stat.get()
    return stat.serialize()
