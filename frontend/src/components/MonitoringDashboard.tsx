import { useState, useEffect } from "react";
import { getDashboard, getMetrics } from "../api";
import "./MonitoringDashboard.css";

export default function MonitoringDashboard() {
  const [dashboardData, setDashboardData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboard();
    const interval = setInterval(loadDashboard, 10000); // Refresh every 10 seconds
    return () => clearInterval(interval);
  }, []);

  const loadDashboard = async () => {
    try {
      setLoading(true);
      const data = await getDashboard();
      setDashboardData(data);
      setError(null);
    } catch (err: any) {
      setError(err.message || "Failed to load dashboard");
      console.error("Dashboard error:", err);
    } finally {
      setLoading(false);
    }
  };

  if (loading && !dashboardData) {
    return (
      <div className="dashboard-container">
        <div className="dashboard-loading">Loading dashboard...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-container">
        <div className="dashboard-error">Error: {error}</div>
      </div>
    );
  }

  const agentPerf = dashboardData?.agent_performance || {};
  const intentDist = dashboardData?.intent_distribution || {};
  const escalationStats = dashboardData?.escalation_stats || {};

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h2>📊 System Monitoring Dashboard</h2>
        <button onClick={loadDashboard} className="refresh-btn">
          🔄 Refresh
        </button>
      </div>

      <div className="dashboard-grid">
        {/* Overview Cards */}
        <div className="dashboard-card">
          <h3>Total Calls</h3>
          <div className="metric-value">{dashboardData?.total_calls || 0}</div>
        </div>

        <div className="dashboard-card">
          <h3>Total Escalations</h3>
          <div className="metric-value">{dashboardData?.total_escalations || 0}</div>
        </div>

        <div className="dashboard-card">
          <h3>Pending Escalations</h3>
          <div className="metric-value">{escalationStats.pending || 0}</div>
        </div>

        <div className="dashboard-card">
          <h3>Resolved Escalations</h3>
          <div className="metric-value">{escalationStats.resolved || 0}</div>
        </div>

        {/* Agent Performance */}
        <div className="dashboard-card large">
          <h3>Agent Performance</h3>
          <div className="agent-stats">
            {Object.entries(agentPerf).map(([agent, stats]: [string, any]) => (
              <div key={agent} className="agent-stat-item">
                <div className="agent-name">{agent}</div>
                <div className="agent-metrics">
                  <div className="metric">
                    <span className="metric-label">Calls:</span>
                    <span className="metric-value-small">{stats.total_calls || 0}</span>
                  </div>
                  <div className="metric">
                    <span className="metric-label">Avg Latency:</span>
                    <span className="metric-value-small">
                      {stats.avg_latency_ms ? `${stats.avg_latency_ms.toFixed(0)}ms` : "N/A"}
                    </span>
                  </div>
                  <div className="metric">
                    <span className="metric-label">Escalation Rate:</span>
                    <span className="metric-value-small">
                      {stats.escalation_rate
                        ? `${(stats.escalation_rate * 100).toFixed(1)}%`
                        : "0%"}
                    </span>
                  </div>
                </div>
              </div>
            ))}
            {Object.keys(agentPerf).length === 0 && (
              <div className="empty-state">No agent data available</div>
            )}
          </div>
        </div>

        {/* Intent Distribution */}
        <div className="dashboard-card large">
          <h3>Intent Distribution</h3>
          <div className="intent-stats">
            {Object.entries(intentDist).map(([intent, count]: [string, any]) => (
              <div key={intent} className="intent-item">
                <div className="intent-label">{intent}</div>
                <div className="intent-bar">
                  <div
                    className="intent-fill"
                    style={{
                      width: `${(count / (dashboardData?.total_calls || 1)) * 100}%`,
                    }}
                  />
                </div>
                <div className="intent-count">{count}</div>
              </div>
            ))}
            {Object.keys(intentDist).length === 0 && (
              <div className="empty-state">No intent data available</div>
            )}
          </div>
        </div>

        {/* Trace Summary */}
        {dashboardData?.trace_summary && (
          <div className="dashboard-card">
            <h3>Trace Summary</h3>
            <div className="trace-stats">
              <div className="trace-stat">
                <span>Total Traces:</span>
                <span>{dashboardData.trace_summary.total_traces || 0}</span>
              </div>
              <div className="trace-stat">
                <span>Completed:</span>
                <span>{dashboardData.trace_summary.completed || 0}</span>
              </div>
              <div className="trace-stat">
                <span>In Progress:</span>
                <span>{dashboardData.trace_summary.in_progress || 0}</span>
              </div>
              <div className="trace-stat">
                <span>Success Rate:</span>
                <span>
                  {dashboardData.trace_summary.success_rate
                    ? `${dashboardData.trace_summary.success_rate.toFixed(1)}%`
                    : "N/A"}
                </span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
