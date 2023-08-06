import sys
import time
import collections
from spanner.decorators import validate_args


class Timer:

    def __init__(self, total_iterations, label, seconds_between_updates=5):
        self.total_iterations = total_iterations
        self.label = label
        self.seconds_between_updates = seconds_between_updates
        self.start_time = self.last_update_time = time.time()

    def tick(self):
        self.iterations_elapsed += 1

        now = time.time()
        if (self.iterations_elapsed >= self.total_iterations) or \
           (now - self.last_update_time > self.seconds_between_updates):
            self.print_status()

    def print_status(self):
        now = time.time()

        if self.iterations_elapsed == self.total_iterations:
            status = '%d loops completed in %s.' % (self.total_iterations,
                                                    seconds_to_time_string(now - self.start_time))
        elif self.iterations_elapsed > self.total_iterations:
            status = 'Timer overrun!  %d loops expected, now at %d and counting' % (self.total_iterations,
                                                                                    self.iterations_elapsed)
        else:
            # project time to completion, assuming each iteration takes the same amount of time
            self.last_update_time = now
            seconds_elapsed = now - self.start_time
            seconds_remaining = self.seconds_remaining()
            status = '%d/%d loops completed in %s. %s remaining.' % (self.iterations_elapsed, self.total_iterations,
                                                                     seconds_to_time_string(seconds_elapsed),
                                                                     seconds_to_time_string(seconds_remaining))

        if self.label is not None:
            print '%s: %s' % (self.label, status)
        else:
            print status
        sys.stdout.flush()

    def seconds_per_iteration(self):
        now = time.time()
        return (now - self.start_time) / self.iterations_elapsed

    def seconds_remaining(self):
        return self.seconds_per_iteration() * (self.total_iterations - self.iterations_elapsed)


def seconds_to_time_string(seconds):
    hours = int(seconds / (60 * 60))
    minutes = int(seconds % (60 * 60) / 60)
    seconds = int(seconds % 60)

    if hours > 0:
        return '%d:%02d:%02d hours' % (hours, minutes, seconds)
    elif minutes > 0:
        return '%d:%02d minutes' % (minutes, seconds)
    elif seconds == 1:
        return '1 second'
    else:
        return '%d seconds' % seconds


@validate_args(collections.Iterable, str, int)
def timer_for_iterable(iterable, label=None, seconds_between_updates=5):
    return Timer(len(iterable), label, seconds_between_updates)


@validate_args(int, str, int)
def timer(total_iterations, label=None, seconds_between_updates=5):
    return Timer(total_iterations, label, seconds_between_updates)
