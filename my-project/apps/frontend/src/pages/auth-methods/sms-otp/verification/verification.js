document.addEventListener('DOMContentLoaded', () => {
    const otpInput = document.getElementById('otp');
    const verifyButton = document.getElementById('verifyOTP');
    const resendButton = document.getElementById('resendOTP');
    const messageDiv = document.getElementById('message');

    verifyButton.addEventListener('click', async () => {
        const otp = otpInput.value.trim();
        
        if (!otp || otp.length !== 6) {
            showMessage('Por favor ingresa un código válido de 6 dígitos', 'error');
            return;
        }

        try {
            const response = await fetch('/api/sms-otp/verify-otp', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ otp })
            });

            const data = await response.json();

            if (response.ok) {
                showMessage('Verificación exitosa', 'success');
                // Redirigir a la página principal después de la verificación exitosa
                setTimeout(() => {
                    window.location.href = '/';
                }, 2000);
            } else {
                showMessage(data.error || 'Código inválido', 'error');
            }
        } catch (error) {
            showMessage('Error de conexión', 'error');
            console.error('Error:', error);
        }
    });

    resendButton.addEventListener('click', async () => {
        try {
            const response = await fetch('/api/sms-otp/send-otp', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ resend: true })
            });

            const data = await response.json();

            if (response.ok) {
                showMessage('Nuevo código enviado', 'success');
            } else {
                showMessage(data.error || 'Error al reenviar el código', 'error');
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