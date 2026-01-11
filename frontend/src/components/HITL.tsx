import { useState, useEffect } from "react";
import axios from "axios";
import type { Escalation, EscalationResponse } from "../api";
import "./HITL.css";

const API_URL = "http://127.0.0.1:8000/api";

function getAuthHeaders() {
  const token = localStorage.getItem("token");
  return {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  };
}

export default function HITL() {
  const [escalations, setEscalations] = useState<Escalation[]>([]);
  const [selectedEscalation, setSelectedEscalation] = useState<Escalation | null>(null);
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState("");
  const [notes, setNotes] = useState("");
  const [editMode, setEditMode] = useState(false);
  const [originalResponse, setOriginalResponse] = useState("");

  useEffect(() => {
    loadEscalations();
    const interval = setInterval(loadEscalations, 5000);
    return () => clearInterval(interval);
  }, []);

  const loadEscalations = async () => {
    try {
      const res = await axios.get(`${API_URL}/hitl/escalations/pending`, {
        headers: getAuthHeaders(),
      });
      setEscalations(res.data.escalations || []);
    } catch (error) {
      console.error("Failed to load escalations:", error);
    }
  };

  const handleSelect = async (escalation: Escalation) => {
    setSelectedEscalation(escalation);
    setResponse("");
    setNotes("");
    setEditMode(false);
    
    // Try to get full escalation details
    try {
      const res = await axios.get(`${API_URL}/hitl/escalations/${escalation._id}`, {
        headers: getAuthHeaders(),
      });
      if (res.data.original_response) {
        setOriginalResponse(res.data.original_response);
        setResponse(res.data.original_response);
      }
    } catch (error) {
      console.error("Failed to load escalation details:", error);
    }
  };

  const handleApprove = async () => {
    if (!selectedEscalation || !response.trim()) {
      alert("Please provide a response");
      return;
    }

    setLoading(true);
    try {
      await axios.post(
        `${API_URL}/hitl/escalations/${selectedEscalation._id}/approve`,
        { response: response.trim(), notes: notes.trim() || undefined },
        { headers: getAuthHeaders() }
      );
      alert("Escalation approved!");
      setSelectedEscalation(null);
      setResponse("");
      setNotes("");
      loadEscalations();
    } catch (error: any) {
      alert(error.response?.data?.detail || "Failed to approve escalation");
    } finally {
      setLoading(false);
    }
  };

  const handleReject = async () => {
    if (!selectedEscalation || !response.trim()) {
      alert("Please provide an alternative response");
      return;
    }

    setLoading(true);
    try {
      await axios.post(
        `${API_URL}/hitl/escalations/${selectedEscalation._id}/reject`,
        { response: response.trim(), notes: notes.trim() || undefined },
        { headers: getAuthHeaders() }
      );
      alert("Escalation rejected with new response!");
      setSelectedEscalation(null);
      setResponse("");
      setNotes("");
      loadEscalations();
    } catch (error: any) {
      alert(error.response?.data?.detail || "Failed to reject escalation");
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = async () => {
    if (!selectedEscalation || !response.trim() || !originalResponse) {
      alert("Please provide an edited response");
      return;
    }

    setLoading(true);
    try {
      await axios.post(
        `${API_URL}/hitl/escalations/${selectedEscalation._id}/edit`,
        {
          original_response: originalResponse,
          edited_response: response.trim(),
          reason: notes.trim() || "Human edited response",
        },
        { headers: getAuthHeaders() }
      );
      alert("Response edited successfully!");
      setSelectedEscalation(null);
      setResponse("");
      setNotes("");
      setEditMode(false);
      loadEscalations();
    } catch (error: any) {
      alert(error.response?.data?.detail || "Failed to edit response");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="hitl-container">
      <div className="hitl-header">
        <h2>🤖 Human-in-the-Loop Dashboard</h2>
        <div className="hitl-stats">
          <span className="stat-badge pending">{escalations.length} Pending</span>
        </div>
      </div>

      <div className="hitl-content">
        <div className="hitl-sidebar">
          <h3>Pending Escalations</h3>
          {escalations.length === 0 ? (
            <div className="empty-state">
              <p>No pending escalations</p>
            </div>
          ) : (
            <div className="escalation-list">
              {escalations.map((esc) => (
                <div
                  key={esc._id}
                  className={`escalation-item ${
                    selectedEscalation?._id === esc._id ? "selected" : ""
                  }`}
                  onClick={() => handleSelect(esc)}
                >
                  <div className="escalation-header">
                    <span className="user-id">{esc.user_id}</span>
                    <span className="agent-type">{esc.agent_type}</span>
                  </div>
                  <div className="escalation-reason">{esc.reason}</div>
                  <div className="escalation-time">
                    {new Date(esc.created_at).toLocaleString()}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="hitl-main">
          {selectedEscalation ? (
            <div className="escalation-detail">
              <div className="detail-header">
                <h3>Review Escalation</h3>
                <button
                  className="close-btn"
                  onClick={() => setSelectedEscalation(null)}
                >
                  ×
                </button>
              </div>

              <div className="detail-content">
                <div className="info-section">
                  <div className="info-row">
                    <label>User ID:</label>
                    <span>{selectedEscalation.user_id}</span>
                  </div>
                  <div className="info-row">
                    <label>Agent Type:</label>
                    <span>{selectedEscalation.agent_type}</span>
                  </div>
                  <div className="info-row">
                    <label>Reason:</label>
                    <span>{selectedEscalation.reason}</span>
                  </div>
                  <div className="info-row">
                    <label>Created:</label>
                    <span>
                      {new Date(selectedEscalation.created_at).toLocaleString()}
                    </span>
                  </div>
                </div>

                <div className="response-section">
                  <label>Response to User:</label>
                  <textarea
                    value={response}
                    onChange={(e) => setResponse(e.target.value)}
                    placeholder="Enter response to send to user..."
                    rows={6}
                    className="response-textarea"
                  />
                </div>

                <div className="notes-section">
                  <label>Notes (optional):</label>
                  <textarea
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    placeholder="Add notes about this review..."
                    rows={3}
                    className="notes-textarea"
                  />
                </div>

                <div className="action-buttons">
                  <button
                    className="btn-approve"
                    onClick={handleApprove}
                    disabled={loading || !response.trim()}
                  >
                    ✓ Approve
                  </button>
                  <button
                    className="btn-reject"
                    onClick={handleReject}
                    disabled={loading || !response.trim()}
                  >
                    ✗ Reject & Replace
                  </button>
                  {originalResponse && (
                    <button
                      className="btn-edit"
                      onClick={() => {
                        setEditMode(true);
                        handleEdit();
                      }}
                      disabled={loading || !response.trim() || response === originalResponse}
                    >
                      ✎ Edit Response
                    </button>
                  )}
                </div>
              </div>
            </div>
          ) : (
            <div className="empty-detail">
              <p>Select an escalation from the list to review</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
