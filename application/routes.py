from flask import current_app as app, request
from application.models import District, Meta
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
    obj = {}
    total_infected = 0
    for d in data:
        d = d.serialize()
        obj[d["name"]] = {"id": d["id"], "count": d["count"]}
        total_infected += d["count"]

    return {
        "total_infected": total_infected,
        "data": obj,
        "updated_on": Meta.get_meta("updated_on").value,
    }


@app.route("/update", methods=["POST"])
def update():
    # check if an update is in progress
    try:
        if Meta.is_updating():
            return {"message": "An update is already in progress"}

        # set updating state to true
        Meta.set_updating("True")

        # download and get updated data
        provider = DataProvider()
        new_data = (
            provider.run_update()
        )  # returns list of tuple as [...(districtName, Count)]

        # check the data against database records and update as necessary
        for pair in new_data:
            district = District.find_by_name(pair[0])
            if district:
                if district.count != pair[1]:
                    district.count = pair[1]
                    district.save()
            else:
                new_district = District(pair[0], pair[1])
                new_district.save()

        # set updating state to False as update is finished
        Meta.set_updating("False")

        # set last updated time to now
        Meta.set_last_updated()

        return {"message": "Updated"}
    except Exception as e:
        print("Exception is", e)
        Meta.set_updating("False")
        return {"message": "Update Error"}, 500
