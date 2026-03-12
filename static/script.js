// Localhost URL for testing. Change this to your Render backend URL once deployed.
const API_BASE = "http://127.0.0.1:10000/api";

// DOM Elements
const loginView = document.getElementById("login-view");
const dashboardView = document.getElementById("dashboard-view");
const loginError = document.getElementById("login-error");
const loadingMsg = document.getElementById("loading-msg");
const dataContainer = document.getElementById("data-container");

// --- UI Routing ---
function showDashboard() {
  loginView.classList.add("hidden");
  dashboardView.classList.remove("hidden");
  loadingMsg.classList.remove("hidden");
  dataContainer.classList.add("hidden");
  fetchSummary(); // Fetch secure data only after showing the dashboard
}

function showLogin() {
  dashboardView.classList.add("hidden");
  loginView.classList.remove("hidden");
  document.getElementById("password").value = ""; // Clear password for security
}

// Auto-login check on page load
if (localStorage.getItem("compass_token")) {
  showDashboard();
}

// --- API Calls ---
async function handleLogin() {
  const userId = document.getElementById("user_id").value;
  const password = document.getElementById("password").value;

  loginError.classList.add("hidden");

  try {
    const response = await fetch(`${API_BASE}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: userId, password: password }),
    });

    if (response.ok) {
      const data = await response.json();
      localStorage.setItem("compass_token", data.token); // Store VIP pass
      showDashboard();
    } else {
      loginError.classList.remove("hidden");
    }
  } catch (error) {
    console.error("Login connection failed:", error);
    loginError.textContent = "Cannot connect to server.";
    loginError.classList.remove("hidden");
  }
}

async function fetchSummary() {
  const token = localStorage.getItem("compass_token");

  try {
    const response = await fetch(`${API_BASE}/summary`, {
      headers: {
        Authorization: `Bearer ${token}`, // Attach VIP pass to request
      },
    });

    if (!response.ok) {
      throw new Error("Unauthorized");
    }

    const data = await response.json();

    // Populate UI
    document.getElementById("balance").textContent =
      `${data.currency} ${data.total_balance.toLocaleString()}`;
    document.getElementById("expenses").textContent =
      `${data.currency} ${data.monthly_expenses.toLocaleString()}`;

    // Hide loader, show data
    loadingMsg.classList.add("hidden");
    dataContainer.classList.remove("hidden");
  } catch (error) {
    console.error("Access denied:", error);
    // If token is bad or missing, boot them back to login
    handleLogout();
  }
}

function handleLogout() {
  localStorage.removeItem("compass_token"); // Destroy VIP pass
  showLogin();
}
