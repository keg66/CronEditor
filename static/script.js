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
    currentEditingJob = jobId;
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

    const minute = editDiv.querySelector('[data-field="minute"]').value;
    const hour = editDiv.querySelector('[data-field="hour"]').value;
    const day = editDiv.querySelector('[data-field="day"]').value;
    const month = editDiv.querySelector('[data-field="month"]').value;
    const weekday = editDiv.querySelector('[data-field="weekday"]').value;
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
            }, 1000);
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