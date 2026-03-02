const journeyDataEl = document.getElementById('journey-data');
const journeyId = journeyDataEl.getAttribute('data-jid');
const journeyData = {
    name: journeyDataEl.getAttribute('data-name'),
    startDate: journeyDataEl.getAttribute('data-start'),
    endDate: journeyDataEl.getAttribute('data-end'),
    description: journeyDataEl.getAttribute('data-desc')
};

document.addEventListener('DOMContentLoaded', function () {
    const expenseDateInput = document.getElementById('expense_date');
    if (expenseDateInput) {
        expenseDateInput.value = new Date().toISOString().split('T')[0];
    }
    document.getElementById('destinationForm').action = `/add_destination/${journeyId}`;
});

function viewDestination(destId) { window.location.href = `/destination/${destId}`; }

// Modal Logic
function openDestinationModal() {
    const modal = document.getElementById('destinationModal');
    document.getElementById('destinationForm').reset();
    document.getElementById('destinationForm').action = `/add_destination/${journeyId}`;
    document.getElementById('modalTitle').textContent = 'Add Destination';
    document.getElementById('submitBtn').textContent = 'Save';
    modal.classList.add('show');
}

function openEditModal(button) {
    const modal = document.getElementById('destinationModal');
    const form = document.getElementById('destinationForm');

    document.getElementById('place_name').value = button.getAttribute('data-name');
    document.getElementById('visit_order').value = button.getAttribute('data-order');
    document.getElementById('visit_status').value = button.getAttribute('data-status');
    document.getElementById('is_main').value = button.getAttribute('data-is_main');
    document.getElementById('map').value = button.getAttribute('data-map');

    form.action = `/edit_destination/${button.getAttribute('data-id')}`;
    window.currentEditingDestId = button.getAttribute('data-id');

    document.getElementById('deleteDestBtn').style.display = 'block';
    document.getElementById('modalTitle').textContent = 'Edit Destination';
    document.getElementById('submitBtn').textContent = 'Update';
    modal.classList.add('show');
}

function closeDestinationModal() {
    document.getElementById('destinationModal').classList.remove('show');
    document.getElementById('deleteDestBtn').style.display = 'none';
}

function openEditJourneyModal() {
    document.getElementById('edit_j_name').value = journeyData.name;
    document.getElementById('edit_start_date').value = journeyData.startDate;
    document.getElementById('edit_end_date').value = journeyData.endDate;
    document.getElementById('edit_description').value = journeyData.description;
    document.getElementById('editJourneyModal').classList.add('show');
}

function closeEditJourneyModal() { document.getElementById('editJourneyModal').classList.remove('show'); }
function openBudgetModal() { document.getElementById('budgetModal').classList.add('show'); }
function closeBudgetModal() { document.getElementById('budgetModal').classList.remove('show'); }

window.addEventListener('click', function (e) {
    if (e.target.classList.contains('modal')) e.target.classList.remove('show');
});

// Form Submissions
document.getElementById('destinationForm').addEventListener('submit', function (e) {
    e.preventDefault();
    fetch(this.action, { method: 'POST', body: new FormData(this) })
        .then(r => r.json()).then(d => d.success ? location.reload() : alert('Error.'));
});

document.getElementById('editJourneyForm').addEventListener('submit', function (e) {
    e.preventDefault();
    fetch(`/edit_journey/${journeyId}`, { method: 'POST', body: new FormData(this) })
        .then(r => r.json()).then(d => d.success ? location.reload() : alert('Error.'));
});

document.getElementById('budgetForm').addEventListener('submit', function (e) {
    e.preventDefault();
    fetch(`/add_budget/${journeyId}`, { method: 'POST', body: new FormData(this) })
        .then(r => r.json()).then(d => d.success ? location.reload() : alert('Error.'));
});

const expenseForm = document.getElementById('expenseForm');
if (expenseForm) {
    expenseForm.addEventListener('submit', function (e) {
        e.preventDefault();
        fetch(`/add_expense/${journeyId}`, { method: 'POST', body: new FormData(this) })
            .then(r => r.json()).then(d => d.success ? location.reload() : alert('Error.'));
    });
}

// Deletions & Toggles
function deleteDestination() {
    if (confirm('Delete this destination?')) {
        fetch(`/delete_destination/${window.currentEditingDestId}`, { method: 'POST' })
            .then(r => r.json()).then(d => d.success ? location.reload() : alert('Error.'));
    }
}

function deleteJourney() {
    if (confirm('Delete this journey? This action cannot be undone.')) {
        fetch(`/delete_journey/${journeyId}`, { method: 'POST' })
            .then(r => r.json()).then(d => d.success ? window.location.href = '/dashboard' : alert('Error.'));
    }
}

function deleteExpense(expenseId) {
    if (confirm('Delete this expense?')) {
        fetch(`/delete_expense/${expenseId}`, { method: 'POST' })
            .then(r => r.json()).then(d => d.success ? location.reload() : alert('Error.'));
    }
}

function toggleStatus(destId, buttonElement) {
    fetch(`/toggle_status/${destId}`, { method: 'POST' })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                const badge = document.getElementById(`status-${destId}`);
                badge.textContent = data.new_status.charAt(0).toUpperCase() + data.new_status.slice(1);
                badge.className = `status-pill status-${data.new_status}`;
            }
        });
}

// Reminders Real-time Update (Adjusted for new HTML structure)
function updateReminders() {
    fetch(`/get_journey_reminders/${journeyId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const remindersContainer = document.getElementById('remindersContainer');
                const badge = document.querySelector('.reminders-header .badge');
                if (badge) badge.textContent = data.reminders.length;

                const currentIds = new Set(Array.from(document.querySelectorAll('.reminder-item')).map(el => parseInt(el.getAttribute('data-reminder-id'))));
                const apiIds = new Set(data.reminders.map(r => r.Rid));

                currentIds.forEach(id => {
                    if (!apiIds.has(id)) {
                        const el = document.querySelector(`[data-reminder-id="${id}"]`);
                        if (el) el.remove();
                    }
                });

                data.reminders.forEach(reminder => {
                    if (!currentIds.has(reminder.Rid)) {
                        const emptyMsg = remindersContainer.querySelector('.reminders-empty');
                        if (emptyMsg) emptyMsg.remove();

                        const div = document.createElement('div');
                        div.className = 'reminder-item';
                        div.setAttribute('data-reminder-id', reminder.Rid);
                        div.innerHTML = `
                            <div class="rem-header">
                                <span class="rem-tag">${reminder.destination_name}</span>
                                <div class="rem-dot"></div>
                            </div>
                            <div class="rem-text">${reminder.rem_text}</div>
                        `;
                        remindersContainer.prepend(div);
                    }
                });

                if (data.reminders.length === 0 && !remindersContainer.querySelector('.reminders-empty')) {
                    remindersContainer.innerHTML = `<div class="reminders-empty"><p>All caught up! No pending reminders for this journey.</p></div>`;
                }
            }
        });
}
setInterval(updateReminders, 2000);
document.addEventListener('visibilitychange', () => { if (!document.hidden) updateReminders(); });

// --- Profile Dropdown Logic ---
function toggleProfileMenu() {
    document.getElementById("profileDropdown").classList.toggle("show");
}

// Close the dropdown if the user clicks anywhere outside of it
window.addEventListener('click', function (event) {
    if (!event.target.matches('.profile-pic')) {
        const dropdowns = document.getElementsByClassName("dropdown-content");
        for (let i = 0; i < dropdowns.length; i++) {
            const openDropdown = dropdowns[i];
            if (openDropdown.classList.contains('show')) {
                openDropdown.classList.remove('show');
            }
        }
    }
});

// --- Edit Budget Modal Functions ---
function openEditBudgetModal(currentAmount) {
    const modal = document.getElementById('editBudgetModal');
    // Pre-fill the input with the current budget amount
    document.getElementById('edit_budget_amount').value = currentAmount;
    modal.classList.add('show');
}

function closeEditBudgetModal() {
    const modal = document.getElementById('editBudgetModal');
    modal.classList.remove('show');
}

// Close Edit Budget modal when clicking outside
window.addEventListener('click', function (event) {
    const modal = document.getElementById('editBudgetModal');
    if (event.target === modal) {
        closeEditBudgetModal();
    }
});

// Handle Edit Budget form submission
const editBudgetForm = document.getElementById('editBudgetForm');
if (editBudgetForm) {
    editBudgetForm.addEventListener('submit', function (e) {
        e.preventDefault();
        const formData = new FormData(this);

        fetch(`/edit_budget/${journeyId}`, {
            method: 'POST',
            body: formData
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload(); // Reload to update the UI with new budget
                } else {
                    alert('Error: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error updating budget. Please try again.');
            });
    });
}