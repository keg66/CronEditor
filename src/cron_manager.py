import subprocess
import re
from typing import List, Dict, Any

class CronManager:
    def __init__(self):
        self.user = None

    def get_cron_jobs(self) -> List[Dict[str, Any]]:
        try:
            result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
            if result.returncode != 0:
                return []

            jobs = []
            lines = result.stdout.strip().split('\n')

            for i, line in enumerate(lines):
                if line.strip() and not line.startswith('#'):
                    job = self._parse_cron_line(line, i)
                    if job:
                        jobs.append(job)

            return jobs
        except Exception as e:
            print(f"Error reading crontab: {e}")
            return []

    def _parse_cron_line(self, line: str, index: int) -> Dict[str, Any]:
        parts = line.split()
        if len(parts) < 6:
            return None

        return {
            'id': index,
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
            jobs = self.get_cron_jobs()
            if job_id >= len(jobs):
                return False

            job = jobs[job_id]

            # Update the job
            job['minute'] = minute
            job['hour'] = hour
            job['day'] = day
            job['month'] = month
            job['weekday'] = weekday
            job['enabled'] = enabled

            # Rebuild crontab
            new_lines = []
            for j in jobs:
                if j['enabled']:
                    line = f"{j['minute']} {j['hour']} {j['day']} {j['month']} {j['weekday']} {j['command']}"
                else:
                    line = f"# {j['minute']} {j['hour']} {j['day']} {j['month']} {j['weekday']} {j['command']}"
                new_lines.append(line)

            # Write back to crontab
            new_crontab = '\n'.join(new_lines) + '\n'
            process = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE, text=True)
            process.communicate(input=new_crontab)

            return process.returncode == 0

        except Exception as e:
            print(f"Error updating crontab: {e}")
            return False