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
        print("Starting Sync: Districts")
        if Meta.is_district_syncing():
            print("A district sync is already in progress")
            return

        # set updating state to true
        Meta.set_district_syncing(True)

        # download and get updated data
        provider = DataProvider()
        new_data = (
            provider.sync_district_data()
        )  # returns list of tuple as [...(districtName, Count)]
        last_updated = Meta.get_last_district_sync()

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
        Meta.set_district_syncing(False)

        if has_updated:
            # set last updated time to now
            Meta.set_last_district_sync()
            print("Sync Complete: Districts (already up to date)")
            return
        print("Sync Complete: Districts (fetched new data)")
    except Exception as e:
        Meta.set_district_syncing(False)
        print("Error in Sync (District): ", e)


def sync_stats():
    """Fetch latest stats from IEDCR website"""
    try:
        print("Starting Sync: Stats")
        if Meta.is_stats_syncing():
            print("A stats sync is already in progress")
            return

        provider = DataProvider()
        data = provider.get_stats()

        stat = Stat.get()

        # iteratively update the data
        for attr, value in data.items():
            setattr(stat, attr, value)

        stat.save()
        print("Sync Complete: Stats")
    except Exception as e:
        print("Error in Sync (Stats): ", e)


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
