from flask import abort

from CTFd.utils import get_config
from CTFd.utils.user import get_current_team

import datetime
import time

from .region_times import region_times


def ctftime():
    """ Checks whether it's CTF time or not. """

    team = get_current_team()
    if team is None:
        return False

    if team.region is None:
        return False

    if team.region == 'root':
        return True

    if team.region == '--':
        return abort(403, {'description': 'You are not part of a finalists team for CSAW CTF' })

    [start, end] = region_times[team.region]

    if start:
        start = int(start)
    else:
        start = 0
    if end:
        end = int(end)
    else:
        end = 0

    if start and end:
        if start < time.time() < end:
            # Within the two time bounds
            return True

    if start < time.time() and end == 0:
        # CTF starts on a date but never ends
        return True

    if start == 0 and time.time() < end:
        # CTF started but ends at a date
        return True

    if start == 0 and end == 0:
        # CTF has no time requirements
        return True

    return False


def ctf_paused():
    return get_config('paused')


def ctf_started():
    team = get_current_team()
    if team is None:
        return False

    if team.region is None:
        return False

    [start, end] = region_times[team.region]

    return time.time() > int(start or 0)


def ctf_ended():
    team = get_current_team()
    if team is None:
        return False

    if team.region is None:
        return False

    [start, end] = region_times[team.region]

    if int(end or 0):
        return time.time() > int(end or 0)

    return False


def unix_time(dt):
    return int((dt - datetime.datetime(1970, 1, 1)).total_seconds())


def unix_time_millis(dt):
    return unix_time(dt) * 1000


def unix_time_to_utc(t):
    return datetime.datetime.utcfromtimestamp(t)


def isoformat(dt):
    return dt.isoformat() + 'Z'