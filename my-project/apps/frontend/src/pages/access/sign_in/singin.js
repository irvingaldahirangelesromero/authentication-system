
document.getElementById("registerBtn").addEventListener("click", async () => {
    const first_name = document.getElementById("first_name").value;
    const email = document.getElementById("your_email").value;
    const password = document.getElementById("password").value;

    if (!email || !email.includes("@")) {
        alert("Por favor ingresa un correo válido.");
        return;
    }

    if (!password || password.length < 6) {
        alert("La contraseña debe tener al menos 6 caracteres.");
        return;
    }

    try {
        const response = await fetch("http://127.0.0.1:5000/register", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            credentials: "include", 
            body: JSON.stringify({ email, password, first_name })
        });

        const data = await response.json();

        if (response.ok) {
            alert("Usuario registrado correctamente. Escanea el QR en la app de autenticación.");
            window.location.href = "../../auth-methods/totp/qr_scan/qr.html";
        } else {
            alert("Error: " + data.error);
        }
    } catch (error) {
        alert("Error al conectar con el servidor.");
        console.error(error);
    }
});