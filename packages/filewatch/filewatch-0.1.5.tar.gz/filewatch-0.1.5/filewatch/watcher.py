import hashlib
import os
import time

from filewatch.file_observer import file_updated_subject
from filewatch.config import settings

class Watcher(object):
    def __init__(self):
        # A map of filepath keys to their last modified date
        self.files = {}

        self._first_run = True

    def run(self, start_directory=None):
        """Continually check the filesytem until the process ends"""
        while True:
            self.perform_check(start_directory=start_directory)

            interval = float(settings.get('DEFAULT', 'interval'))
            time.sleep(interval)

    def perform_check(self, start_directory=None):
        """Run a check over filesytem.

        :note: If no start directory is supplied then we will begin walking
        from the current working directory.
        """
        if not start_directory:
            start_directory = os.getcwd()

        files_updated = []

        for dirpath, dirnames, filenames in os.walk(start_directory):
            for filename in filenames:
                updated = False
                full_path = os.path.join(dirpath, filename)
                key = self._get_key(full_path)

                file_modified = os.path.getmtime(full_path)

                try:
                    last_changed = self.files[key]
                    updated = last_changed < file_modified

                    if updated:
                        # Update file change time
                        self.files[key] = file_modified
                except KeyError:
                    # We have not seen this file before, add it our dict and
                    # broadcast
                    updated = not self._first_run
                    self.files[key] = file_modified

                if updated:
                    files_updated.append(full_path)

        if files_updated:
            file_updated_subject.notify(file_list=files_updated)

        # Keep track of state
        self._first_run = False

    def _get_key(self, full_path):
        """Build a checksum used to identify this filepath"""
        full_path_checksum = hashlib.sha1(full_path).digest()
        return full_path_checksum
