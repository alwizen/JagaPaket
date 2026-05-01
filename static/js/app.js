// Global App Utilities
const App = {
  showToast: (message, type = "info") => {
    const container = document.getElementById("toast-container");
    const toast = document.createElement("div");

    let bgClass = "bg-blue-600";
    if (type === "success") bgClass = "bg-emerald-600";
    if (type === "error") bgClass = "bg-red-600";
    if (type === "warning") bgClass = "bg-amber-600";

    toast.className = `${bgClass} text-white px-6 py-3 rounded-lg shadow-lg flex items-center justify-between toast-enter`;
    toast.innerHTML = `
            <span>${message}</span>
            <button onclick="this.parentElement.remove()" class="ml-4 text-white hover:text-gray-200">
                &times;
            </button>
        `;

    container.appendChild(toast);

    setTimeout(() => {
      toast.classList.add("toast-leave");
      setTimeout(() => toast.remove(), 300);
    }, 5000);
  },

  logout: () => {
    localStorage.clear();
    document.cookie =
      "access_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    fetch("/api/auth/logout", { method: "POST" }).then(() => {
      window.location.href = "/";
    });
  },

  authHeader: () => {
    const token = localStorage.getItem("access_token");
    return token ? { Authorization: `Bearer ${token}` } : {};
  },
};

// Intercept HTMX requests to inject Authorization header if needed
document.body.addEventListener("htmx:configRequest", function (evt) {
  const token = localStorage.getItem("access_token");
  if (token) {
    evt.detail.headers["Authorization"] = `Bearer ${token}`;
  }
});

// Global error handling for HTMX 401/403
document.body.addEventListener("htmx:responseError", function (evt) {
  if (evt.detail.xhr.status === 401 || evt.detail.xhr.status === 403) {
    if (window.location.pathname !== "/") {
      App.logout();
    }
  }
});
