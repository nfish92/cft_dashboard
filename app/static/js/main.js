// --- app/static/js/main.js ---
// JavaScript to handle real-time alert updates and flag form submissions

// Initialize Socket.IO for live alert push
const socket = io();

// Listen for "new_alert" events from server via WebSocket
socket.on('new_alert', ({ uuid }) => {
  // When a new alert is pushed, reload the page (simple method)
  window.location.reload();
});

// Function to handle submitting a flag for an alert
function handleSubmitForm(form) {
  form.addEventListener('submit', async (e) => {
    e.preventDefault(); // Prevent normal form submission

    const row = form.closest('tr'); // Get the table row containing this form
    const uuid = form.querySelector('input[name="uuid"]').value;
    const flag = form.querySelector('input[name="flag"]').value;
    const resultCell = row.querySelector('.result-cell');

    try {
      // Submit flag to backend via AJAX
      const response = await fetch('/submit_flag', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({ uuid, flag })
      });
      const data = await response.json();

      // Update the Result cell based on response
      resultCell.textContent = data.message;
      resultCell.style.color = data.success ? 'green' : 'red';

      // Disable form after correct submission
      if (data.success) {
        form.querySelector('button').disabled = true;
      }
    } catch (err) {
      console.error('Submission error', err);
      resultCell.textContent = 'Error submitting flag';
      resultCell.style.color = 'red';
    }
  });
}

// Attach event listeners to all forms once page loads
document.addEventListener('DOMContentLoaded', () => {
  // Attach to existing forms
  document.querySelectorAll('.submit-form').forEach(handleSubmitForm);

  // Delegate form handlers for any new alerts dynamically added via WebSocket
  document.getElementById('alerts-body').addEventListener('submit', (e) => {
    if (e.target.classList.contains('submit-form')) {
      handleSubmitForm(e.target);
    }
  });
});
