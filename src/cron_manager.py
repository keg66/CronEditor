import subprocess
import re
import os
import getpass
from typing import List, Dict, Any

class CronManager:
    def __init__(self):
        self.all_lines = []
        self.cron_jobs = []

    def get_cron_jobs(self) -> List[Dict[str, Any]]:
        try:
            result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
            if result.returncode != 0:
                print(f"crontab -l failed with return code {result.returncode}")
                print(f"stderr: {result.stderr}")
                return []

            self.all_lines = result.stdout.strip().split('\n')
            jobs = []
            job_index = 0

            for line_index, line in enumerate(self.all_lines):
                if line.strip():
                    # Check if it's a cron job (active or disabled)
                    if self._is_cron_job_line(line):
                        job = self._parse_cron_line(line, job_index, line_index)
                        if job:
                            jobs.append(job)
                            job_index += 1

            self.cron_jobs = jobs
            print(f"Found {len(jobs)} cron jobs (including disabled ones)")
            return jobs
        except Exception as e:
            print(f"Error reading crontab: {e}")
            return []

    def _is_cron_job_line(self, line: str) -> bool:
        """Check if a line is a cron job (active or disabled)"""
        line = line.strip()

        # Skip empty lines
        if not line:
            return False

        # Check for disabled cron job pattern: # minute hour day month weekday command
        if line.startswith('#'):
            return self._looks_like_disabled_cron(line)

        # Check for active cron job pattern: minute hour day month weekday command
        parts = line.split()
        return len(parts) >= 6 and self._is_valid_cron_time_fields(parts[:5])

    def _looks_like_disabled_cron(self, line: str) -> bool:
        """Check if a commented line looks like a disabled cron job"""
        # Remove the # and check if it looks like a cron job
        uncommented = line[1:].strip()
        if not uncommented:
            return False

        parts = uncommented.split()
        return len(parts) >= 6 and self._is_valid_cron_time_fields(parts[:5])

    def _is_valid_cron_time_fields(self, fields: List[str]) -> bool:
        """Check if the first 5 fields look like valid cron time fields"""
        if len(fields) != 5:
            return False

        # Define patterns for each field type
        cron_patterns = [
            r'^(\*|[0-5]?[0-9](-[0-5]?[0-9])?(\,[0-5]?[0-9](-[0-5]?[0-9])?)*|\*/[0-9]+|[0-5]?[0-9](-[0-5]?[0-9])?/[0-9]+)$',  # minute (0-59)
            r'^(\*|[01]?[0-9]|2[0-3]|[01]?[0-9]-[01]?[0-9]|2[0-3]-2[0-3]|\*|\*/[0-9]+|[0-2]?[0-9]/[0-9]+|\d+(,\d+)*)$',  # hour (0-23)
            r'^(\*|[1-9]|[12][0-9]|3[01]|\*/[0-9]+|[1-9]-[1-3]?[0-9]|[1-9]/[0-9]+|\d+(,\d+)*)$',  # day (1-31)
            r'^(\*|[1-9]|1[0-2]|\*/[0-9]+|[1-9]-1?[0-2]|[1-9]/[0-9]+|\d+(,\d+)*)$',  # month (1-12)
            r'^(\*|[0-7]|(sun|mon|tue|wed|thu|fri|sat)(-(sun|mon|tue|wed|thu|fri|sat))?(,(sun|mon|tue|wed|thu|fri|sat)(-(sun|mon|tue|wed|thu|fri|sat))?)*|\*/[0-9]+|[0-7]/[0-9]+|\d+(,\d+)*)$'  # weekday (0-7 or names)
        ]

        for i, field in enumerate(fields):
            # For simplicity, use a more relaxed but still restrictive pattern
            if not re.match(r'^[0-9*,/-]+$|^[a-zA-Z,-]+$', field):
                return False

            # Additional check: field shouldn't be just letters without being weekday-like
            if re.match(r'^[a-zA-Z]+$', field) and i != 4:  # Only weekday field (index 4) can be pure letters
                if not re.match(r'^(sun|mon|tue|wed|thu|fri|sat)$', field.lower()):
                    return False

        return True

    def _parse_cron_line(self, line: str, job_id: int, line_index: int) -> Dict[str, Any]:
        original_line = line
        enabled = not line.strip().startswith('#')

        # If it's a commented line, remove the comment to parse
        if line.strip().startswith('#'):
            line = line.strip()[1:].strip()

        parts = line.split()
        if len(parts) < 6:
            return None

        return {
            'id': job_id,
            'line_index': line_index,
            'minute': parts[0],
            'hour': parts[1],
            'day': parts[2],
            'month': parts[3],
            'weekday': parts[4],
            'command': ' '.join(parts[5:]),
            'enabled': enabled,
            'original_line': original_line
        }

    def update_cron_job(self, job_id: int, minute: str, hour: str, day: str, month: str, weekday: str, enabled: bool) -> bool:
        try:
            print(f"Updating job {job_id} with minute={minute}, hour={hour}, day={day}, month={month}, weekday={weekday}, enabled={enabled}")

            # Get fresh cron jobs
            jobs = self.get_cron_jobs()

            if job_id >= len(jobs):
                print(f"Job ID {job_id} out of range. Available jobs: {len(jobs)}")
                return False

            job = jobs[job_id]
            line_index = job['line_index']

            # Create new cron line
            if enabled:
                new_line = f"{minute} {hour} {day} {month} {weekday} {job['command']}"
            else:
                new_line = f"# {minute} {hour} {day} {month} {weekday} {job['command']}"

            # Update the line in all_lines
            self.all_lines[line_index] = new_line

            # Write back to crontab
            new_crontab = '\n'.join(self.all_lines) + '\n'
            print(f"Writing new crontab:\n{new_crontab}")

            process = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate(input=new_crontab)

            if process.returncode != 0:
                print(f"crontab update failed with return code {process.returncode}")
                print(f"stderr: {stderr}")
                return False

            print("Crontab updated successfully")
            return True

        except Exception as e:
            print(f"Error updating crontab: {e}")
            import traceback
            traceback.print_exc()
            return False