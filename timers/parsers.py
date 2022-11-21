from datetime import datetime, timedelta
import re


PARSERS = {}
UNITS_LOOKUP = {
    'd': 'days',
    'h': 'hours',
    'm': 'minutes',
    's': 'seconds'
}


def register(pattern):
    """Add a regex/function pair to the PARSERS global."""
    def inner(parser):
        PARSERS[pattern] = parser
        return parser

    return inner


@register(
    r'^(?P<when>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{6})?)\s+'
    '(?P<what>.+)$')
def iso_parser(what, when):
    """Parse a ISO formatted date phrase combination."""
    return what, datetime.fromisoformat(when)


@register(r'^(?P<what>.+)\s+in\s+(?!.*at)(?P<when>\d.*)$')
def in_parser(what, when):
    """Parse a relative time phrase."""
    now = datetime.now()

    when_parts = re.split(r'\s+|([a-z]+?)(?:s|\s|$)', when.lower())
    when_parts = [p for p in when_parts if p]

    delta = {}
    for duration, units in zip(when_parts[::2], when_parts[1::2]):
        delta[UNITS_LOOKUP[units[0]]] = int(duration)

    return what, now + timedelta(**delta)


@register(r'^(?P<what>.+)\s+(?:at|@?)\s+(?!.*in)(?P<when>\d.*)$')
def at_parser(what, when):
    """Parse an absolute time phrase."""
    match = re.match(r'(?P<hour>\d{1,2})(?::?(?P<minute>\d{2}))?', when)

    if not match:
        raise ValueError('Could not parse time')

    hour, minute = match.groups()
    hour = int(hour)

    now = datetime.now()
    alarm_time = now.replace(
        hour=hour,
        minute=0 if minute is None else int(minute),
        second=0,
        microsecond=0,
    )

    while alarm_time < now:
        alarm_time += timedelta(hours=12)

    return what, alarm_time
