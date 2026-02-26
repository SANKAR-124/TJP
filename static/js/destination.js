// Pull the Destination ID safely from the hidden HTML bridge
const destDataEl = document.getElementById('destination-data');
const destId = destDataEl.getAttribute('data-did');

document.getElementById('logForm').addEventListener('submit', function (e) {
    e.preventDefault();

    const formData = new FormData(this);

    fetch(`/travel_log/${destId}`, {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload(); // Reload to show the new log!
            } else {
                alert('Error: ' + data.message);
            }
        })
        .catch(error => console.error('Error:', error));
});

// Handle reminder form submission
document.getElementById('reminderForm').addEventListener('submit', function (e) {
    e.preventDefault();

    const formData = new FormData(this);
// fetch(`/add_reminder/{{ destination.Did }}`, {
    fetch(`/add_reminder/${destId}`, {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload(); // Reload to show the new reminder!
            } else {
                alert('Error: ' + data.message);
            }
        })
        .catch(error => console.error('Error:', error));
});

// Toggle reminder status
function toggleReminder(reminderId) {
    fetch(`/toggle_reminder/${reminderId}`, {
        method: 'POST'
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const reminderEl = document.getElementById(`reminder-${reminderId}`);
                const statusSpan = document.querySelector(`.reminder-status-${reminderId}`);
                const toggleBtn = reminderEl.querySelector('button');

                // Convert 0/1 back to words for the user to see
                statusSpan.textContent = data.new_status === 0 ? "pending" : "completed";

                // If the new status is 1 (completed)
                if (data.new_status === 1) {
                    reminderEl.classList.add('alert-success');
                    toggleBtn.classList.remove('btn-success');
                    toggleBtn.classList.add('btn-warning');
                    toggleBtn.textContent = '↻ Reopen';
                } else {
                    reminderEl.classList.remove('alert-success');
                    toggleBtn.classList.remove('btn-warning');
                    toggleBtn.classList.add('btn-success');
                    toggleBtn.textContent = '✓ Done';
                }
            } else {
                alert('Error toggling reminder. Please try again.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error toggling reminder. Please try again.');
        });
}

// Delete log
function deleteLog(logId) {
    if (!confirm('Are you sure you want to delete this log entry? This cannot be undone.')) return;

    fetch(`/delete_log/${logId}`, {
        method: 'POST'
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const logEl = document.getElementById(`log-${logId}`);
                logEl.style.animation = 'fadeOut 0.3s ease-out forwards';
                setTimeout(() => {
                    logEl.remove();
                }, 300);
            } else {
                alert('Error deleting log. Please try again.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error deleting log. Please try again.');
        });
}

// Delete reminder
function deleteReminder(reminderId) {
    if (!confirm('Are you sure you want to delete this reminder? This cannot be undone.')) return;

    fetch(`/delete_reminder/${reminderId}`, {
        method: 'POST'
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const reminderEl = document.getElementById(`reminder-${reminderId}`);
                reminderEl.style.animation = 'fadeOut 0.3s ease-out forwards';
                setTimeout(() => {
                    reminderEl.remove();
                }, 300);
            } else {
                alert('Error deleting reminder. Please try again.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error deleting reminder. Please try again.');
        });
}