from datetime import datetime, timedelta

"""
    Generate the start datetimes of fixed-length slots within a time block
    on a given date.

    Parameters:
      date          -- a date (the day the block falls on)
      start_time    -- a time (block start, e.g. 14:00)
      end_time      -- a time (block end, e.g. 15:00)
      slot_minutes  -- int, length of each slot in minutes (default 15)

    Returns:
      A list of datetime objects, each representing the start of a slot.
      If the block ends before it starts, or has zero length, returns [].
      A slot is only included if it fits entirely within the block; partial
      trailing slots are dropped (e.g. a 40-min block at 15-min slots
      yields 2 slots, not 3)
    """

def generate_slots(date, start_time, end_time, slot_minutes=15):

    if end_time <= start_time:
        return []
    slot = timedelta(minutes=slot_minutes)
    current = datetime.combine(date, start_time)
    block_end = datetime.combine(date, end_time)
    slots = []
    while current + slot <= block_end:
        slots.append(current)
        current += slot
    return slots