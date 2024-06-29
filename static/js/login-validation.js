// login page
document.getElementById('loginform').addEventListener('submit', function(event) {
    let isValid = true;
  
    // Validate Username
    const username = document.getElementById('username').value.trim(); // Trim whitespace
    const usernameError = document.getElementById('usernameError');
    const usernameRegex = /^[a-zA-Z][a-zA-Z0-9]{5,14}$/;
    
    if (!usernameRegex.test(username)) {
        usernameError.innerHTML = 'Username must:<br>- Start with a letter<br>- Be 6-15 characters long<br>- Contain no special characters or spaces.';
        isValid = false;
    } else {
        usernameError.textContent = '';
    }
  
    // Validate Password
    const password = document.getElementById('password').value;
    const passwordError = document.getElementById('passwordError');
    const passwordRegex = /^[a-zA-Z0-9]{7,15}$/;
    
    if (!passwordRegex.test(password)) {
        passwordError.innerHTML = 'Password must:<br>- Be 7-15 characters long<br>- Contain no special characters or spaces.';
        isValid = false;
    } else {
        passwordError.textContent = '';
    }
  
    // Clear other error messages if they are not related to the current input
    if (!isValid) {
        event.preventDefault();
    }
    // Clear username error if username is valid
    if (usernameRegex.test(username)) {
        usernameError.textContent = '';
    }
    // Clear password error if password is valid
    if (passwordRegex.test(password)) {
        passwordError.textContent = '';
    }

    if (!isValid) {
        event.preventDefault();
    }
});