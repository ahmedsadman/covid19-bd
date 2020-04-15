"""Backgrounds tasks to run"""
from application import create_app
from config import Config
from apscheduler.schedulers.blocking import BlockingScheduler
from application.models import District, Meta
from application.provider import DataProvider


def sync_data():
    try:
        print("Starting sync...")
        if Meta.is_updating():
            print("A sync is already in progress")
            return

        # set updating state to true
        Meta.set_updating("True")

        # download and get updated data
        provider = DataProvider()
        new_data = (
            provider.run_update()
        )  # returns list of tuple as [...(districtName, Count)]

        # check the data against database records and update as necessary
        has_updated = False
        for pair in new_data:
            district = District.find_by_name(pair[0])
            if district:
                if district.count != pair[1]:
                    district.count = pair[1]
                    district.save()
                    has_updated = True
            else:
                new_district = District(pair[0], pair[1])
                new_district.save()
                has_updated = True

        # set updating state to False as update is finished
        Meta.set_updating("False")

        if has_updated:
            # set last updated time to now
            Meta.set_last_updated()
            print("Sync Complete: Fetched latest data")
            return
        print("Sync Complete: Already up to date")
    except Exception as e:
        Meta.set_updating("False")
        print("Error occured while syncing: ", e)


def run_sync_data(app):
    """Fetch latest data from IEDCR reports"""
    with app.app_context():
        sync_data()


if __name__ == "__main__":
    app = create_app(Config)
    sched = BlockingScheduler()

    # schedule the job on 15:00, 17:00 and 20:00 UTC time everyday
    # push the app context, because some parts of the task needs the context
    sched.add_job(lambda: run_sync_data(app), "cron", hour="15, 16, 17, 20")
    sched.start()
