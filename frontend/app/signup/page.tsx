"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { authApi } from "@/lib/api/endpoints";
import { useAuthToken } from "@/hooks/useAuthToken";

export default function SignupPage() {
  const router = useRouter();
  const { saveToken } = useAuthToken();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
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

    if (username.length < 3) {
      setError("아이디는 3글자 이상이어야 합니다.");
      setLoading(false);
      return;
    }

    if (password.length < 6) {
      setError("비밀번호는 6글자 이상이어야 합니다.");
      setLoading(false);
      return;
    }

    if (password !== confirmPassword) {
      setError("비밀번호가 일치하지 않습니다.");
      setLoading(false);
      return;
    }

    try {
      const result = await authApi.signup({ username, password });
      saveToken(result.access_token);
      router.push("/dashboard");
    } catch (error) {
      setError("회원가입 실패: 이미 존재하는 아이디이거나 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="mx-auto max-w-sm">
      <div className="card space-y-4">
        <h2 className="text-lg font-semibold">회원가입</h2>

        <form className="space-y-3" onSubmit={onSubmit}>
          <input
            id="username"
            className="input"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="아이디 (3글자 이상)"
            disabled={loading}
          />

          <input
            id="password"
            className="input"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="비밀번호 (6글자 이상)"
            disabled={loading}
          />

          <input
            id="confirmPassword"
            className="input"
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            placeholder="비밀번호 확인"
            disabled={loading}
          />

          {error && <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</div>}

          <button className="button w-full" type="submit" disabled={loading}>
            {loading ? "가입 중..." : "회원가입"}
          </button>
        </form>

        <div className="text-center text-sm">
          이미 계정이 있으신가요?{" "}
          <Link href="/login" className="font-medium text-brand-600 hover:text-brand-700">
            로그인
          </Link>
        </div>
      </div>
    </section>
  );
}
