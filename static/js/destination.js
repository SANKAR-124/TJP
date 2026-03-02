const destDataEl = document.getElementById('destination-data');
const destId = destDataEl.getAttribute('data-did');

// --- Log Upload UI Update ---
document.getElementById('log_photo').addEventListener('change', function () {
    const fileLabel = document.getElementById('fileName');
    if (this.files.length > 1) {
        fileLabel.innerHTML = `<b>${this.files.length}</b> Photos Selected`;
        fileLabel.style.color = 'var(--accent)';
    } else if (this.files.length === 1) {
        // Show truncated filename if only one
        let name = this.files[0].name;
        if (name.length > 20) name = name.substring(0, 17) + '...';
        fileLabel.textContent = name;
        fileLabel.style.color = 'var(--accent)';
    } else {
        fileLabel.textContent = 'Attach Photo(s)';
        fileLabel.style.color = 'var(--text-muted)';
    }
});

// --- Handle Log Form Submission ---
document.getElementById('logForm').addEventListener('submit', function (e) {
    e.preventDefault();
    const formData = new FormData(this);

    // Matches your app.py route: @app.route('/travel_log/<int:Did>', methods=['POST'])
    fetch(`/travel_log/${destId}`, {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('Error: ' + data.message);
            }
        })
        .catch(error => console.error('Error:', error));
});

// --- Handle Reminder Form Submission ---
document.getElementById('reminderForm').addEventListener('submit', function (e) {
    e.preventDefault();
    const formData = new FormData(this);

    // Matches your app.py route: @app.route('/add_reminder/<int:Did>', methods=['POST'])
    fetch(`/add_reminder/${destId}`, {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('Error: ' + data.message);
            }
        })
        .catch(error => console.error('Error:', error));
});

// --- Toggle Reminder Status ---
function toggleReminder(reminderId, isChecked) {
    // Matches your app.py route: @app.route('/toggle_reminder/<int:Rid>', methods=['POST'])
    fetch(`/toggle_reminder/${reminderId}`, {
        method: 'POST'
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Find the specific text span next to the checkbox
                const reminderItem = document.getElementById(`reminder-${reminderId}`);
                const textSpan = reminderItem.querySelector('.rem-text');

                // App.py toggles between 0 and 1
                if (data.new_status === 1) {
                    textSpan.classList.add('completed');
                } else {
                    textSpan.classList.remove('completed');
                }
            } else {
                alert('Error toggling reminder.');
                location.reload(); // Revert visually if backend failed
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

// --- Delete Functions ---
function deleteLog(logId) {
    if (!confirm('Are you sure you want to delete this log entry?')) return;
    fetch(`/delete_log/${logId}`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById(`log-${logId}`).remove();
                if (document.querySelectorAll('.log-entry').length === 0) location.reload();
            } else {
                alert('Error deleting log.');
            }
        });
}

function deleteReminder(reminderId) {
    if (!confirm('Are you sure you want to delete this task?')) return;
    fetch(`/delete_reminder/${reminderId}`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById(`reminder-${reminderId}`).remove();
                if (document.querySelectorAll('.reminder-item').length === 0) location.reload();
            } else {
                alert('Error deleting reminder.');
            }
        });
}

// --- Fullscreen Photo Modal ---
let currentGallery = [];
let currentIndex = 0;

function openGalleryModal(photosArray, startIndex) {
    currentGallery = photosArray;
    currentIndex = startIndex;
    updateModalImage();
    document.getElementById('photoModal').classList.add('show');
}

function updateModalImage() {
    const expandedImg = document.getElementById('expandedPhoto');
    // Add an animation class to make it feel smooth
    expandedImg.style.opacity = 0; 
    setTimeout(() => {
        // Appends '/static/' so the URLs resolve correctly
        expandedImg.src = '/static/' + currentGallery[currentIndex];
        expandedImg.style.opacity = 1;
    }, 150); 

    // Toggle Arrows based on position
    document.getElementById('prevBtn').style.display = currentIndex > 0 ? 'flex' : 'none';
    document.getElementById('nextBtn').style.display = currentIndex < currentGallery.length - 1 ? 'flex' : 'none';
    
    // Update Counter
    document.getElementById('galleryCounter').textContent = `${currentIndex + 1} / ${currentGallery.length}`;
}

function nextImage(e) {
    e.stopPropagation(); // Prevent closing modal when clicking arrow
    if (currentIndex < currentGallery.length - 1) {
        currentIndex++;
        updateModalImage();
    }
}

function prevImage(e) {
    e.stopPropagation();
    if (currentIndex > 0) {
        currentIndex--;
        updateModalImage();
    }
}

function closePhotoModal() {
    document.getElementById('photoModal').classList.remove('show');
}

// Close when clicking outside the image
window.addEventListener('click', function (e) {
    if (e.target.id === 'photoModal' || e.target.classList.contains('gallery-container')) {
        closePhotoModal();
    }
});