# src/my_package_name/controllers/file_watcher.py
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from typing import Callable

class FileWatcher:
    """Watches a directory and fires a callback on changes."""
    def __init__(self, directory: str, callback: Callable[[], None]) -> None:
        self.directory = directory
        self.callback = callback
        self._observer = Observer()

    def start(self) -> None:
        handler = _WatchHandler(self.callback)
        self._observer.schedule(handler, self.directory, recursive=True)
        self._observer.start()

    def stop(self) -> None:
        self._observer.stop()
        self._observer.join()

class _WatchHandler(FileSystemEventHandler):
    def __init__(self, callback: Callable[[], None]) -> None:
        super().__init__()
        self.callback = callback
    def on_any_event(self, event) -> None:
        self.callback()
