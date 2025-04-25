document.addEventListener('DOMContentLoaded', function() {
    const goalForm = document.getElementById('goalForm');
    const goalList = document.getElementById('goalList');
    const goalTypeSelect = document.getElementById('goalType');
    const targetInput = document.getElementById('target');
    const endDateInput = document.getElementById('endDate');

    // Update target input placeholder based on goal type
    goalTypeSelect.addEventListener('change', function() {
        const goalType = this.value;
        if (goalType === 'WEIGHT') {
            targetInput.placeholder = 'Enter target weight in kg';
        } else if (goalType === 'WORKOUTS') {
            targetInput.placeholder = 'Enter number of workouts per week';
        } else if (goalType === 'CALORIES') {
            targetInput.placeholder = 'Enter target calories per day';
        }
    });

    // Handle goal form submission
    goalForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(goalForm);
        
        fetch('/workouts/add-goal/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                addGoalToList(data);
                goalForm.reset();
            } else {
                alert('Error adding goal: ' + Object.values(data.errors).join(', '));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error adding goal. Please try again.');
        });
    });

    // Add goal to the list
    function addGoalToList(goal) {
        const goalElement = document.createElement('div');
        goalElement.className = 'goal-item';
        goalElement.dataset.goalId = goal.goal_id;
        
        goalElement.innerHTML = `
            <div class="goal-header">
                <h3>${goal.goal_type_display}</h3>
                <div class="goal-actions">
                    <button class="edit-btn" onclick="editGoal(${goal.goal_id})">Edit</button>
                    <button class="delete-btn" onclick="deleteGoal(${goal.goal_id})">Delete</button>
                </div>
            </div>
            <div class="goal-details">
                <p>Target: ${goal.target}</p>
                <p>Progress: ${goal.progress}%</p>
                ${goal.end_date ? `<p>End Date: ${goal.end_date}</p>` : ''}
            </div>
            <div class="progress-bar">
                <div class="progress" style="width: ${goal.progress}%"></div>
            </div>
        `;
        
        goalList.appendChild(goalElement);
    }

    // Edit goal
    window.editGoal = function(goalId) {
        fetch(`/workouts/get-goal/${goalId}/`)
            .then(response => response.json())
            .then(goal => {
                goalTypeSelect.value = goal.goal_type;
                targetInput.value = goal.target;
                endDateInput.value = goal.end_date || '';
                
                // Update form action
                goalForm.action = `/workouts/update-goal/${goalId}/`;
                
                // Change submit button text
                const submitBtn = goalForm.querySelector('button[type="submit"]');
                submitBtn.textContent = 'Update Goal';
                
                // Scroll to form
                goalForm.scrollIntoView({ behavior: 'smooth' });
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error loading goal. Please try again.');
            });
    };

    // Delete goal
    window.deleteGoal = function(goalId) {
        if (confirm('Are you sure you want to delete this goal?')) {
            fetch(`/workouts/delete-goal/${goalId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const goalElement = document.querySelector(`[data-goal-id="${goalId}"]`);
                    goalElement.remove();
                } else {
                    alert('Error deleting goal. Please try again.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error deleting goal. Please try again.');
            });
        }
    };

    // Helper function to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
}); 