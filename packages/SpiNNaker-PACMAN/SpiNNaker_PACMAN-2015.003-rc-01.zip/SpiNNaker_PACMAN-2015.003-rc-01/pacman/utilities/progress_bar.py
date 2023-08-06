from __future__ import print_function
import logging
import sys
import math
logger = logging.getLogger(__name__)


class ProgressBar(object):
    MAX_LENGTH_IN_CHARS = 60

    def __init__(self, total_number_of_things_to_do,
                 string_describing_what_being_progressed):
        self.total_number_of_things_to_do = total_number_of_things_to_do
        self.currently_completed = 0
        self.chars_per_thing = None
        self.last_update = 0
        self.chars_done = 0
        self.string = string_describing_what_being_progressed

        self.create_initial_progress_bar(
            string_describing_what_being_progressed)

    def update(self, amount_to_add=1):
        self.currently_completed += amount_to_add
        self.check_differences()

    def create_initial_progress_bar(self,
                                    string_describing_what_being_progressed):
        if self.total_number_of_things_to_do == 0:
            self.chars_per_thing = ProgressBar.MAX_LENGTH_IN_CHARS
        else:
            self.chars_per_thing = (float(ProgressBar.MAX_LENGTH_IN_CHARS) /
                                    float(self.total_number_of_things_to_do))
        print("Progress {}".format(string_describing_what_being_progressed),
              file=sys.stderr)
        print("|0                           50%                         100%|",
              file=sys.stderr)
        print(" ", end="", file=sys.stderr)
        self.check_differences()

    def check_differences(self):
        expected_chars_done = math.floor(self.currently_completed
                                         * self.chars_per_thing)
        if self.currently_completed == self.total_number_of_things_to_do:
            expected_chars_done = ProgressBar.MAX_LENGTH_IN_CHARS
        while self.chars_done < expected_chars_done:
            print("=", end='', file=sys.stderr)
            self.chars_done += 1
        sys.stderr.flush()

    @staticmethod
    def end():
        print("", file=sys.stderr)

    def __repr__(self):
        return "progress bar for {}".format(self.string)
