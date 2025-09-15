import subprocess
import re
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
                if line.strip() and not line.startswith('#'):
                    job = self._parse_cron_line(line, job_index, line_index)
                    if job:
                        jobs.append(job)
                        job_index += 1

            self.cron_jobs = jobs
            print(f"Found {len(jobs)} cron jobs")
            return jobs
        except Exception as e:
            print(f"Error reading crontab: {e}")
            return []

    def _parse_cron_line(self, line: str, job_id: int, line_index: int) -> Dict[str, Any]:
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
            'enabled': True,
            'original_line': line
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