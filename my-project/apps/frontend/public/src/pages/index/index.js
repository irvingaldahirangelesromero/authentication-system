async function cerrarSesion() {
    try {
        await fetch('https://authentication-system-xp73.onrender.com/logout', {
            method: 'POST',
            credentials: 'include'
        });
    } catch (e) {
        console.error('Logout failed', e);
    }
    window.location.replace('../access/log_in/login.html');
}

async function cargarUsuario() {
    try {
        const resp = await fetch('https://authentication-system-xp73.onrender.com/user-info', {
            credentials: 'include'
        });
        if (resp.ok) {
            const data = await resp.json();
            document.getElementById('welcome-text').textContent =
                `¡Bienvenido ${data.first_name || 'Usuario'}!`;
        } else {
            window.location.replace('../access/log_in/login.html');
        }
    } catch {
        window.location.replace('../access/log_in/login.html');
    }
}
cargarUsuario();