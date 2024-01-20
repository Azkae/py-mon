import os
import subprocess
from sys import executable
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

from .logger import *


class Monitor:
    def _handle_event(self, event):
        log(Color.YELLOW, "restarting due to changes detected...")

        if self.debug:
            log(Color.CYAN, f"{event.event_type} {event.src_path}")

        self.restart_process()

    def __init__(self, arguments):
        self.filename = arguments.filename + (
            ".py" if not arguments.filename.endswith(".py") else ""
        )
        self.patterns = arguments.patterns
        self.ignore_patterns = arguments.ignore_patterns
        self.args = arguments.args
        self.watch = arguments.watch
        self.debug = arguments.debug

        self.process = None

        self.event_handler = PatternMatchingEventHandler(
            patterns=self.patterns, ignore_patterns=self.ignore_patterns
        )
        self.event_handler.on_modified = self._handle_event
        self.event_handler.on_created = self._handle_event
        self.event_handler.on_deleted = self._handle_event
        self.event_handler.on_moved = self._handle_event

        self.observer = Observer()
        self.observer.schedule(self.event_handler, self.watch, recursive=True)

    def start(self):
        log(Color.YELLOW, f"watching path: {self.watch}")
        log(Color.YELLOW, f"watching patterns: {', '.join(self.patterns)}")
        log(
            Color.YELLOW, f"watching ignore-patterns: {', '.join(self.ignore_patterns)}"
        )
        log(Color.YELLOW, "enter 'rs' to restart or 'stop' to terminate")

        self.observer.start()
        self.start_process()

    def stop(self):
        self.stop_process()
        self.observer.stop()
        self.observer.join()

        log(Color.RED, "terminated process")

    def restart_process(self):
        self.stop_process()
        self.start_process()

    def start_process(self):
        log(Color.GREEN, f"starting {self.filename}")
        self.process = subprocess.Popen([executable, self.filename, *self.args])

    def stop_process(self):
        self.process.terminate()
        self.process = None
