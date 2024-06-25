import os
import sys
import unittest

from datetime import datetime, timedelta

TEST_SUB_DIR = os.path.dirname(os.path.realpath(__file__))

TEST_DATA_DIR = os.path.join(TEST_SUB_DIR, "data")

if __name__ == "__main__":
    TESTS_DIR = os.path.dirname(TEST_SUB_DIR)
    REPO_DIR = os.path.dirname(TESTS_DIR)
    sys.path.insert(0, REPO_DIR)

from backupnow import (  # noqa: E402
    echo0,
)

from backupnow.taskmanager import (
    TMTimer,
    TaskManager,
)

from backupnow.bnsettings import settings
# , Settings


class TestBackupGoNowCmd(unittest.TestCase):
    src = os.path.join(TEST_DATA_DIR, "source1")

    source1_subtree = [  # same in test_rsync.py
        "sub folder 1",
        os.path.join("sub folder 1", "some other text file.txt"),
        "image-from-rawpixel-id-2258263-jpeg.jpg",
        "some file with text.txt",
    ]

    def __init__(self, *args, **kwargs):
        # super(TestBackupGoNowCmd).__init__()
        unittest.TestCase.__init__(self, *args, **kwargs)
        # self.src = TestBackupGoNowCmd.src

    def test_time_until(self):
        now = datetime(year=2024, month=6, day=20, hour=12, minute=0, second=0)
        timerdict = {
            "time": "12:01",
            "span": "daily",
            "commands": ["*"],
        }
        timer = TMTimer(timerdict=timerdict)
        delta = timer.time_until(now=now)
        seconds = int(delta.total_seconds())
        minutes = int(seconds/60)
        self.assertEqual(minutes, 1)

        timerdict = {
            "time": "12:00",
            "span": "daily",
            "commands": ["*"],
        }
        timer = TMTimer(timerdict=timerdict)
        delta = timer.time_until(now=now)
        seconds = int(delta.total_seconds())
        minutes = int(seconds/60)
        self.assertEqual(minutes, 0)

        timerdict = {
            "time": "11:59",
            "span": "daily",
            "commands": ["*"],
        }
        timer = TMTimer(timerdict=timerdict)
        delta = timer.time_until(now=now)
        seconds = int(delta.total_seconds())
        minutes = int(seconds/60)
        self.assertEqual(minutes, -1)

    def test_validate_time(self):
        timerdict = settings.default_timerdict()  # ["*"] 12:00 daily
        timer = TMTimer(timerdict=timerdict)
        self.assertEqual(
            timer.validate_time("1:32"),
            "01:32"
        )

        self.assertEqual(
            timer.validate_time("0:00"),
            "00:00"
        )

        self.assertEqual(
            timer.validate_time("00:00"),
            "00:00"
        )

        self.assertEqual(
            timer.validate_time("11:59"),
            "11:59"
        )

        detected = False
        try:
            time = timer.validate_time("13:2")
            echo0("Error: bad value={}".format(time))
        except ValueError:
            detected = True
        self.assertTrue(detected)

        detected = False
        try:
            time = timer.validate_time("24:00")
            echo0("Error: bad value={}".format(time))
        except ValueError:
            detected = True
        self.assertTrue(detected)

        detected = False
        try:
            time = timer.validate_time("21:60")
            echo0("Error: bad value={}".format(time))
        except ValueError:
            detected = True
        self.assertTrue(detected)

        detected = False
        try:
            time = timer.validate_time("-1:00")
            echo0("Error: bad value={}".format(time))
        except ValueError:
            detected = True
        self.assertTrue(detected)

        detected = False
        try:
            time = timer.validate_time("1:-1")
            echo0("Error: bad value={}".format(time))
        except ValueError:
            detected = True
        self.assertTrue(detected)

    def test_tmtask_weekly(self):
        now = datetime(year=2024, month=6, day=20, hour=12, minute=0, second=0)
        # dow_name = now.strftime("%A")
        # print(dow_name)  # Thursday (6/20/2024)
        # ^ For index see INDEX_OF_DOW[dow_name]
        #   (or dow_index_fmt = "%w") in taskmanager.py ("4" for Thursday)
        # mgr = TaskManager()
        timerdict = settings.default_timerdict()  # ["*"] 12:00 daily
        timerdict['time'] = "12:01"
        timerdict['span'] = "weekly"
        timerdict['day_of_week'] = "Thursday"
        timer = TMTimer(timerdict=timerdict)
        # mgr.add_timer(settings.default_backup_name, timer)
        self.assertTrue(not timer.ready(now=now))
        timerdict['time'] = "12:00"
        timer = TMTimer(timerdict=timerdict)
        self.assertTrue(timer.ready(now=now))

        delta = timedelta(days=1)
        earlier = now + delta
        # print("Testing earlier: {} using {} timer"
        #       .format(earlier.strftime("%A"), timerdict['day_of_week']))
        self.assertTrue(not timer.ready(now=earlier))

    def test_taskmanager(self):
        # Test timerdict *and* timer
        timerdict = settings.default_timerdict()  # ["*"] 12:00 daily
        timerdict['time'] = "12:01"
        timerdict['span'] = "daily"
        self.run_taskmanager_daily(timerdict=timerdict)
        timer = TMTimer(timerdict=timerdict)
        self.run_taskmanager_daily(timer=timer)

    def run_taskmanager_daily(self, timerdict=None, timer=None):
        now = datetime(year=2024, month=6, day=20, hour=12, minute=0, second=0)
        mgr = TaskManager()
        if timer:
            mgr.add_timer(settings.default_backup_name, timer)
        else:
            mgr.add_timer_dict(settings.default_backup_name, timerdict)
        self.assertEqual(mgr.get_ready_timers(now=now), {})
        delta = timedelta(minutes=1)
        now += delta
        if not timer:
            timer = TMTimer(timerdict)
        self.assertEqual(
            mgr.get_ready_timers(now=now),
            {
                settings.default_backup_name: timer,
            }
        )

    def test_taskmanager_dict(self):
        #
        mgr = TaskManager()
        timerdict = settings.default_timerdict()  # ["*"] 12:00 daily
        mgr.add_timer_dict(settings.default_backup_name, timerdict)

    def test_tmtask(self):
        # src = self.src
        # tm = TaskManager()
        timerdict = settings.default_timerdict()  # ["*"] 12:00 daily
        timer = TMTimer(timerdict=timerdict)
        now = datetime(year=2024, month=6, day=20, hour=12, minute=0, second=0)
        later = now + timedelta(seconds=60)
        # now = now - timedelta(seconds=59)
        timer.span = "daily"

        timer.time = now.strftime(TMTimer.time_fmt)
        self.assertTrue(timer.ready(now=now))
        # ^ should be True since less than 1 min has passed & second=0

        timer.time = later.strftime(TMTimer.time_fmt)
        self.assertTrue(not timer.ready(now=now))
        # ^ Should not be true since tmtimer time is later

        now = now + timedelta(seconds=60)
        self.assertTrue(timer.ready(now=now))
        # try:
        #     self.assertEqual(
        #         got_subtree,
        #         self.source1_subtree
        #     )
        # except AssertionError:
        #     echo0("expected: {}".format(self.source1_subtree))
        #     echo0("got: {}".format(got_subtree))
        #     raise


if __name__ == "__main__":
    unittest.main()
