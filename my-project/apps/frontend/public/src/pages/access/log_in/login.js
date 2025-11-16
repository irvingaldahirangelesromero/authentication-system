document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Login page loaded');

    const togglePassword = document.getElementById('togglePassword');
    const password = document.getElementById('password');
    const loginForm = document.getElementById('loginForm');
    const loginMessage = document.getElementById('loginMessage');

    // Toggle password visibility
    if (togglePassword) {
        togglePassword.addEventListener('click', () => {
            const type = password.getAttribute('type') === 'password' ? 'text' : 'password';
            password.setAttribute('type', type);
            togglePassword.querySelector('i').classList.toggle('bi-eye');
            togglePassword.querySelector('i').classList.toggle('bi-eye-slash');
        });
    }

    // Handle form submission
    if (loginForm) {
        loginForm.addEventListener('submit', async function (e) {
            e.preventDefault();
            console.log('📝 Form submitted');

            const email = document.getElementById("email").value.trim();
            const password = document.getElementById("password").value;

            if (!email || !password) {
                showMessage('Por favor completa todos los campos', 'error');
                return;
            }

            showMessage('Iniciando sesión...', 'info');

            try {
                console.log('📤 Sending login request...');

                // PRIMERO intentar con TOTP (servicio principal)
                let response = await fetch("https://authentication-system-vkmt.onrender.com/login", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    credentials: "include",
                    body: JSON.stringify({ email, password })
                });

                console.log('📨 Response status TOTP:', response.status);

                let data = await response.json();
                console.log('📦 Response data TOTP:', data);

                // Si TOTP falla o el usuario es de tipo SMS, intentar con SMS OTP
                if (!response.ok || (data.success && data.auth_method === 'sms')) {
                    console.log('🔄 Usuario es SMS o TOTP falló, intentando con SMS OTP...');
                    
                    response = await fetch("https://authentication-system-xp73.onrender.com/login", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        credentials: "include",
                        body: JSON.stringify({ email, password })
                    });
                    
                    data = await response.json();
                    console.log('📨 Response status SMS OTP:', response.status);
                    console.log('📦 Response data SMS OTP:', data);
                }

                if (response.ok && data.success) {
                    if (data.requires_otp) {
                        // Guardar email para la verificación en AMBOS localStorage
                        localStorage.setItem('pending_verification_email', email);
                        localStorage.setItem('user_email', email);

                        showMessage('Redirigiendo a verificación...', 'success');

                        setTimeout(() => {
                            if (data.auth_method === 'sms') {
                                console.log('📱 Redirigiendo a verificación SMS...');
                                window.location.href = "../../auth-methods/sms-otp/verification/verification.html";
                            } else {
                                console.log('🔐 Redirigiendo a verificación TOTP...');
                                window.location.href = "../../auth-methods/totp/verification/verification.html";
                            }
                        }, 1000);
                    } else {
                        // Login directo sin OTP
                        localStorage.setItem('user_email', email);
                        console.log('✅ Login directo exitoso, redirigiendo al dashboard...');
                        window.location.href = "../../index/index.html";
                    }
                } else {
                    showMessage(data.error || "Error al iniciar sesión", 'error');
                }
            } catch (error) {
                console.error('❌ Error:', error);
                showMessage("Error de conexión con el servidor", 'error');
            }
        });
    }

    function showMessage(message, type) {
        if (loginMessage) {
            loginMessage.textContent = message;
            loginMessage.className = `mt-3 text-center text-${type === 'error' ? 'danger' : type === 'success' ? 'success' : 'info'}`;
        }
        console.log(`💬 [${type}] ${message}`);
    }
});