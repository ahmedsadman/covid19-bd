"""Backgrounds tasks to run"""
from application import create_app
from config import Config
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
from application.models import District, Meta, Stat
from application.provider import DataProvider


def sync_district_data():
    """Fetch latest data from IEDCR reports"""
    try:
        print("Starting Districts sync...")
        if Meta.is_updating():
            print("A sync is already in progress")
            return

        # set updating state to true
        Meta.set_updating("True")

        # download and get updated data
        provider = DataProvider()
        new_data = (
            provider.sync_district_data()
        )  # returns list of tuple as [...(districtName, Count)]
        last_updated = Meta.get_meta("updated_on").value
        last_updated = datetime.strptime(
            last_updated, "%Y-%m-%d %H:%M:%S.%f"
        )  # str -> datetime obj

        # flag to monitor if fetched data has changed
        has_updated = False

        # check the data against database records and update as necessary
        for pair in new_data:
            district = District.find_by_name(pair[0])
            if district:
                if district.count != pair[1]:
                    # count changed from last record
                    # - save previous count
                    # - update new count
                    district.prev_count = district.count
                    district.count = pair[1]
                    has_updated = True
                else:
                    # count did not change
                    # - make count and prev_count same only if last change was 1 day ago
                    update_delta = datetime.utcnow() - last_updated
                    if update_delta.days >= 1:
                        district.prev_count = district.count

                district.save()
            else:
                new_district = District(pair[0], pair[1])
                new_district.save()
                has_updated = True

        # set updating state to False as update is finished
        Meta.set_updating("False")

        if has_updated:
            # set last updated time to now
            Meta.set_last_updated()
            print("District Sync Complete: Fetched latest data")
            return
        print("District Sync Complete: Already up to date")
    except Exception as e:
        Meta.set_updating("False")
        print("Error occured while syncing: ", e)


def sync_stats():
    """Fetch latest stats from IEDCR website"""
    try:
        print("Starting Stats sync...")
        provider = DataProvider()
        data = provider.get_stats()

        stat = Stat.get()

        if not stat:
            print("Stat data not found. Creating...")
            stat = Stat()

        # iteratively update the data
        for attr, value in data.items():
            setattr(stat, attr, value)

        stat.save()
        print("Stats sync complete")
    except Exception as e:
        print("Error occured on Stats update: ", e)


def run_sync_district(app):
    with app.app_context():
        sync_district_data()


def run_sync_stats(app):
    with app.app_context():
        sync_stats()


if __name__ == "__main__":
    app = create_app(Config)
    sched = BlockingScheduler()

    # schedule the job to be run every hour
    # push the app context, because app context is required for background jobs
    sched.add_job(lambda: run_sync_district(app), "interval", hours=2)
    sched.add_job(lambda: run_sync_stats(app), "interval", minutes=65)
    sched.start()
