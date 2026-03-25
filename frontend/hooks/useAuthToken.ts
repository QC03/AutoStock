"use client";

import { useEffect, useState } from "react";

const KEY = "autostock_token";

export function useAuthToken() {
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    const stored = window.localStorage.getItem(KEY);
    if (stored) {
      setToken(stored);
    }
  }, []);

  const saveToken = (value: string) => {
    window.localStorage.setItem(KEY, value);
    setToken(value);
  };

  const clearToken = () => {
    window.localStorage.removeItem(KEY);
    setToken(null);
  };

  return { token, saveToken, clearToken };
}
