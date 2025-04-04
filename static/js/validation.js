// Form validation functions
function validateForm(formId) {
    const form = document.getElementById(formId);
    const inputs = form.querySelectorAll('input[required]');
    let isValid = true;

    inputs.forEach(input => {
        if (!validateInput(input)) {
            isValid = false;
        }
    });

    return isValid;
}

function validateInput(input) {
    const value = input.value.trim();
    const type = input.type;
    const name = input.name;
    let isValid = true;
    let errorMessage = '';

    switch(type) {
        case 'email':
            isValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
            errorMessage = 'Please enter a valid email address';
            break;
        case 'tel':
            isValid = /^[0-9]{10}$/.test(value);
            errorMessage = 'Please enter a valid 10-digit phone number';
            break;
        case 'password':
            isValid = value.length >= 8;
            errorMessage = 'Password must be at least 8 characters long';
            break;
        default:
            isValid = value.length > 0;
            errorMessage = 'This field is required';
    }

    if (name === 'aadhar') {
        isValid = /^[0-9]{12}$/.test(value);
        errorMessage = 'Please enter a valid 12-digit Aadhar number';
    }

    showInputError(input, isValid, errorMessage);
    return isValid;
}

function showInputError(input, isValid, message) {
    const errorDiv = input.parentElement.querySelector('.error-message') || 
                    createErrorDiv(input);
    
    if (!isValid) {
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
        input.classList.add('error');
    } else {
        errorDiv.style.display = 'none';
        input.classList.remove('error');
    }
}

function createErrorDiv(input) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    input.parentElement.appendChild(errorDiv);
    return errorDiv;
} 