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
                <p class="section-intro">Sign in to enter your nutrition targets and get meal recommendations.</p>
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

    // Wrapper section with clear intro
    const section = document.createElement("div");
    section.id = "meal-builder-section";
    section.innerHTML = '<p class="section-intro">Enter your target amounts below (at least one). Leave others blank if you don’t have a preference. Then click <strong>Get my meal plan</strong> to see recommendations.</p>';

    const form = document.createElement("form");
    form.id = "meal-form";

    const inputs = [
        { id: "protein", label: "Protein (g)", placeholder: "e.g. 50" },
        { id: "calories", label: "Calories", placeholder: "e.g. 500" },
        { id: "fats", label: "Fats (g)", placeholder: "e.g. 30" },
        { id: "carbs", label: "Carbs (g)", placeholder: "e.g. 100" },
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
        inputField.placeholder = input.placeholder;
        inputField.min = "0";
        inputField.step = "1";

        inputWrapper.appendChild(label);
        inputWrapper.appendChild(inputField);
        form.appendChild(inputWrapper);
    });

    section.appendChild(form);

    const submitButton = document.createElement("button");
    submitButton.textContent = "Get my meal plan";
    submitButton.id = "get-meal-btn";
    submitButton.type = "button";
    section.appendChild(submitButton);

    container.appendChild(section);

    submitButton.addEventListener("click", () => {
        const inputFields = Array.from(form.querySelectorAll("input"));
        const values = inputFields.reduce((acc, input) => {
            acc[input.id] = input.value;
            return acc;
        }, {});

        const filledKey = Object.keys(values).find(key => values[key] !== "");
        const filledValue = filledKey ? values[filledKey] : null;
        if (!filledKey || !filledValue) {
            alert("Please enter at least one target (e.g. protein or calories).");
            return;
        }

        fetch('/generate_meal', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({
                goal: filledKey === "fats" ? "fat" : filledKey === "carbs" ? "carbs" : filledKey,
                target_amount: parseFloat(filledValue),
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
                if (data && !data.error) {
                    sessionStorage.setItem('apiResults', JSON.stringify(data));
                    window.location.href = "results.html";
                } else if (data && data.error) {
                    alert(data.error || 'Failed to generate meal plan');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Something went wrong. Please try again.');
            });
    });
});
