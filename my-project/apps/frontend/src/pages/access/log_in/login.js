document.addEventListener('DOMContentLoaded', () => {
    const togglePassword = document.getElementById('togglePassword');
    const password = document.getElementById('password');

    togglePassword.addEventListener('click', () => {
        const type = password.getAttribute('type') === 'password' ? 'text' : 'password';
        password.setAttribute('type', type);
        togglePassword.querySelector('i').classList.toggle('bi-eye');
        togglePassword.querySelector('i').classList.toggle('bi-eye-slash');
    });
});

document.getElementById("loginForm").addEventListener("submit", async function (e) {
    e.preventDefault();

    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    try {
        const response = await fetch("http://127.0.0.1:5000/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            credentials: "include",
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (response.ok && data.success) {
            if (data.requires_otp) {
                if (data.auth_method === 'sms') {
                    window.location.href = "../../auth-methods/sms-otp/verification/verification.html";
                } else {
                    window.location.href = "../../auth-methods/totp/verification/verification.html";
                }
            } else {
                window.location.href = "../../index/index.html";
            }
        } else {
            document.getElementById("loginMessage").textContent = data.error || "Error al iniciar sesión.";
        }
    } catch (error) {
        document.getElementById("loginMessage").textContent = "Error de conexión con el servidor.";
        console.error(error);
    }
});