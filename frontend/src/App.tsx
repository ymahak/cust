import { useState, useEffect } from "react";
import Chat from "./components/Chat";
import HITL from "./components/HITL";
import MonitoringDashboard from "./components/MonitoringDashboard";
import Login from "./components/Login";
import Signup from "./components/Signup";
import { getCurrentUser } from "./api";
import "./App.css";

type View = "chat" | "hitl" | "monitoring";
type AuthView = "login" | "signup";

function App() {
  const [user, setUser] = useState<{ username: string; role: string } | null>(null);
  const [loading, setLoading] = useState(true);
  const [view, setView] = useState<View>("chat");
  const [authView, setAuthView] = useState<AuthView>("login");

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      getCurrentUser()
        .then((userData) => {
          setUser(userData);
          // Set default view based on role
          if (userData.role === "admin" || userData.role === "agent") {
            setView("hitl");
          }
        })
        .catch(() => {
          localStorage.removeItem("token");
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const handleLogin = (token: string) => {
    localStorage.setItem("token", token);
    getCurrentUser().then(setUser).catch(() => {
      localStorage.removeItem("token");
      setUser(null);
    });
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    setUser(null);
    setView("chat");
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  // Show login/signup if not authenticated
  if (!user) {
    if (authView === "signup") {
      return (
        <Signup
          onSignup={(token) => {
            handleLogin(token);
            setAuthView("login");
          }}
          onSwitchToLogin={() => setAuthView("login")}
        />
      );
    }
    return (
      <Login
        onLogin={handleLogin}
        onSwitchToSignup={() => setAuthView("signup")}
      />
    );
  }

  const isAdminOrAgent = user.role === "admin" || user.role === "agent";

  return (
    <div className="app-container">
      <nav className="app-nav">
        <div className="nav-brand">
          <h2>🤖 AI Customer Support</h2>
          <span className="nav-user">{user.username} ({user.role})</span>
        </div>
        <div className="nav-links">
          <button
            className={`nav-link ${view === "chat" ? "active" : ""}`}
            onClick={() => setView("chat")}
          >
            💬 Chat
          </button>
          {isAdminOrAgent && (
            <>
              <button
                className={`nav-link ${view === "hitl" ? "active" : ""}`}
                onClick={() => setView("hitl")}
              >
                👥 HITL Dashboard
              </button>
              <button
                className={`nav-link ${view === "monitoring" ? "active" : ""}`}
                onClick={() => setView("monitoring")}
              >
                📊 Monitoring
              </button>
            </>
          )}
          <button className="nav-link logout" onClick={handleLogout}>
            🚪 Logout
          </button>
        </div>
      </nav>

      <main className="app-main">
        {view === "chat" && <Chat />}
        {view === "hitl" && isAdminOrAgent && <HITL />}
        {view === "monitoring" && isAdminOrAgent && <MonitoringDashboard />}
      </main>
    </div>
  );
}

export default App;
