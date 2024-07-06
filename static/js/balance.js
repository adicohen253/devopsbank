document.addEventListener("DOMContentLoaded", function() {
    // Replace this with your actual balance value from your server-side code
    const balanceValue = parseFloat(document.getElementById("balance").textContent);

    // Get the balance element
    const balanceElement = document.getElementById("balance");

    // Check the balance and apply the appropriate class
    if (balanceValue > 0) {
        balanceElement.classList.add("positive-balance");
    } 
    else if (balanceValue < 0) {
        balanceElement.classList.add("non-positive-balance");
    }
});

document.getElementById('amount').addEventListener('input', function(event) {
    const amountInput = event.target;
    const pattern = /^[0-9]+([.,][0-9]{1,2})?$/;
    const errorMessageElement = document.getElementById('error-message');

    if (!pattern.test(amountInput.value)) {
        amountInput.setCustomValidity('Please enter a valid number up to two decimal digits.');
    } else {
        amountInput.setCustomValidity('');
        errorMessageElement.textContent = '';
    }
});