from datetime import datetime
from datetime import datetime, timedelta

TOTAL_WORKING_HOURS_IN_DAY = float(8)

DAYS_IN_WORKING_WEEK = float(5)

TOTAL_WORKING_HOURS_IN_WEEK = TOTAL_WORKING_HOURS_IN_DAY * DAYS_IN_WORKING_WEEK

MINIMUM_MEETING_LENGHT_MINS = float(15)

MAX_NUMBER_OF_MEETINGS = float(50)

ROUNDING_DEFAULT = 1

def calc_average_meeting_length(total_meeting_hours, total_meetings, rounding: int = ROUNDING_DEFAULT):
    if total_meetings == 0:
        return 0
    return round(float(total_meeting_hours / total_meetings * 60), rounding)

def calc_average_meeting_block_length(total_meeting_hours, total_meeting_blocks, rounding: int = ROUNDING_DEFAULT):
    if total_meeting_blocks == 0:
        return 0
    return round(float(total_meeting_hours / total_meeting_blocks * 60), rounding)

def calc_meeting_time(total_meeting_hours, as_prop: bool = False, rounding: int = ROUNDING_DEFAULT):
    val = total_meeting_hours
    if as_prop:
        val = val / TOTAL_WORKING_HOURS_IN_WEEK
    return round(float(val), rounding)

def calc_lost_productivity(total_meeting_blocks, context_switch_cost_mins, as_prop: bool = False, rounding: int = ROUNDING_DEFAULT):
    val = round(float(total_meeting_blocks * context_switch_cost_mins / 60), rounding)
    if as_prop:
        val = val / TOTAL_WORKING_HOURS_IN_WEEK
    return round(float(val), rounding)

def calc_productive_time_lost(total_meeting_hours, total_meeting_blocks, context_switch_cost_mins, as_prop: bool = False, rounding: int = ROUNDING_DEFAULT):
    val = total_meeting_hours + calc_lost_productivity(total_meeting_blocks, context_switch_cost_mins)
    if as_prop:
        val = val / TOTAL_WORKING_HOURS_IN_WEEK
    return round(float(val), rounding)

def calc_potential_productive_time(total_meeting_hours, total_meeting_blocks, context_switch_cost_mins, as_prop: bool = False, rounding: int = ROUNDING_DEFAULT):
    val = TOTAL_WORKING_HOURS_IN_WEEK - calc_productive_time_lost(total_meeting_hours, total_meeting_blocks, context_switch_cost_mins)
    if as_prop:
        val = val / TOTAL_WORKING_HOURS_IN_WEEK
    return round(float(val), rounding)

def get_week_start(dt_object: datetime):
    start = dt_object - timedelta(days=dt_object.weekday())
    return start.strftime('%d %B %Y')
