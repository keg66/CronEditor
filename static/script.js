let currentEditingJob = null;

function editJob(jobId) {
    if (currentEditingJob !== null && currentEditingJob !== jobId) {
        cancelEdit(currentEditingJob);
    }

    const jobRow = document.querySelector(`[data-job-id="${jobId}"]`);
    const displayDiv = jobRow.querySelector('.job-display');
    const editDiv = jobRow.querySelector('.job-edit');

    displayDiv.style.display = 'none';
    editDiv.style.display = 'grid';

    // Auto-detect if advanced mode is needed
    autoDetectEditMode(jobId);

    currentEditingJob = jobId;
}

function autoDetectEditMode(jobId) {
    const jobRow = document.querySelector(`[data-job-id="${jobId}"]`);
    const timeValues = [
        jobRow.querySelector('.job-display .time-part:nth-child(1)').textContent, // minute
        jobRow.querySelector('.job-display .time-part:nth-child(2)').textContent, // hour
        jobRow.querySelector('.job-display .time-part:nth-child(3)').textContent, // day
        jobRow.querySelector('.job-display .time-part:nth-child(4)').textContent, // month
        jobRow.querySelector('.job-display .time-part:nth-child(5)').textContent  // weekday
    ];

    // Check if any value requires advanced mode
    const needsAdvancedMode = timeValues.some(value => {
        return value.includes('/') || value.includes('-') || value.includes(',') ||
               value.includes('mon') || value.includes('tue') || value.includes('wed') ||
               value.includes('thu') || value.includes('fri') || value.includes('sat') || value.includes('sun');
    });

    if (needsAdvancedMode) {
        showAdvancedMode(jobId);
    } else {
        showSimpleMode(jobId);
    }
}

function toggleEditMode(jobId) {
    const jobRow = document.querySelector(`[data-job-id="${jobId}"]`);
    const simpleMode = jobRow.querySelector('.simple-mode');
    const advancedMode = jobRow.querySelector('.advanced-mode');
    const toggleBtn = jobRow.querySelector('.toggle-btn');
    const toggleText = toggleBtn.querySelector('.toggle-text');

    if (simpleMode.style.display !== 'none') {
        showAdvancedMode(jobId);
    } else {
        showSimpleMode(jobId);
    }
}

function showSimpleMode(jobId) {
    const jobRow = document.querySelector(`[data-job-id="${jobId}"]`);
    const simpleMode = jobRow.querySelector('.simple-mode');
    const advancedMode = jobRow.querySelector('.advanced-mode');
    const toggleBtn = jobRow.querySelector('.toggle-btn');
    const toggleText = toggleBtn.querySelector('.toggle-text');

    simpleMode.style.display = 'grid';
    advancedMode.style.display = 'none';
    toggleBtn.classList.remove('active');
    toggleText.textContent = '高度な設定';
}

function showAdvancedMode(jobId) {
    const jobRow = document.querySelector(`[data-job-id="${jobId}"]`);
    const simpleMode = jobRow.querySelector('.simple-mode');
    const advancedMode = jobRow.querySelector('.advanced-mode');
    const toggleBtn = jobRow.querySelector('.toggle-btn');
    const toggleText = toggleBtn.querySelector('.toggle-text');

    simpleMode.style.display = 'none';
    advancedMode.style.display = 'grid';
    toggleBtn.classList.add('active');
    toggleText.textContent = '基本設定';
}

function cancelEdit(jobId) {
    const jobRow = document.querySelector(`[data-job-id="${jobId}"]`);
    const displayDiv = jobRow.querySelector('.job-display');
    const editDiv = jobRow.querySelector('.job-edit');

    displayDiv.style.display = 'grid';
    editDiv.style.display = 'none';
    currentEditingJob = null;
}

function saveJob(jobId) {
    const jobRow = document.querySelector(`[data-job-id="${jobId}"]`);
    const editDiv = jobRow.querySelector('.job-edit');
    const simpleMode = jobRow.querySelector('.simple-mode');
    const advancedMode = jobRow.querySelector('.advanced-mode');

    let minute, hour, day, month, weekday;

    // Get values from the currently active mode
    if (simpleMode.style.display !== 'none') {
        // Simple mode - get from dropdowns
        minute = simpleMode.querySelector('[data-field="minute"]').value;
        hour = simpleMode.querySelector('[data-field="hour"]').value;
        day = simpleMode.querySelector('[data-field="day"]').value;
        month = simpleMode.querySelector('[data-field="month"]').value;
        weekday = simpleMode.querySelector('[data-field="weekday"]').value;
    } else {
        // Advanced mode - get from text inputs
        minute = advancedMode.querySelector('[data-field="minute"]').value.trim();
        hour = advancedMode.querySelector('[data-field="hour"]').value.trim();
        day = advancedMode.querySelector('[data-field="day"]').value.trim();
        month = advancedMode.querySelector('[data-field="month"]').value.trim();
        weekday = advancedMode.querySelector('[data-field="weekday"]').value.trim();

        // Basic validation for advanced mode
        if (!minute || !hour || !day || !month || !weekday) {
            showMessage('全ての時間フィールドを入力してください。', 'error');
            return;
        }
    }

    const enabled = editDiv.querySelector('.enabled-checkbox').checked;

    const data = {
        job_id: jobId,
        minute: minute,
        hour: hour,
        day: day,
        month: month,
        weekday: weekday,
        enabled: enabled
    };

    fetch('/update_job', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            showMessage('Cronジョブが正常に更新されました。', 'success');
            setTimeout(() => {
                window.location.reload();
            }, 1500);
        } else {
            showMessage('エラー: ' + result.error, 'error');
        }
    })
    .catch(error => {
        showMessage('通信エラーが発生しました。', 'error');
        console.error('Error:', error);
    });
}

function showMessage(text, type) {
    const messageDiv = document.getElementById('message');
    messageDiv.textContent = text;
    messageDiv.className = `message ${type}`;
    messageDiv.style.display = 'block';

    setTimeout(() => {
        messageDiv.style.display = 'none';
    }, 5000);
}