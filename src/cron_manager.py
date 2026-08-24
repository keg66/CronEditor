import subprocess
import re
from typing import List, Dict, Any, Optional

class CronManager:
    FIELD_SPECS = (
        ('minute', 0, 59, False),
        ('hour', 0, 23, False),
        ('day', 1, 31, False),
        ('month', 1, 12, False),
        ('weekday', 0, 7, True),
    )
    WEEKDAYS = {'sun': 0, 'mon': 1, 'tue': 2, 'wed': 3, 'thu': 4, 'fri': 5, 'sat': 6}
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
        return len(parts) >= 6 and self._looks_like_cron_fields(parts[:5])

    def _looks_like_disabled_cron(self, line: str) -> bool:
        """Check if a commented line looks like a disabled cron job"""
        # Remove the # and check if it looks like a cron job
        uncommented = line[1:].strip()
        if not uncommented:
            return False

        parts = uncommented.split()
        return len(parts) >= 6 and self._looks_like_cron_fields(parts[:5])

    def _looks_like_cron_fields(self, fields: List[str]) -> bool:
        """Recognise both supported expressions and cron-like unsupported ones."""
        if self._is_valid_cron_time_fields(fields):
            return True
        # Preserve rows with special day-of-month syntax (for example ``L``),
        # but do not mistake prose comments for disabled cron jobs.  The minute,
        # hour, month and weekday columns must still be valid cron fields.
        return len(fields) == 5 and all((
            self._validate_field(fields[0], 0, 59, False) is None,
            self._validate_field(fields[1], 0, 23, False) is None,
            self._validate_field(fields[3], 1, 12, False) is None,
            self._validate_field(fields[4], 0, 7, True) is None,
        ))

    def _is_valid_cron_time_fields(self, fields: List[str]) -> bool:
        """Check if the first 5 fields look like valid cron time fields"""
        if len(fields) != 5:
            return False

        return not self.validate_time_fields(*fields)

    def validate_time_fields(self, minute: str, hour: str, day: str,
                             month: str, weekday: str) -> Dict[str, str]:
        """Return field-specific validation errors for standard five-field cron."""
        values = (minute, hour, day, month, weekday)
        errors = {}
        for (name, minimum, maximum, allows_names), value in zip(self.FIELD_SPECS, values):
            error = self._validate_field(value, minimum, maximum, allows_names)
            if error:
                errors[name] = error
        return errors

    def _validate_field(self, value: Any, minimum: int, maximum: int,
                        allows_names: bool) -> Optional[str]:
        if not isinstance(value, str) or not value:
            return '値を指定してください。'
        if ',' in value and '/' in value:
            return '間隔と複数指定の組み合わせには対応していません。'
        for part in value.lower().split(','):
            if not part:
                return '空の項目は指定できません。'
            base, *steps = part.split('/')
            if len(steps) > 1 or (steps and (not steps[0].isdigit() or int(steps[0]) < 1)):
                return '間隔は1以上の整数で指定してください。'
            if steps and base != '*' and '-' not in base:
                return '間隔は任意または範囲に指定してください。'
            if base == '*':
                continue
            bounds = base.split('-')
            if len(bounds) > 2 or not all(bounds):
                return '範囲の形式が正しくありません。'
            parsed = [self._parse_value(item, minimum, maximum, allows_names) for item in bounds]
            if any(item is None for item in parsed):
                return '指定可能な値または範囲を入力してください。'
            if len(parsed) == 2 and parsed[0] > parsed[1]:
                return '範囲の開始値は終了値以下にしてください。'
        return None

    def _parse_value(self, value: str, minimum: int, maximum: int,
                     allows_names: bool) -> Optional[int]:
        if allows_names and value in self.WEEKDAYS:
            return self.WEEKDAYS[value]
        if not value.isdigit():
            return None
        parsed = int(value)
        return parsed if minimum <= parsed <= maximum else None

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
            , 'supported': self._is_valid_cron_time_fields(parts[:5])
        }

    def update_cron_job(self, job_id: int, minute: str, hour: str, day: str, month: str, weekday: str, enabled: bool) -> bool:
        try:
            print(f"Updating job {job_id} with minute={minute}, hour={hour}, day={day}, month={month}, weekday={weekday}, enabled={enabled}")

            errors = self.validate_time_fields(minute, hour, day, month, weekday)
            if errors:
                raise ValueError('; '.join(f'{field}: {message}' for field, message in errors.items()))

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
