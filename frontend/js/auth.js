const API = window.location.origin + "/api";

export function saveSession(data) {
  localStorage.setItem("token", data.access_token);
  localStorage.setItem("user",  JSON.stringify(data.user));
}
export function getToken() { return localStorage.getItem("token"); }
export function getUser()  { return JSON.parse(localStorage.getItem("user") || "null"); }
export function logout() {
  localStorage.removeItem("token");
  localStorage.removeItem("user");
  window.location.href = "/static/index.html";
}
export function requireAuth() {
  if (!getToken()) window.location.href = "/static/index.html";
}

export async function apiFetch(path, options = {}) {
  const token   = getToken();
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const res  = await fetch(API + path, { ...options, headers });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Request failed");
  return data;
}

export const login    = (email, password)             => apiFetch("/auth/login",    { method: "POST", body: JSON.stringify({ email, password }) });
export const register = (name, email, phone, password) => apiFetch("/auth/register", { method: "POST", body: JSON.stringify({ name, email, phone, password }) });
export const fetchMe  = ()                             => apiFetch("/auth/me");
