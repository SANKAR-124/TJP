// Toggle Profile Dropdown
function toggleDropdown() {
    document.getElementById("profileDropdown").classList.toggle("show");
}

window.onclick = function(event) {
    if (!event.target.matches('.profile-pic') && !event.target.closest('.profile-pic')) {
        const dropdowns = document.getElementsByClassName("dropdown-content");
        for (let i = 0; i < dropdowns.length; i++) {
            if (dropdowns[i].classList.contains('show')) {
                dropdowns[i].classList.remove('show');
            }
        }
    }
}

// Modal management
function openModal() {
    document.getElementById('addJourneyModal').style.display = 'flex';
}

function closeModal() {
    document.getElementById('addJourneyModal').style.display = 'none';
}

// Render Journeys
function loadJourneys() {
    const gridEl = document.getElementById('journeyGrid');
    const dataEl = document.getElementById('journey-data');
    
    if (!gridEl || !dataEl) return; 

    const allJourneys = JSON.parse(dataEl.getAttribute('data-json'));

    allJourneys.forEach(journey => {
        const card = document.createElement('div');
        card.className = 'journey-card fade-in';
        card.onclick = () => window.location.href = `/journey/${journey.Jid}`;

        const statusClass = journey.status.toLowerCase().replace(" ", "");

        card.innerHTML = `
            <div class="card-content">
                <div class="card-header-row">
                    <h3 class="card-title">${journey.J_name}</h3>
                    <span class="status-tag status-${statusClass}">${journey.status}</span>
                </div>
                
                <p class="card-date">
                    <i class="fa-solid fa-calendar-alt"></i> ${journey.Start_date} to ${journey.end_date}
                </p>
                
                <p class="card-description">
                    ${journey.description ? journey.description : '<span class="text-muted" style="font-style: italic;">No description provided.</span>'}
                </p>
            </div>
            
            <div class="card-actions">
                <button class="btn btn-gradient btn-full">
                    Open Workspace <i class="fa-solid fa-arrow-right"></i>
                </button>
            </div>
        `;
        
        gridEl.appendChild(card);
    });
}

// Handle Form Submission
document.addEventListener('DOMContentLoaded', function () {
    loadJourneys();
    
    const formEl = document.getElementById('addJourneyForm');
    if (formEl) {
        formEl.addEventListener('submit', function (e) {
            e.preventDefault();
            const formData = new FormData(this);

            // Matches your @app.route('/create_journey')
            fetch('/create_journey', {
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
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred. Please try again.');
            });
        });
    }
});