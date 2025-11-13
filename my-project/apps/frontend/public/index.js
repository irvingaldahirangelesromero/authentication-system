async function Acceder() {
    try {
        window.location.replace('/src/pages/access/log_in/login.html');
    } catch (e) {
        console.error('Logout failed', e);
    }
}