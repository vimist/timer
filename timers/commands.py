import re
from datetime import datetime

from timers import TIMERS
from timers.parsers import PARSERS


TIME_FORMAT = '%H:%M:%S %d/%m/%Y'


def add(phrase):
    """Add a new timer.

    Parameters:
        phrase (str,list): A string (or a list) to convert to a new timer.

    Returns:
        dict: A dictionary with the status and optional message.
    """
    if isinstance(phrase, list):
        phrase = ' '.join(phrase)

    for pattern, parser in PARSERS.items():
        match = re.match(pattern, phrase)

        if match:
            break
    else:
        return {
            'status': 'error',
            'message': f'No parser found for "{phrase}"'
        }

    what, when = parser(**match.groupdict())

    # Insert the timer into the correct position in the list, earliest first
    i = -1
    for i, timer in enumerate(TIMERS):
        if when < timer['when']:
            break
    else:
        i += 1

    TIMERS.insert(i, {'what': what, 'when': when})

    return {'status': 'success'}


def list_timers(parsable, absolute, delta):
    """List the existing timers.

    Parameters:
        parsable (bool): Whether to output the timers in a parsable format. If
            this is specified, the other options are ignored.
        absolute (bool): Whether to print the absolute time the timer is due.
        delta (bool): Whether to print the delta time the timer is due.

    Returns:
        dict: A dictionary with the status and message containing a table of
            timers.
    """
    now = datetime.now()

    max_column_sizes = [0, 0, 0, 0]
    rows = []
    for i, timer in enumerate(TIMERS):
        if parsable:
            columns = [timer['when'].isoformat()]
        else:
            columns = [f'{i+1}:']

        if not parsable and delta:
            seconds = (timer['when'] - now).total_seconds()
            years, seconds = divmod(seconds, 365.25 * 24 * 60 * 60)
            weeks, seconds = divmod(seconds, 7 * 24 * 60 * 60)
            days, seconds = divmod(seconds, 24 * 60 * 60)
            hours, seconds = divmod(seconds, 60 * 60)
            minutes, seconds = divmod(seconds, 60)

            columns.append('')
            columns[-1] += f'{int(years)}y ' if years > 0 else ''
            columns[-1] += f'{int(weeks)}w ' if weeks > 0 else ''
            columns[-1] += f'{int(days)}d ' if days > 0 else ''
            columns[-1] += f'{int(hours)}h ' if hours > 0 else ''
            columns[-1] += f'{int(minutes)}m ' if minutes > 0 else ''
            columns[-1] += f'{int(seconds)}s ' if seconds > 0 else ''
            columns[-1] = columns[-1].strip()

        if not parsable and absolute:
            columns.append(timer['when'].strftime(TIME_FORMAT))

        columns.append(f'{timer["what"]}')
        rows.append(columns)

        # Update the max column sizes if necessary (don't pad the last column)
        for i, column in enumerate(columns[:-1]):
            max_column_sizes[i] = max(max_column_sizes[i], len(column))

    # Build the table
    table = ''
    for i, row in enumerate(rows):
        for j, field in enumerate(row):
            table += f'{field:{max_column_sizes[j]+2}s}'

        if i < len(rows) - 1:
            table += '\n'

    return {'status': 'success', 'message': table}


def remove(timer_index):
    """Remove a timer.

    Parameters:
        timer_index (int): The index of the timer to remove.

    Returns:
        dict: A dictionary with the status and optional message.
    """
    timer_index -= 1

    if timer_index < len(TIMERS):
        TIMERS.pop(timer_index)
    else:
        return { 'status': 'error', 'message': 'No such timer' }

    return { 'status': 'success' }


def unknown_action(function_name, **kwargs):
    """Executed if the action the client requested could not be found.

    Parameters:
        function_name (str): The name of the function the client requested.
        **kwargs (dict): The arguments passed to the function.

    Returns:
        dict: A dictionary with the status and optional message.
    """
    return {
        'status': 'error',
        'message': f'Unknown action "{function_name}" with arguments {kwargs}'
    }
