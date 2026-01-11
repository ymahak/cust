import { useState } from "react";
import { signup } from "../api";
import "./Signup.css";

interface SignupProps {
  onSignup: (token: string) => void;
  onSwitchToLogin: () => void;
}

export default function Signup({ onSwitchToLogin }: SignupProps) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [role, setRole] = useState("user");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    // Validation
    if (username.length < 3) {
      setError("Username must be at least 3 characters");
      return;
    }

    if (password.length < 6) {
      setError("Password must be at least 6 characters");
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    setLoading(true);

    try {
      await signup(username, password, role);
      // After successful signup, automatically login
      // Note: In a real app, you might want to show a success message first
      setError("");
      // Switch to login view
      onSwitchToLogin();
    } catch (err: any) {
      setError(err.message || "Signup failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="signup-container">
      <div className="signup-box">
        <div className="signup-header">
          <h1>🤖 AI Support</h1>
          <p>Create your account to get started</p>
        </div>
        
        <form onSubmit={handleSubmit} className="signup-form">
          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Choose a username (min 3 characters)"
              required
              minLength={3}
              autoComplete="username"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Choose a password (min 6 characters)"
              required
              minLength={6}
              autoComplete="new-password"
            />
          </div>

          <div className="form-group">
            <label htmlFor="confirmPassword">Confirm Password</label>
            <input
              id="confirmPassword"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Confirm your password"
              required
              autoComplete="new-password"
            />
          </div>

          <div className="form-group">
            <label htmlFor="role">Account Type</label>
            <select
              id="role"
              value={role}
              onChange={(e) => setRole(e.target.value)}
              className="role-select"
            >
              <option value="user">User</option>
              <option value="agent">Agent</option>
              <option value="admin">Admin</option>
            </select>
            <small className="role-hint">
              Note: Admin and Agent roles have access to HITL and Monitoring dashboards
            </small>
          </div>

          {error && <div className="error-message">{error}</div>}

          <button type="submit" disabled={loading} className="signup-button">
            {loading ? "Creating account..." : "Sign Up"}
          </button>
        </form>

        <div className="signup-footer">
          <p>
            Already have an account?{" "}
            <button type="button" onClick={onSwitchToLogin} className="link-button">
              Login here
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}
