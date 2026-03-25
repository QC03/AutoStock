"use client";

import { useState } from "react";

import { authApi } from "@/lib/api/endpoints";
import { useAuthToken } from "@/hooks/useAuthToken";

export default function LoginPage() {
  const { saveToken } = useAuthToken();
  const [username, setUsername] = useState("tester");
  const [password, setPassword] = useState("pass1234");
  const [message, setMessage] = useState("");

  const onSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setMessage("로그인 중...");
    try {
      const result = await authApi.login({ username, password });
      saveToken(result.access_token);
      setMessage("로그인 성공: 토큰이 저장되었습니다.");
    } catch (error) {
      setMessage("로그인 실패: 계정을 먼저 생성하세요.");
    }
  };

  return (
    <section className="mx-auto max-w-md card">
      <h2 className="mb-4 text-xl font-semibold">로그인</h2>
      <form className="space-y-3" onSubmit={onSubmit}>
        <input className="input" value={username} onChange={(event) => setUsername(event.target.value)} placeholder="아이디" />
        <input
          className="input"
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          placeholder="비밀번호"
        />
        <button className="button w-full" type="submit">
          로그인
        </button>
      </form>
      <p className="mt-3 text-sm text-slate-600">{message}</p>
    </section>
  );
}
