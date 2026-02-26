const journeyDataEl = document.getElementById('journey-data');
const journeyId = journeyDataEl.getAttribute('data-jid');

const journeyData = {
    name: journeyDataEl.getAttribute('data-name'),
    startDate: journeyDataEl.getAttribute('data-start'),
    endDate: journeyDataEl.getAttribute('data-end'),
    description: journeyDataEl.getAttribute('data-desc')
};

// Set today's date as default for expense date picker (when form loads)
document.addEventListener('DOMContentLoaded', function () {
    const expenseDateInput = document.getElementById('expense_date');
    if (expenseDateInput) {
        const today = new Date().toISOString().split('T')[0];
        expenseDateInput.value = today;
    }

    // Initialize form action
    document.getElementById('destinationForm').action = `/add_destination/${journeyId}`;
});

// View destination - navigate to destination details page
function viewDestination(destId) {
    window.location.href = `/destination/${destId}`;
}

// Open destination modal for new destination
function openDestinationModal() {
    const modal = document.getElementById('destinationModal');
    const form = document.getElementById('destinationForm');
    const modalTitle = document.getElementById('modalTitle');
    const submitBtn = document.getElementById('submitBtn');

    // Reset for new destination
    form.reset();
    form.action = `/add_destination/${journeyId}`;
    modalTitle.textContent = 'Add Destination';
    submitBtn.textContent = 'Add Destination';

    modal.classList.add('show');
}

// Open destination modal for editing
function openEditModal(button) {
    const modal = document.getElementById('destinationModal');
    const form = document.getElementById('destinationForm');
    const modalTitle = document.getElementById('modalTitle');
    const submitBtn = document.getElementById('submitBtn');
    const deleteBtn = document.getElementById('deleteDestBtn');

    // Extract data from button attributes
    const destId = button.getAttribute('data-id');
    const destName = button.getAttribute('data-name');
    const destOrder = button.getAttribute('data-order');
    const destStatus = button.getAttribute('data-status');
    const destIsMain = button.getAttribute('data-is_main');
    const destMap = button.getAttribute('data-map');

    // Populate form with destination data
    document.getElementById('place_name').value = destName;
    document.getElementById('visit_order').value = destOrder;
    document.getElementById('visit_status').value = destStatus;
    document.getElementById('is_main').value = destIsMain;
    document.getElementById('map').value = destMap;

    // Change form action to edit route
    form.action = `/edit_destination/${destId}`;

    // Store the destination ID for delete function
    window.currentEditingDestId = destId;

    // Show delete button and update modal title and button text
    deleteBtn.style.display = 'block';
    modalTitle.textContent = 'Edit Destination';
    submitBtn.textContent = 'Update Destination';

    modal.classList.add('show');
}

// Close destination modal
function closeDestinationModal() {
    const modal = document.getElementById('destinationModal');
    modal.classList.remove('show');
    document.getElementById('destinationForm').reset();
    // Hide delete button when closing modal
    document.getElementById('deleteDestBtn').style.display = 'none';
}

// Close modal when clicking outside
window.addEventListener('click', function (event) {
    const modal = document.getElementById('destinationModal');
    if (event.target === modal) {
        closeDestinationModal();
    }
});

// Handle form submission
document.getElementById('destinationForm').addEventListener('submit', function (e) {
    e.preventDefault();

    const formData = new FormData(this);
    const formAction = this.action; // Use the form's action attribute

    fetch(formAction, {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // alert('Destination added successfully!');
                closeDestinationModal();
                location.reload();
            } else {
                alert('Error. Please try again.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error. Please try again.');
        });
});

// Delete destination function
function deleteDestination() {
    if (confirm('Are you sure you want to delete this destination? This action cannot be undone.')) {
        fetch(`/delete_destination/${window.currentEditingDestId}`, {
            method: 'POST'
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    closeDestinationModal();
                    location.reload();
                } else {
                    alert('Error deleting destination. Please try again.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error deleting destination. Please try again.');
            });
    }
}


// Open Edit Journey Modal
function openEditJourneyModal() {
    const modal = document.getElementById('editJourneyModal');

    // Populate form with journey data using the safe |tojson filter
    document.getElementById('edit_j_name').value = journeyData.name;
    document.getElementById('edit_start_date').value = journeyData.startDate;
    document.getElementById('edit_end_date').value = journeyData.endDate;
    document.getElementById('edit_description').value = journeyData.description;

    modal.classList.add('show');
}

// Close Edit Journey Modal
function closeEditJourneyModal() {
    const modal = document.getElementById('editJourneyModal');
    modal.classList.remove('show');
    document.getElementById('editJourneyForm').reset();
}

// Close journey modal when clicking outside
window.addEventListener('click', function (event) {
    const journeyModal = document.getElementById('editJourneyModal');
    if (event.target === journeyModal) {
        closeEditJourneyModal();
    }
});

// Handle edit journey form submission
document.getElementById('editJourneyForm').addEventListener('submit', function (e) {
    e.preventDefault();

    const formData = new FormData(this);

    fetch(`/edit_journey/${journeyId}`, {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                closeEditJourneyModal();
                location.reload();
            } else {
                alert('Error updating journey. Please try again.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error updating journey. Please try again.');
        });
});

// Delete journey function
function deleteJourney() {
    if (confirm('Are you sure you want to delete this journey? This action cannot be undone and will delete ALL associated destinations.')) {
        fetch(`/delete_journey/${journeyId}`, {
            method: 'POST'
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    window.location.href = '/dashboard';
                } else {
                    alert('Error deleting journey. Please try again.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error deleting journey. Please try again.');
            });
    }
}

// Toggle destination status
function toggleStatus(destId, buttonElement) {
    fetch(`/toggle_status/${destId}`, {
        method: 'POST'
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update the status badge dynamically without page reload
                const statusBadge = document.getElementById(`status-${destId}`);
                statusBadge.textContent = data.new_status;

                // Change color based on status
                statusBadge.style.backgroundColor = data.new_status === 'visited' ? '#28a745' : '#667eea';
                statusBadge.style.transition = 'all 0.3s ease';
            } else {
                alert('Error toggling status. Please try again.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error toggling status. Please try again.');
        });
}

// Real-time reminder updates
let remindersContainer = document.getElementById('remindersContainer');

function updateReminders() {
    fetch(`/get_journey_reminders/${journeyId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const reminders = data.reminders;

                // Get current reminder IDs in the DOM
                const currentReminders = new Set(
                    Array.from(document.querySelectorAll('.reminder-item'))
                        .map(el => parseInt(el.getAttribute('data-reminder-id')))
                );

                // Get reminder IDs from the API
                const apiReminders = new Set(reminders.map(r => r.Rid));

                // Find reminders to remove (completed)
                currentReminders.forEach(remId => {
                    if (!apiReminders.has(remId)) {
                        // Reminder was removed/completed
                        const reminderEl = document.querySelector(`[data-reminder-id="${remId}"]`);
                        if (reminderEl) {
                            reminderEl.classList.add('removing');
                            setTimeout(() => {
                                reminderEl.remove();

                                // Show empty message if no reminders left
                                if (document.querySelectorAll('.reminder-item').length === 0) {
                                    remindersContainer.innerHTML = '<div class="reminders-empty">No pending reminders</div>';
                                }
                            }, 300);
                        }
                    }
                });

                // Find new reminders to add
                reminders.forEach(reminder => {
                    if (!currentReminders.has(reminder.Rid)) {
                        // New reminder
                        const reminderEl = document.createElement('div');
                        reminderEl.className = 'reminder-item';
                        reminderEl.setAttribute('data-reminder-id', reminder.Rid);
                        reminderEl.setAttribute('data-destination-id', reminder.Did);
                        reminderEl.innerHTML = `
                                    <div class="reminder-destination">${reminder.destination_name}</div>
                                    <div class="reminder-text">${reminder.rem_text}</div>
                                `;

                        // Remove empty message if it exists
                        const emptyMsg = remindersContainer.querySelector('.reminders-empty');
                        if (emptyMsg) {
                            emptyMsg.remove();
                        }

                        // Add to the beginning (since flex-direction: column-reverse)
                        remindersContainer.insertBefore(reminderEl, remindersContainer.firstChild);
                    }
                });
            }
        })
        .catch(error => console.error('Error updating reminders:', error));
}

// Poll for reminder updates every 2 seconds
setInterval(updateReminders, 2000);

// Also update when the user returns to the tab
document.addEventListener('visibilitychange', () => {
    if (!document.hidden) {
        updateReminders();
    }
});

// Budget Modal Functions
function openBudgetModal() {
    const modal = document.getElementById('budgetModal');
    modal.classList.add('show');
}

function closeBudgetModal() {
    const modal = document.getElementById('budgetModal');
    modal.classList.remove('show');
    document.getElementById('budgetForm').reset();
}

// Close modal when clicking outside
window.addEventListener('click', function (event) {
    const modal = document.getElementById('budgetModal');
    if (event.target === modal) {
        closeBudgetModal();
    }
});

// Handle budget form submission
document.getElementById('budgetForm').addEventListener('submit', function (e) {
    e.preventDefault();

    const formData = new FormData(this);

    fetch(`/add_budget/${journeyId}`, {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // alert('Budget set successfully!');
                location.reload();
            } else {
                alert('Error: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error setting budget. Please try again.');
        });
});
// Handle expense form submission (only if budget is set)
const expenseForm = document.getElementById('expenseForm');
if (expenseForm) {
    expenseForm.addEventListener('submit', function (e) {
        e.preventDefault();

        const formData = new FormData(this);

        fetch(`/add_expense/${journeyId}`, {
            method: 'POST',
            body: formData
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // alert('Expense added successfully!');
                    location.reload();
                } else {
                    alert('Error: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error adding expense. Please try again.');
            });
    });
}

// Delete expense function
function deleteExpense(expenseId) {
    if (!confirm('Are you sure you want to delete this expense?')) return;

    fetch(`/delete_expense/${expenseId}`, {
        method: 'POST'
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const expenseEl = document.getElementById(`expense-${expenseId}`);
                expenseEl.classList.add('removing');
                setTimeout(() => {
                    expenseEl.remove();
                    location.reload(); // Reload to update totals
                }, 300);
            } else {
                alert('Error deleting expense. Please try again.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error deleting expense. Please try again.');
        });
}