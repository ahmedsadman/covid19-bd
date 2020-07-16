"""Backgrounds tasks to run"""
from application import create_app
from config import Config
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
from application.models import District, Meta, Stat
from application.provider import DataProvider
from application.logger import Logger


def sync_district_data():
    """Fetch latest data from IEDCR reports"""
    try:
        # For some unknown reason, Logger.createLogger(__name__),
        # where __name__ == "application.tasks" doesn't bind
        # the handler. After some debugging, I found that anything
        # prefixing "application.*" doesn't work. According to
        # Logger.create_logger(), it assumes that a handler is
        # already binded, although it's not.

        # For the other parts it doesn't cause any problem. For example,
        # when the logger is created inside DataProvider module, the name
        # "application.provider.*" doesn't cause any problem.

        # This is a weird issue. I will look into this later. For now,
        # I will name it "tasks"
        logger = Logger.create_logger("tasks")
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

        # differnece with current time and last updated time
        update_delta = datetime.utcnow() - last_updated

        # check the data against database records and update as necessary
        for pair in new_data:
            # ignore blank data
            if pair[0] == "" or pair[1] == "":
                continue

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
            # set last updated time to now if more than 24hrs
            # the 24hrs constant window helps to better calculate new_count - prev_count
            if update_delta.days >= 1:
                Meta.set_last_district_sync()
                logger.info("Updated last sync time")
            logger.info("District sync complete (fetched new data)")
            return
        logger.info("District sync complete (already up-to-date)")
    except Exception as e:
        Meta.set_district_syncing(False)
        logger.error(f"District sync failed with error: {e}")


def sync_stats():
    """Fetch latest stats from IEDCR website"""
    try:
        logger = Logger.create_logger("tasks")
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


def run_sync_district():
    with app.app_context():
        sync_district_data()


def run_sync_stats():
    with app.app_context():
        sync_stats()


if __name__ == "__main__":
    app = create_app(Config)
    sched = BlockingScheduler()

    # schedule the job to be run every hour
    # push the app context, because app context is required for background jobs
    sched.add_job(run_sync_district, "interval", minutes=30)
    sched.add_job(run_sync_stats, "interval", minutes=18)
    sched.start()
