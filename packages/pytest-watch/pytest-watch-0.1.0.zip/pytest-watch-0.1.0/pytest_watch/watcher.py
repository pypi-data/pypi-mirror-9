import os
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


default_extensions = ['.py']


class ChangeHandler(FileSystemEventHandler):
    """Listens for changes to files and re-runs tests after each change."""
    def __init__(self, directory=None, auto_clear=False, extensions=[]):
        super(ChangeHandler, self).__init__()
        self.directory = os.path.abspath(directory or '.')
        self.auto_clear = auto_clear
        self.extensions = extensions or default_extensions

    def on_any_event(self, event):
        if event.is_directory:
            return
        ext = os.path.splitext(event.src_path)[1].lower()
        if ext in self.extensions:
            self.run()

    def run(self):
        """Called when a file is changed to re-run the tests with nose."""
        if self.auto_clear:
            os.system('cls' if os.name == 'nt' else 'auto_clear')
        else:
            print
        print 'Running unit tests...'
        if self.auto_clear:
            print
        subprocess.call('py.test', cwd=self.directory, shell=True)


def watch(directory=None, auto_clear=False, extensions=[]):
    """Starts a server to render the specified file or directory containing a README."""
    if directory and not os.path.isdir(directory):
        raise ValueError('Directory not found: ' + directory)
    directory = os.path.abspath(directory)

    # Initial run
    event_handler = ChangeHandler(directory, auto_clear, extensions)
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
