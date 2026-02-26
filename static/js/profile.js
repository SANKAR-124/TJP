 // Trigger file input for photo upload
        function triggerPhotoUpload() {
            document.getElementById('photoInput').click();
        }
        
        // Handle photo upload
        function handlePhotoUpload(event) {
            const file = event.target.files[0];
            
            if (!file) {
                return;
            }
            
            // Check file type
            const validTypes = ['image/jpeg', 'image/png', 'image/gif'];
            if (!validTypes.includes(file.type)) {
                showError('Please upload a valid image file (JPG, PNG, GIF)');
                return;
            }
            
            // Check file size (max 5MB)
            if (file.size > 5 * 1024 * 1024) {
                showError('File size must be less than 5MB');
                return;
            }
            
            // Upload the photo
            uploadPhoto(file);
        }
        
        // Upload photo to server
        function uploadPhoto(file) {
            const formData = new FormData();
            formData.append('profile_photo', file);
            
            fetch('/upload_profile_photo', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update the profile photo display
                    const photoElement = document.getElementById('profilePhotoDisplay');
                    const placeholder = document.getElementById('profilePhotoPlaceholder');
                    
                    if (photoElement) {
                        photoElement.src = data.photo_path + '?' + new Date().getTime();
                    } else if (placeholder) {
                        placeholder.remove();
                        const img = document.createElement('img');
                        img.id = 'profilePhotoDisplay';
                        img.src = data.photo_path;
                        img.className = 'profile-photo-large';
                        document.querySelector('.profile-photo-section').insertBefore(img, document.querySelector('.upload-photo-btn'));
                    }
                    
                    showSuccess('Profile photo updated successfully!');
                } else {
                    showError(data.error || 'Failed to upload photo');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showError('Error uploading photo');
            });
        }
        
        // Enable edit mode
        function enableEdit() {
            const nameInput = document.getElementById('nameEdit');
            const ageInput = document.getElementById('ageEdit');
            const sexSelect = document.getElementById('sexEdit');
            
            // Set current values to edit inputs
            nameInput.value = document.getElementById('name').value;
            ageInput.value = document.getElementById('age').value;
            sexSelect.value = document.getElementById('sex').value;
            
            // Hide display inputs
            document.getElementById('name').style.display = 'none';
            document.getElementById('age').style.display = 'none';
            document.getElementById('sex').style.display = 'none';
            
            // Show edit inputs
            nameInput.style.display = 'block';
            ageInput.style.display = 'block';
            sexSelect.style.display = 'block';
            
            // Show/hide buttons
            document.getElementById('editBtn').style.display = 'none';
            document.getElementById('saveBtn').style.display = 'inline-block';
            document.getElementById('cancelBtn').style.display = 'inline-block';
            document.getElementById('uploadPhotoBtn').disabled = true;
        }
        
        // Cancel edit mode
        function cancelEdit() {
            // Hide edit inputs
            document.getElementById('nameEdit').style.display = 'none';
            document.getElementById('ageEdit').style.display = 'none';
            document.getElementById('sexEdit').style.display = 'none';
            
            // Show display inputs
            document.getElementById('name').style.display = 'block';
            document.getElementById('age').style.display = 'block';
            document.getElementById('sex').style.display = 'block';
            
            // Show/hide buttons
            document.getElementById('editBtn').style.display = 'inline-block';
            document.getElementById('saveBtn').style.display = 'none';
            document.getElementById('cancelBtn').style.display = 'none';
            document.getElementById('uploadPhotoBtn').disabled = false;
        }
        
        // Save profile changes
        function saveProfile() {
            const name = document.getElementById('nameEdit').value.trim();
            const age = document.getElementById('ageEdit').value;
            const sex = document.getElementById('sexEdit').value;
            
            // Validate inputs
            if (!name) {
                showError('Please enter your name');
                return;
            }
            
            if (age && (age < 1 || age > 120)) {
                showError('Please enter a valid age between 1 and 120');
                return;
            }
            
            // Send data to server
            fetch('/update_profile', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    name: name,
                    age: age ? parseInt(age) : null,
                    sex: sex
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update display values
                    document.getElementById('name').value = name;
                    document.getElementById('age').value = age;
                    document.getElementById('sex').value = sex;
                    
                    // Exit edit mode
                    cancelEdit();
                    showSuccess('Profile updated successfully!');
                } else {
                    showError(data.error || 'Failed to update profile');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showError('Error updating profile');
            });
        }
        
        // Show success message
        function showSuccess(message) {
            const successMsg = document.getElementById('successMessage');
            successMsg.textContent = message;
            successMsg.style.display = 'block';
            setTimeout(() => {
                successMsg.style.display = 'none';
            }, 3000);
        }
        
        // Show error message
        function showError(message) {
            const errorMsg = document.getElementById('errorMessage');
            errorMsg.textContent = message;
            errorMsg.style.display = 'block';
            setTimeout(() => {
                errorMsg.style.display = 'none';
            }, 3000);
        }