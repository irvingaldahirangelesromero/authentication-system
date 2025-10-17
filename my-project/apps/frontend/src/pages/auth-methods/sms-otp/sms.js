document.addEventListener('DOMContentLoaded', () => {
    const phoneInput = document.getElementById('phone');
    const sendButton = document.getElementById('sendOTP');
    const messageDiv = document.getElementById('message');

    sendButton.addEventListener('click', async () => {
        const phoneNumber = phoneInput.value.trim();
        
        if (!phoneNumber) {
            showMessage('Por favor ingresa un número de teléfono', 'error');
            return;
        }

        try {
            const response = await fetch('/api/sms-otp/send-otp', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ phone_number: phoneNumber })
            });

            const data = await response.json();

            if (response.ok) {
                showMessage('Código enviado correctamente', 'success');
                // Redirigir a la página de verificación
                window.location.href = './verification/verification.html';
            } else {
                showMessage(data.error || 'Error al enviar el código', 'error');
            }
        } catch (error) {
            showMessage('Error de conexión', 'error');
            console.error('Error:', error);
        }
    });

    function showMessage(text, type) {
        messageDiv.textContent = text;
        messageDiv.className = type;
    }
});