"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { authApi } from "@/lib/api/endpoints";
import { useAuthToken } from "@/hooks/useAuthToken";

export default function LoginPage() {
  const router = useRouter();
  const { saveToken } = useAuthToken();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const onSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError("");
    setLoading(true);

    if (!username.trim() || !password.trim()) {
      setError("아이디와 비밀번호를 입력하세요.");
      setLoading(false);
      return;
    }

    try {
      const result = await authApi.login({ username, password });
      saveToken(result.access_token);
      router.push("/dashboard");
    } catch (error) {
      setError("로그인 실패: 아이디 또는 비밀번호를 확인하세요.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="mx-auto max-w-sm">
      <div className="card space-y-4">
        <h2 className="text-lg font-semibold">로그인</h2>

        <form className="space-y-3" onSubmit={onSubmit}>
          <input
            id="username"
            className="input"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="아이디"
            disabled={loading}
          />

          <input
            id="password"
            className="input"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="비밀번호"
            disabled={loading}
          />

          {error && <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</div>}

          <button className="button w-full" type="submit" disabled={loading}>
            {loading ? "로그인 중..." : "로그인"}
          </button>
        </form>

        <div className="text-center text-sm">
          계정이 없으신가요?{" "}
          <Link href="/signup" className="font-medium text-brand-600 hover:text-brand-700">
            회원가입
          </Link>
        </div>
      </div>
    </section>
  );
}
