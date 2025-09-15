from flask import Flask, render_template, request, jsonify
import configparser
import os
from src.cron_manager import CronManager

app = Flask(__name__)
cron_manager = CronManager()

def load_config():
    config = configparser.ConfigParser()
    config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
    config.read(config_path)
    return config

@app.route('/')
def index():
    jobs = cron_manager.get_cron_jobs()
    return render_template('index.html', jobs=jobs)

@app.route('/update_job', methods=['POST'])
def update_job():
    try:
        data = request.get_json()
        job_id = data.get('job_id')
        minute = data.get('minute')
        hour = data.get('hour')
        day = data.get('day')
        month = data.get('month')
        weekday = data.get('weekday')
        enabled = data.get('enabled', True)

        success = cron_manager.update_cron_job(
            job_id, minute, hour, day, month, weekday, enabled
        )

        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Cronジョブの更新に失敗しました'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    config = load_config()
    host = config.get('server', 'host', fallback='0.0.0.0')
    port = config.getint('server', 'port', fallback=5000)
    debug = config.getboolean('server', 'debug', fallback=False)

    app.run(host=host, port=port, debug=debug)