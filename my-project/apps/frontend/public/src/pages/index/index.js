// Ruta: authentication-system/my-project/apps/frontend/public/src/pages/index/index.js
async function cerrarSesion() {
    try {
        // Intentar cerrar sesión en ambos servicios
        await Promise.allSettled([
            fetch('https://authentication-system-8jpe.onrender.com/logout', {
                method: 'POST',
                credentials: 'include'
            }),
            fetch('https://authentication-system-xp73.onrender.com/logout', {
                method: 'POST', 
                credentials: 'include'
            })
        ]);
    } catch (e) {
        console.error('Logout failed', e);
    }
    
    // Limpiar localStorage
    localStorage.removeItem('pending_verification_email');
    localStorage.removeItem('user_email');
    localStorage.removeItem('user_auth_method');
    
    // Redirigir al login
    window.location.replace('../access/log_in/login.html');
}

async function cargarUsuario() {
    try {
        console.log('🔍 Verificando sesión en dashboard...');
        
        // Obtener información del método de autenticación desde localStorage
        const userEmail = localStorage.getItem('user_email');
        const authMethod = localStorage.getItem('user_auth_method');
        
        console.log('📋 Información localStorage:', { userEmail, authMethod });
        
        // PRIMERO intentar con el servicio basado en el método de autenticación
        if (authMethod === 'sms') {
            console.log('📱 Verificando sesión SMS OTP...');
            let resp = await fetch('https://authentication-system-xp73.onrender.com/user-info', {
                method: 'GET',
                credentials: 'include'
            });
            
            if (resp.ok) {
                const data = await resp.json();
                console.log('✅ Sesión SMS OTP activa:', data);
                document.getElementById('welcome-text').textContent =
                    `¡Bienvenido ${data.first_name || 'Usuario'}!`;
                return;
            }
        } else {
            // Por defecto o TOTP, intentar con servicio TOTP
            console.log('🔐 Verificando sesión TOTP...');
            let resp = await fetch('https://authentication-system-8jpe.onrender.com/user-info', {
                method: 'GET',
                credentials: 'include'
            });
            
            if (resp.ok) {
                const data = await resp.json();
                console.log('✅ Sesión TOTP activa:', data);
                document.getElementById('welcome-text').textContent =
                    `¡Bienvenido ${data.first_name || 'Usuario'}!`;
                return;
            }
        }
        
        // SI FALLA el método preferido, intentar con el otro
        console.log('🔄 Intentando método alternativo...');
        let resp = await fetch('https://authentication-system-xp73.onrender.com/user-info', {
            method: 'GET',
            credentials: 'include'
        });
        
        if (resp.ok) {
            const data = await resp.json();
            console.log('✅ Sesión SMS OTP activa (método alternativo):', data);
            document.getElementById('welcome-text').textContent =
                `¡Bienvenido ${data.first_name || 'Usuario'}!`;
            // Actualizar localStorage
            localStorage.setItem('user_auth_method', 'sms');
            return;
        }
        
        resp = await fetch('https://authentication-system-8jpe.onrender.com/user-info', {
            method: 'GET',
            credentials: 'include'
        });
        
        if (resp.ok) {
            const data = await resp.json();
            console.log('✅ Sesión TOTP activa (método alternativo):', data);
            document.getElementById('welcome-text').textContent =
                `¡Bienvenido ${data.first_name || 'Usuario'}!`;
            // Actualizar localStorage
            localStorage.setItem('user_auth_method', 'totp');
            return;
        }
        
        // SI AMBOS FALLAN, redirigir al login
        console.log('❌ No hay sesión activa en ningún servicio');
        window.location.replace('../access/log_in/login.html');
        
    } catch (error) {
        console.error('❌ Error cargando usuario:', error);
        window.location.replace('../access/log_in/login.html');
    }
}

// Cargar usuario cuando la página se carga
document.addEventListener('DOMContentLoaded', cargarUsuario);