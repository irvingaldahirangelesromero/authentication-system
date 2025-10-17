
document.addEventListener('DOMContentLoaded', () => {
    // Manejo de mostrar/ocultar contraseña
    const togglePassword = document.getElementById('togglePassword');
    const toggleConfirmPassword = document.getElementById('toggleConfirmPassword');
    const password = document.getElementById('password');
    const confirmPassword = document.getElementById('confirmPassword');

    togglePassword.addEventListener('click', () => {
        const type = password.getAttribute('type') === 'password' ? 'text' : 'password';
        password.setAttribute('type', type);
        togglePassword.querySelector('i').classList.toggle('bi-eye');
        togglePassword.querySelector('i').classList.toggle('bi-eye-slash');
    });

    toggleConfirmPassword.addEventListener('click', () => {
        const type = confirmPassword.getAttribute('type') === 'password' ? 'text' : 'password';
        confirmPassword.setAttribute('type', type);
        toggleConfirmPassword.querySelector('i').classList.toggle('bi-eye');
        toggleConfirmPassword.querySelector('i').classList.toggle('bi-eye-slash');
    });
});

document.getElementById("registerBtn").addEventListener("click", async () => {
    const first_name = document.getElementById("first_name").value;
    const email = document.getElementById("your_email").value;
    const password = document.getElementById("password").value;
    const authMethod = document.querySelector('input[name="authMethod"]:checked').value;
    const phone_number = document.getElementById("phone_number").value;

    if (!email || !email.includes("@")) {
        alert("Por favor ingresa un correo válido.");
        return;
    }

    const confirmPassword = document.getElementById("confirmPassword").value;

    if (!password || password.length < 6) {
        alert("La contraseña debe tener al menos 6 caracteres.");
        return;
    }

    if (password !== confirmPassword) {
        alert("Las contraseñas no coinciden.");
        return;
    }

    if (!phone_number) {
        alert("Por favor ingresa un número de teléfono.");
        return;
    }

    try {
        const response = await fetch("http://127.0.0.1:5000/register", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            credentials: "include", 
            body: JSON.stringify({ 
                email, 
                password, 
                first_name, 
                auth_method: authMethod,
                phone_number: phone_number 
            })
        });

        const data = await response.json();

        if (response.ok) {
            if (authMethod === 'totp') {
                alert("Usuario registrado correctamente. Escanea el QR en la app de autenticación.");
                window.location.href = "../../auth-methods/totp/qr_scan/qr.html";
            } else {
                alert("Usuario registrado correctamente. Se enviará un código por SMS.");
                window.location.href = "../../auth-methods/sms-otp/verification/verification.html";
            }
        } else {
            alert("Error: " + data.error);
        }
    } catch (error) {
        alert("Error al conectar con el servidor.");
        console.error(error);
    }
});