from datetime import datetime, timedelta
from humanize import naturaltime


def print_progress_bar(iteration: int, total: int, starting_time=None, decimals=1, length=50, fill='█') -> None:
    """ Call in a loop to create terminal progress bar.

    Shamelessly stolen from: https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)

    runtime = ''
    if starting_time:
        runtime = naturaltime(datetime.now() - starting_time)

    ending_time = ''
    if starting_time:
        seconds_from_start = (datetime.now() - starting_time).total_seconds()
        per_second = int(iteration / seconds_from_start)
        try:
            ending_time = naturaltime(timedelta(seconds=(-1 * ((total-iteration) / per_second))))
        except (TypeError, ZeroDivisionError):
            ending_time = '???'

    print(
        f'\r{iteration} |{bar}| {percent}% {total} '
        f'[Started: {runtime} Rate: {per_second:d}/per sec Finished: {ending_time}]',
        end='\r')

    # Print New Line on Complete
    if iteration == total:
        print()
