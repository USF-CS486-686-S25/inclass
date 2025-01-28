document.addEventListener('DOMContentLoaded', () => {
    const decimalInput = document.getElementById('decimal');
    const binaryInput = document.getElementById('binary');
    const hexInput = document.getElementById('hex');

    const decimalError = document.getElementById('decimal-error');
    const binaryError = document.getElementById('binary-error');
    const hexError = document.getElementById('hex-error');

    function hideAllErrors() {
        decimalError.style.display = 'none';
        binaryError.style.display = 'none';
        hexError.style.display = 'none';
    }

    async function convertNumber(value, fromBase) {
        try {
            const response = await fetch('/convert', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    value: value,
                    from_base: fromBase
                })
            });

            if (!response.ok) {
                throw new Error('Conversion failed');
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error:', error);
            return null;
        }
    }

    async function updateInputs(value, fromBase) {
        hideAllErrors();
        
        if (!value) {
            decimalInput.value = '';
            binaryInput.value = '';
            hexInput.value = '';
            return;
        }

        const result = await convertNumber(value, fromBase);
        if (!result) {
            document.getElementById(`${fromBase}-error`).style.display = 'block';
            return;
        }

        decimalInput.value = result.decimal;
        binaryInput.value = result.binary;
        hexInput.value = result.hex;
    }

    decimalInput.addEventListener('input', (e) => {
        updateInputs(e.target.value.trim(), 'decimal');
    });

    binaryInput.addEventListener('input', (e) => {
        updateInputs(e.target.value.trim(), 'binary');
    });

    hexInput.addEventListener('input', (e) => {
        updateInputs(e.target.value.trim(), 'hex');
    });
});
