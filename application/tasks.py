"""Backgrounds tasks to run"""
from application import create_app
from config import Config
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
from application.models import District, Meta, Stat
from application.provider import DataProvider
from application.logger import Logger


def sync_district_data(logger):
    """Fetch latest data from IEDCR reports"""
    try:
        logger.info("Starting sync of district data")
        if Meta.is_district_syncing():
            logger.info("A district sync is already in progress")
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

        logger.debug(f"Has updated = {has_updated}")
        if has_updated:
            # set last updated time to now
            Meta.set_last_district_sync()
            logger.info("District sync complete (fetched new data)")
            return
        logger.info("District sync complete (already up-to-date)")
    except Exception as e:
        Meta.set_district_syncing(False)
        logger.error(f"District sync failed with error: {e}")


def sync_stats(logger):
    """Fetch latest stats from IEDCR website"""
    try:
        logger.info("Starting sync of stats data")
        if Meta.is_stats_syncing():
            logger.info("A stats sync is already in progress")
            return

        Meta.set_stats_syncing(True)

        provider = DataProvider()
        data = provider.get_stats()

        stat = Stat.get()

        # iteratively update the data
        for attr, value in data.items():
            setattr(stat, attr, value)

        stat.save()
        Meta.set_stats_syncing(False)
        logger.info("Stats sync complete")
    except Exception as e:
        Meta.set_stats_syncing(False)
        logger.error(f"Stats sync failed with error: {e}")


def run_sync_district(logger):
    with app.app_context():
        sync_district_data(logger)


def run_sync_stats(logger):
    with app.app_context():
        sync_stats(logger)


if __name__ == "__main__":
    app = create_app(Config)
    logger = Logger.create_logger(__name__)
    sched = BlockingScheduler()

    # schedule the job to be run every hour
    # push the app context, because app context is required for background jobs
    # sched.add_job(lambda: run_sync_district(logger), "interval", minutes=30)
    sched.add_job(lambda: run_sync_stats(logger), "interval", minutes=18)
    sched.start()
