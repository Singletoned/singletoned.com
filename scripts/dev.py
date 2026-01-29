#!/usr/bin/env python3
"""Development server with auto-rebuild on file changes."""

import http.server
import socketserver
import sys
import threading
import time
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

# Add parent directory to path to import build module
sys.path.insert(0, str(Path(__file__).parent.parent))
from build import BlogBuilder

PORT = 3000
is_building = False
build_lock = threading.Lock()


def rebuild():
    global is_building
    with build_lock:
        if is_building:
            return
        is_building = True

    print("Changes detected, rebuilding...")
    try:
        builder = BlogBuilder()
        builder.build()
        print("Rebuild complete!")
    except Exception as e:
        print(f"Build error: {e}")
        raise
    finally:
        with build_lock:
            is_building = False


class RebuildHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_rebuild = 0
        self.debounce_seconds = 0.5

    def on_any_event(self, event):
        if event.is_directory:
            return
        # Debounce rapid changes
        now = time.time()
        if now - self.last_rebuild < self.debounce_seconds:
            return
        self.last_rebuild = now
        threading.Thread(target=rebuild).start()


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="public", **kwargs)

    def log_message(self, format, *args):
        # Only log errors, not every request
        pass


def main():
    print("Starting development server...")

    # Initial build
    rebuild()

    # Start file watcher
    event_handler = RebuildHandler()
    observer = Observer()
    for watch_path in ["drafts", "posts", "pages", "templates", "static"]:
        if Path(watch_path).exists():
            observer.schedule(event_handler, watch_path, recursive=True)
    observer.start()

    # Start HTTP server
    with socketserver.TCPServer(("", PORT), QuietHandler) as httpd:
        print(f"Development server running at http://localhost:{PORT}")
        print("Watching for changes...")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down...")
            observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
