import axios from "axios";

export const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000",
  timeout: 8000,
});

export const authHeaders = (token: string | null) =>
  token
    ? {
        Authorization: `Bearer ${token}`,
      }
    : {};
