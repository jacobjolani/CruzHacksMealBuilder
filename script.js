// Authentication functions
async function register(username, email, password) {
    const response = await fetch('/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, email, password }),
        credentials: 'include'
    });
    return response.json();
}

async function login(username, password) {
    const response = await fetch('/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
        credentials: 'include'
    });
    return response.json();
}

async function logout() {
    const response = await fetch('/logout', {
        method: 'POST',
        credentials: 'include'
    });
    return response.json();
}

async function checkAuth() {
    try {
        const response = await fetch('/api/user', {
            credentials: 'include'
        });
        if (response.ok) {
            return await response.json();
        }
        return null;
    } catch (error) {
        return null;
    }
}

document.addEventListener("DOMContentLoaded", async () => {
    // Check if user is logged in
    const user = await checkAuth();
    const container = document.getElementById("input-container");
    
    // Show login/register UI if not authenticated
    if (!user) {
        const authContainer = document.createElement("div");
        authContainer.id = "auth-container";
        authContainer.innerHTML = `
            <div class="auth-form">
                <h2>Login or Register</h2>
                <div id="auth-tabs">
                    <button id="login-tab" class="auth-tab active">Login</button>
                    <button id="register-tab" class="auth-tab">Register</button>
                </div>
                <div id="login-form" class="auth-form-content">
                    <input type="text" id="login-username" placeholder="Username" required>
                    <input type="password" id="login-password" placeholder="Password" required>
                    <button id="login-btn">Login</button>
                    <div id="login-error" class="error-message"></div>
                </div>
                <div id="register-form" class="auth-form-content" style="display: none;">
                    <input type="text" id="register-username" placeholder="Username" required>
                    <input type="email" id="register-email" placeholder="Email" required>
                    <input type="password" id="register-password" placeholder="Password" required>
                    <button id="register-btn">Register</button>
                    <div id="register-error" class="error-message"></div>
                </div>
            </div>
        `;
        container.appendChild(authContainer);
        
        // Tab switching
        document.getElementById('login-tab').addEventListener('click', () => {
            document.getElementById('login-form').style.display = 'block';
            document.getElementById('register-form').style.display = 'none';
            document.getElementById('login-tab').classList.add('active');
            document.getElementById('register-tab').classList.remove('active');
        });
        
        document.getElementById('register-tab').addEventListener('click', () => {
            document.getElementById('register-form').style.display = 'block';
            document.getElementById('login-form').style.display = 'none';
            document.getElementById('register-tab').classList.add('active');
            document.getElementById('login-tab').classList.remove('active');
        });
        
        // Login handler
        document.getElementById('login-btn').addEventListener('click', async () => {
            const username = document.getElementById('login-username').value;
            const password = document.getElementById('login-password').value;
            const errorDiv = document.getElementById('login-error');
            
            if (!username || !password) {
                errorDiv.textContent = 'Please fill in all fields';
                return;
            }
            
            const result = await login(username, password);
            if (result.error) {
                errorDiv.textContent = result.error;
            } else {
                location.reload();
            }
        });
        
        // Register handler
        document.getElementById('register-btn').addEventListener('click', async () => {
            const username = document.getElementById('register-username').value;
            const email = document.getElementById('register-email').value;
            const password = document.getElementById('register-password').value;
            const errorDiv = document.getElementById('register-error');
            
            if (!username || !email || !password) {
                errorDiv.textContent = 'Please fill in all fields';
                return;
            }
            
            const result = await register(username, email, password);
            if (result.error) {
                errorDiv.textContent = result.error;
            } else {
                location.reload();
            }
        });
        
        return; // Don't show meal form if not logged in
    }
    
    // Show logout button
    const logoutBtn = document.createElement("button");
    logoutBtn.textContent = "Logout";
    logoutBtn.id = "logout-btn";
    logoutBtn.style.marginBottom = "20px";
    logoutBtn.addEventListener('click', async () => {
        await logout();
        location.reload();
    });
    container.appendChild(logoutBtn);
    
    // Show user info
    const userInfo = document.createElement("div");
    userInfo.innerHTML = `<p>Logged in as: <strong>${user.username}</strong></p>`;
    container.appendChild(userInfo);

    const form = document.createElement("form");
    form.id = "meal-form";

    const inputs = [
        { id: "protein", label: "Protein (g)" },
        { id: "calories", label: "Calories" },
        { id: "fats", label: "Fats (g)" },
        { id: "carbs", label: "Carbs (g)" },
    ];

    inputs.forEach((input) => {
        const inputWrapper = document.createElement("div");
        inputWrapper.classList.add("input-wrapper");

        const label = document.createElement("label");
        label.textContent = input.label;
        label.setAttribute("for", input.id);

        const inputField = document.createElement("input");
        inputField.type = "number";
        inputField.id = input.id;
        inputField.name = input.id;

        inputWrapper.appendChild(label);
        inputWrapper.appendChild(inputField);
        form.appendChild(inputWrapper);
    });

    container.appendChild(form);

    const submitButton = document.createElement("button");
    submitButton.textContent = "Submit";
    container.appendChild(submitButton);

    submitButton.addEventListener("click", () => {
        const inputFields = Array.from(form.querySelectorAll("input"));
        const values = inputFields.reduce((acc, input) => {
            acc[input.id] = input.value;
            return acc;
        }, {});

        fetch('/generate_meal', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({
                goal: Object.keys(values).find(key => values[key] != ""),
                target_amount: Object.values(values).find(value => value != ""),
            }),
        })
            .then(response => {
                if (response.status === 401) {
                    alert('Please login to generate meal plans');
                    window.location.href = '/';
                    return;
                }
                return response.json();
            })
            .then(data => {
                if (data) {
                    sessionStorage.setItem('apiResults', JSON.stringify(data));
                    window.location.href = "results.html";
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
    });
});