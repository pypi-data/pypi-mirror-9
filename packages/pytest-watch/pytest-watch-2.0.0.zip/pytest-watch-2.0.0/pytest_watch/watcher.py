from __future__ import print_function

import os
import time
import subprocess

from colorama import Fore
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


DEFAULT_EXTENSIONS = ['.py']
CLEAR_COMMAND = 'cls' if os.name == 'nt' else 'clear'
BEEP_CHARACTER = '\a'


class ChangeHandler(FileSystemEventHandler):
    """Listens for changes to files and re-runs tests after each change."""
    def __init__(self, directory=None, auto_clear=False, beep_on_failure=True,
                 onpass=None, onfail=None, extensions=[]):
        super(ChangeHandler, self).__init__()
        self.directory = os.path.abspath(directory or '.')
        self.auto_clear = auto_clear
        self.beep_on_failure = beep_on_failure
        self.onpass = onpass
        self.onfail = onfail
        self.extensions = extensions or DEFAULT_EXTENSIONS

    def on_any_event(self, event):
        if event.is_directory:
            return
        ext = os.path.splitext(event.src_path)[1].lower()
        if ext in self.extensions:
            self.run(event.src_path)

    def run(self, filename=None):
        """Called when a file is changed to re-run the tests with nose."""
        if self.auto_clear:
            subprocess.call(CLEAR_COMMAND, cwd=self.directory, shell=True)
        elif filename:
            print()
            print(Fore.CYAN + 'Change detected in ' + filename + Fore.RESET)
        print()
        print('Running unit tests...')
        if self.auto_clear:
            print()
        exit_code = subprocess.call('py.test', cwd=self.directory, shell=True)
        passed = exit_code == 0

        # Beep if failed
        if not passed and self.beep_on_failure:
            print(BEEP_CHARACTER, end='')

        # Run custom commands
        if passed and self.onpass:
            os.system(self.onpass)
        elif not passed and self.onfail:
            os.system(self.onfail)


def watch(directory=None, auto_clear=False, beep_on_failure=True,
          onpass=None, onfail=None, extensions=[]):
    """
    Starts a server to render the specified file or directory
    containing a README.
    """
    if directory and not os.path.isdir(directory):
        raise ValueError('Directory not found: ' + directory)
    directory = os.path.abspath(directory or '')

    # Initial run
    event_handler = ChangeHandler(directory, auto_clear, beep_on_failure,
                                  onpass, onfail, extensions)
    event_handler.run()

    # Setup watchdog
    observer = Observer()
    observer.schedule(event_handler, path=directory, recursive=True)
    observer.start()

    # Watch and run tests until interrupted by user
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
