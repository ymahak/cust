import axios from "axios";

const API_URL = "http://localhost:8000/api";

// Create axios instance with default config
const api = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add auth token to requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export interface ChatResponse {
  response: string;
  intent: string;
  agent_type: string;
  escalated: boolean;
  timestamp: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface User {
  username: string;
  role: string;
}

export interface SignupRequest {
  username: string;
  password: string;
  role?: string;
}

export interface SignupResponse {
  message: string;
  username: string;
  role: string;
}

// Auth API
export const signup = async (username: string, password: string, role: string = "user"): Promise<SignupResponse> => {
  try {
    const res = await api.post("/auth/signup", { username, password, role });
    return res.data;
  } catch (error: any) {
    console.error("Signup error:", error);
    if (error.response) {
      throw new Error(error.response.data?.detail || "Signup failed");
    }
    throw error;
  }
};

export const login = async (username: string, password: string): Promise<LoginResponse> => {
  try {
    const res = await api.post("/auth/login", { username, password });
    return res.data;
  } catch (error: any) {
    console.error("Login error:", error);
    if (error.response) {
      throw new Error(error.response.data?.detail || "Login failed");
    }
    throw error;
  }
};

export const getCurrentUser = async (): Promise<User> => {
  const res = await api.get("/auth/me");
  return res.data;
};

// Chat API
export const sendMessage = async (message: string): Promise<ChatResponse> => {
  const res = await api.post("/chat", { message });
  return res.data;
};

// Health check
export const healthCheck = async (): Promise<{ status: string }> => {
  const res = await axios.get(`${API_URL}/health`);
  return res.data;
};

// HITL Types
export interface Escalation {
  _id: string;
  user_id: string;
  reason: string;
  agent_type: string;
  status: string;
  created_at: string;
  human_response?: string;
  reviewed_by?: string;
  reviewed_at?: string;
}

export interface EscalationResponse {
  response: string;
  notes?: string;
}

// HITL API
export const getPendingEscalations = async (): Promise<{ escalations: Escalation[]; count: number }> => {
  const token = localStorage.getItem("token");
  const res = await api.get("/hitl/escalations/pending", {
    headers: { Authorization: `Bearer ${token}` },
  });
  return res.data;
};

export const getEscalation = async (id: string): Promise<Escalation> => {
  const token = localStorage.getItem("token");
  const res = await api.get(`/hitl/escalations/${id}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return res.data;
};

export const approveEscalation = async (id: string, response: EscalationResponse): Promise<void> => {
  const token = localStorage.getItem("token");
  await api.post(`/hitl/escalations/${id}/approve`, response, {
    headers: { Authorization: `Bearer ${token}` },
  });
};

export const rejectEscalation = async (id: string, response: EscalationResponse): Promise<void> => {
  const token = localStorage.getItem("token");
  await api.post(`/hitl/escalations/${id}/reject`, response, {
    headers: { Authorization: `Bearer ${token}` },
  });
};

export const editEscalation = async (
  id: string,
  original: string,
  edited: string,
  reason: string
): Promise<void> => {
  const token = localStorage.getItem("token");
  await api.post(
    `/hitl/escalations/${id}/edit`,
    { original_response: original, edited_response: edited, reason },
    {
      headers: { Authorization: `Bearer ${token}` },
    }
  );
};

// Monitoring API
export const getMetrics = async (): Promise<any> => {
  const token = localStorage.getItem("token");
  const res = await api.get("/monitoring/metrics", {
    headers: { Authorization: `Bearer ${token}` },
  });
  return res.data;
};

export const getDashboard = async (): Promise<any> => {
  const token = localStorage.getItem("token");
  const res = await api.get("/monitoring/dashboard", {
    headers: { Authorization: `Bearer ${token}` },
  });
  return res.data;
};
