// Open modal function
        function openModal() {
            const modal = document.getElementById('journeyModal');
            modal.classList.add('show');
        }
        
        // Close modal function
        function closeModal() {
            const modal = document.getElementById('journeyModal');
            modal.classList.remove('show');
            // Reload the page to see new journey
            location.reload();
        }
        
        // Close modal when clicking outside of it
        window.addEventListener('click', function(event) {
            const modal = document.getElementById('journeyModal');
            if (event.target === modal) {
                modal.classList.remove('show');
            }
        });
        
        // Listen for close message from iframe
        window.addEventListener('message', function(event) {
            if (event.data === 'closeModal') {
                closeModal();
            }
        });