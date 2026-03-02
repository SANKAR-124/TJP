// --- Photo Upload Logic ---
function triggerPhotoUpload() {
    document.getElementById('photoInput').click();
}

function handlePhotoUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    const validTypes = ['image/jpeg', 'image/png', 'image/gif'];
    if (!validTypes.includes(file.type)) {
        showToast('Please upload a valid image file (JPG, PNG, GIF)', 'error');
        return;
    }

    if (file.size > 5 * 1024 * 1024) {
        showToast('File size must be less than 5MB', 'error');
        return;
    }

    const formData = new FormData();
    formData.append('profile_photo', file);

    fetch('/upload_profile_photo', {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update the image source dynamically to bypass cache
                const photoElement = document.getElementById('profilePhotoDisplay');
                const placeholder = document.getElementById('profilePhotoPlaceholder');
                const cleanPath = data.photo_path.replace('static/', '');

                if (photoElement) {
                    photoElement.src = `/static/${cleanPath}?t=${new Date().getTime()}`;
                } else if (placeholder) {
                    // If replacing a placeholder, create an img element
                    placeholder.outerHTML = `<img id="profilePhotoDisplay" src="/static/${cleanPath}" class="profile-photo">`;
                }
                showToast('Profile photo updated successfully!', 'success');
            } else {
                showToast(data.error || 'Failed to upload photo', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('Error uploading photo', 'error');
        });
}

// --- Edit & Save Logic ---
function enableEdit() {
    // Enable inputs
    document.querySelectorAll('.input-editable').forEach(input => {
        input.disabled = false;
    });

    // Focus first input naturally
    document.getElementById('nameEdit').focus();

    // Swap buttons
    document.getElementById('editBtn').style.display = 'none';
    document.getElementById('saveCancelGroup').classList.add('show');

    // Disable photo change while editing info
    document.querySelector('.btn-change-photo').style.pointerEvents = 'none';
    document.querySelector('.btn-change-photo').style.opacity = '0.5';
}

function cancelEdit() {
    // Disable inputs
    document.querySelectorAll('.input-editable').forEach(input => {
        input.disabled = true;
    });

    // Swap buttons back
    document.getElementById('saveCancelGroup').classList.remove('show');
    document.getElementById('editBtn').style.display = 'block';

    // Re-enable photo button
    document.querySelector('.btn-change-photo').style.pointerEvents = 'auto';
    document.querySelector('.btn-change-photo').style.opacity = '1';
}

function saveProfile() {
    const name = document.getElementById('nameEdit').value.trim();
    const age = document.getElementById('ageEdit').value;
    const sex = document.getElementById('sexEdit').value;

    if (!name) {
        showToast('Please enter your full name', 'error');
        return;
    }

    if (age && (age < 1 || age > 120)) {
        showToast('Please enter a valid age (1-120)', 'error');
        return;
    }

    fetch('/update_profile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            name: name,
            age: age ? parseInt(age) : null,
            sex: sex
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update the display name at the top
                document.getElementById('displayName').textContent = name;
                cancelEdit();
                showToast('Profile updated successfully!', 'success');
            } else {
                showToast(data.error || 'Failed to update profile', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('Error updating profile', 'error');
        });
}

// --- Fullscreen Photo Modal ---
function openPhotoModal() {
    const displayImg = document.getElementById('profilePhotoDisplay');
    if (displayImg) {
        const modal = document.getElementById('photoModal');
        document.getElementById('expandedPhoto').src = displayImg.src;
        modal.classList.add('show');
    }
}

function closePhotoModal() {
    document.getElementById('photoModal').classList.remove('show');
}

window.addEventListener('click', function (e) {
    if (e.target.id === 'photoModal') closePhotoModal();
});

// --- Toast Notification System ---
let toastTimeout;
function showToast(message, type) {
    const toast = document.getElementById('toastNotification');
    toast.textContent = message;

    // Reset classes
    toast.className = 'toast show';
    toast.classList.add(type); // 'success' or 'error'

    clearTimeout(toastTimeout);
    toastTimeout = setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}