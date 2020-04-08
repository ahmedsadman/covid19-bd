from flask import current_app as app, request
from application.models import District


@app.route("/respond")
def respond():
    req = request.get_json()
    d = District(req["name"], req["count"])
    d.save()
    return {"message": "Ok"}


@app.route("/district")
def get_district_data():
    data = District.get_all()
    obj = {}
    for d in data:
        d = d.serialize()
        obj[d["name"]] = {"count": d["count"]}

    return {"data": obj}
