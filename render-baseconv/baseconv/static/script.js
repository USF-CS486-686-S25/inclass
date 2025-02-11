const decimalInput = document.getElementById('decimal');
const binaryInput = document.getElementById('binary');
const hexadecimalInput = document.getElementById('hexadecimal');
const errorMessage = document.getElementById('error-message');

const MAX_VALUE = 2147483647;
const MIN_VALUE = -2147483648;
const API_BASE_URL = ''; // Using relative paths since we're serving from the same domain

function validateInput(input, base) {
    if (!input) {
        errorMessage.textContent = '';
        return false;
    }
    
    if (base === 10) {
        const num = parseInt(input, 10);
        if (isNaN(num) || num > MAX_VALUE || num < MIN_VALUE) {
            errorMessage.textContent = 'Invalid 32-bit decimal value';
            return false;
        }
    } else if (base === 2) {
        if (!/^[01]+$/.test(input)) {
            errorMessage.textContent = 'Invalid binary value';
            return false;
        }
        const num = parseInt(input, 2);
        if (num > MAX_VALUE) {
            errorMessage.textContent = 'Value too large for 32-bit';
            return false;
        }
    } else if (base === 16) {
        if (!/^[0-9a-fA-F]+$/.test(input)) {
            errorMessage.textContent = 'Invalid hexadecimal value';
            return false;
        }
        const num = parseInt(input, 16);
        if (num > MAX_VALUE) {
            errorMessage.textContent = 'Value too large for 32-bit';
            return false;
        }
    }
    errorMessage.textContent = '';
    return true;
}

function clearOtherInputs(currentInput) {
    if (currentInput !== decimalInput) decimalInput.value = '';
    if (currentInput !== binaryInput) binaryInput.value = '';
    if (currentInput !== hexadecimalInput) hexadecimalInput.value = '';
}

async function convertDecimal(value) {
    try {
        console.log('Converting decimal:', value);
        const response = await fetch(`${API_BASE_URL}/convert/decimal?value=${value}`);
        console.log('Response status:', response.status);
        
        if (response.ok) {
            const data = await response.json();
            console.log('Conversion result:', data);
            binaryInput.value = data.binary;
            hexadecimalInput.value = data.hexadecimal;
        } else {
            const errorData = await response.json();
            console.error('API error:', errorData);
            errorMessage.textContent = errorData.detail || 'Conversion failed';
            clearOtherInputs(decimalInput);
        }
    } catch (error) {
        console.error('Network error:', error);
        errorMessage.textContent = 'Failed to connect to conversion service';
        clearOtherInputs(decimalInput);
    }
}

async function convertBinary(value) {
    try {
        console.log('Converting binary:', value);
        const response = await fetch(`${API_BASE_URL}/convert/binary?value=${value}`);
        console.log('Response status:', response.status);
        
        if (response.ok) {
            const data = await response.json();
            console.log('Conversion result:', data);
            decimalInput.value = data.decimal;
            hexadecimalInput.value = data.hexadecimal;
        } else {
            const errorData = await response.json();
            console.error('API error:', errorData);
            errorMessage.textContent = errorData.detail || 'Conversion failed';
            clearOtherInputs(binaryInput);
        }
    } catch (error) {
        console.error('Network error:', error);
        errorMessage.textContent = 'Failed to connect to conversion service';
        clearOtherInputs(binaryInput);
    }
}

async function convertHexadecimal(value) {
    try {
        console.log('Converting hexadecimal:', value);
        const response = await fetch(`${API_BASE_URL}/convert/hexadecimal?value=${value}`);
        console.log('Response status:', response.status);
        
        if (response.ok) {
            const data = await response.json();
            console.log('Conversion result:', data);
            decimalInput.value = data.decimal;
            binaryInput.value = data.binary;
        } else {
            const errorData = await response.json();
            console.error('API error:', errorData);
            errorMessage.textContent = errorData.detail || 'Conversion failed';
            clearOtherInputs(hexadecimalInput);
        }
    } catch (error) {
        console.error('Network error:', error);
        errorMessage.textContent = 'Failed to connect to conversion service';
        clearOtherInputs(hexadecimalInput);
    }
}

decimalInput.addEventListener('input', () => {
    const value = decimalInput.value.trim();
    if (!value) {
        binaryInput.value = '';
        hexadecimalInput.value = '';
        errorMessage.textContent = '';
        return;
    }
    if (validateInput(value, 10)) {
        convertDecimal(value);
    }
});

binaryInput.addEventListener('input', () => {
    const value = binaryInput.value.trim();
    if (!value) {
        decimalInput.value = '';
        hexadecimalInput.value = '';
        errorMessage.textContent = '';
        return;
    }
    if (validateInput(value, 2)) {
        convertBinary(value);
    }
});

hexadecimalInput.addEventListener('input', () => {
    const value = hexadecimalInput.value.trim();
    if (!value) {
        decimalInput.value = '';
        binaryInput.value = '';
        errorMessage.textContent = '';
        return;
    }
    if (validateInput(value, 16)) {
        convertHexadecimal(value);
    }
});

// Log when the script loads
console.log('Number conversion script loaded');