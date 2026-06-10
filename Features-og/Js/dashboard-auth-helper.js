// dashboard-auth-helper.js
// Funciones para conectar el dashboard con la API de autenticación

const API_URL = "http://localhost:8000/api/auth";

class LynkoAuth {
    
    /**
     * Obtener token del localStorage
     */
    static getToken() {
        return localStorage.getItem("token");
    }

    /**
     * Obtener datos del usuario del localStorage
     */
    static getUser() {
        const userStr = localStorage.getItem("user");
        return userStr ? JSON.parse(userStr) : null;
    }

    /**
     * Verificar si el usuario está autenticado
     */
    static isAuthenticated() {
        return !!this.getToken();
    }

    /**
     * Obtener información del usuario actual desde la API
     */
    static async getCurrentUser() {
        const token = this.getToken();
        
        if (!token) {
            console.error("No token found");
            return null;
        }

        try {
            const response = await fetch(`${API_URL}/me?token=${token}`, {
                method: "GET",
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            });

            if (response.ok) {
                const user = await response.json();
                // Actualizar localStorage con datos frescos
                localStorage.setItem("user", JSON.stringify(user));
                return user;
            } else if (response.status === 401) {
                // Token inválido o expirado
                this.logout();
                return null;
            }
        } catch (error) {
            console.error("Error fetching current user:", error);
        }
        
        return null;
    }

    /**
     * Cerrar sesión
     */
    static logout() {
        localStorage.removeItem("token");
        localStorage.removeItem("user");
        window.location.href = "login.html";
    }

    /**
     * Verificar autenticación al cargar página
     * Redirigir a login si no está autenticado
     */
    static checkAuth() {
        if (!this.isAuthenticated()) {
            window.location.href = "login.html";
        }
    }

    /**
     * Actualizar datos del usuario en el dashboard
     * Ejemplo: mostrar nombre y XP
     */
    static updateDashboard() {
        const user = this.getUser();
        
        if (user) {
            // Ejemplo: actualizar elementos HTML
            const nameElement = document.getElementById("userName");
            const xpElement = document.getElementById("userXP");
            const levelElement = document.getElementById("userLevel");

            if (nameElement) nameElement.textContent = user.name;
            if (xpElement) xpElement.textContent = user.xp || 0;
            if (levelElement) levelElement.textContent = user.level || 1;
        }
    }

    /**
     * Hacer request autenticado a la API
     */
    static async authenticatedFetch(url, options = {}) {
        const token = this.getToken();
        
        const headers = {
            ...options.headers,
            "Authorization": `Bearer ${token}`
        };

        const response = await fetch(url, {
            ...options,
            headers
        });

        if (response.status === 401) {
            // Token expirado
            this.logout();
        }

        return response;
    }
}

// ===== USO EN DASHBOARD =====

// Al cargar el dashboard:
document.addEventListener("DOMContentLoaded", () => {
    // 1. Verificar que usuario está autenticado
    LynkoAuth.checkAuth();
    
    // 2. Cargar y mostrar datos del usuario
    LynkoAuth.updateDashboard();
    
    // 3. (Opcional) Obtener datos frescos de la API
    // LynkoAuth.getCurrentUser();
    
    // 4. Configurar botón de logout
    const logoutBtn = document.getElementById("logoutBtn");
    if (logoutBtn) {
        logoutBtn.addEventListener("click", () => {
            LynkoAuth.logout();
        });
    }
});

// ===== EJEMPLO: Obtener datos de la API protegida =====

async function getProtectedData() {
    const response = await LynkoAuth.authenticatedFetch(
        "http://localhost:8000/api/content/subjects",
        { method: "GET" }
    );

    if (response.ok) {
        const data = await response.json();
        console.log("Protected data:", data);
        return data;
    }
}

// ===== EJEMPLO: Hacer POST con autenticación =====

async function updateUserXP(amount) {
    const response = await LynkoAuth.authenticatedFetch(
        "http://localhost:8000/api/users/xp",
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ xp_amount: amount })
        }
    );

    if (response.ok) {
        const data = await response.json();
        console.log("XP updated:", data);
        // Actualizar dashboard
        LynkoAuth.updateDashboard();
    }
}

// ===== EN INICIO_LYNKO.HTML =====

// <!DOCTYPE html>
// <html>
// <head>
//     <script src="dashboard-auth-helper.js"></script>
// </head>
// <body>
//     <div class="navbar">
//         <h2>Hola, <span id="userName">Usuario</span>!</h2>
//         <div>
//             <span>Nivel: <span id="userLevel">1</span></span>
//             <span>XP: <span id="userXP">0</span></span>
//         </div>
//         <button id="logoutBtn">Cerrar sesión</button>
//     </div>
//     
//     <div class="dashboard">
//         <!-- Contenido del dashboard -->
//     </div>
// </body>
// </html>
