# logger.py
# BOF Core – Data Logging Utility

import datetime
import os

class BOFLogger:
    """
    Simple logging utility for the BOF Core system.
    Stores runtime events in timestamped log files.
    """

    def __init__(self, log_dir="data/log/records"):
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        self.log_file = os.path.join(self.log_dir, "bof_log.txt")

    def write(self, message):
        """Append a timestamped message to the log file."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")

    def section(self, title):
        """Write a visual section divider to the log."""
        divider = "=" * 40
        self.write(f"\n{divider}\n{title}\n{divider}\n")

    def clear(self):
        """Clear current log file."""
        open(self.log_file, "w").close()
