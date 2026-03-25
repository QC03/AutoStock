"use client";

import { useEffect, useState } from "react";

const KEY = "autostock_token";
const TOKEN_CHANGED_EVENT = "autostock:token-changed";

function readToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(KEY);
}

export function useAuthToken() {
  const [token, setToken] = useState<string | null>(() => readToken());

  useEffect(() => {
    const sync = () => setToken(readToken());
    sync();

    const onStorage = (event: StorageEvent) => {
      if (event.key === KEY) sync();
    };

    const onTokenChanged = () => sync();

    window.addEventListener("storage", onStorage);
    window.addEventListener(TOKEN_CHANGED_EVENT, onTokenChanged);

    return () => {
      window.removeEventListener("storage", onStorage);
      window.removeEventListener(TOKEN_CHANGED_EVENT, onTokenChanged);
    };
  }, []);

  const saveToken = (value: string) => {
    window.localStorage.setItem(KEY, value);
    setToken(value);
    window.dispatchEvent(new Event(TOKEN_CHANGED_EVENT));
  };

  const clearToken = () => {
    window.localStorage.removeItem(KEY);
    setToken(null);
    window.dispatchEvent(new Event(TOKEN_CHANGED_EVENT));
  };

  return { token, saveToken, clearToken };
}
