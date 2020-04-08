from flask import current_app as app, request
from application.models import District, Meta
from application.provider import DataProvider


@app.route("/respond")
def respond():
    req = request.get_json()
    d = District(req["name"], req["count"])
    d.save()
    return {"message": "Ok"}


@app.route("/district", methods=["GET"])
def get_district_data():
    data = District.get_all()
    obj = {}
    for d in data:
        d = d.serialize()
        obj[d["name"]] = {"id": d["id"], "count": d["count"]}

    return {"data": obj, "updated_on": Meta.get_meta("updated_on").value}


@app.route("/update", methods=["POST"])
def update():
    # check if an update is in progress
    if Meta.is_updating():
        return {"message": "An update is already in progress"}

    # set updating state to true
    Meta.set_updating("True")

    # download and get updated data
    provider = DataProvider("https://www.iedcr.gov.bd/district_wise_report.pdf")
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
