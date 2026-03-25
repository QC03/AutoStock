"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";

import { tradingApi } from "@/lib/api/endpoints";
import { useAuthToken } from "@/hooks/useAuthToken";

export default function TradingSettingsPage() {
  const { token } = useAuthToken();
  const [strategy, setStrategy] = useState("rsi_macd");
  const [maxLossPct, setMaxLossPct] = useState(5);
  const [message, setMessage] = useState("");

  const toggleMutation = useMutation({
    mutationFn: (enabled: boolean) => tradingApi.toggleAutoTrade(token, enabled),
    onSuccess: (data) => setMessage(`자동매매 상태: ${data.enabled ? "ON" : "OFF"}`),
    onError: () => setMessage("자동매매 설정 실패: 로그인 상태를 확인하세요."),
  });

  return (
    <section className="card max-w-2xl space-y-4">
      <h2 className="text-lg font-semibold">매매 설정</h2>

      <div>
        <label className="mb-1 block text-sm">전략</label>
        <select className="input" value={strategy} onChange={(event) => setStrategy(event.target.value)}>
          <option value="rsi_macd">RSI + MACD</option>
          <option value="momentum">Momentum</option>
          <option value="mean_reversion">Mean Reversion</option>
        </select>
      </div>

      <div>
        <label className="mb-1 block text-sm">최대 손실 한도(%)</label>
        <input
          className="input"
          type="number"
          min={1}
          max={30}
          value={maxLossPct}
          onChange={(event) => setMaxLossPct(Number(event.target.value))}
        />
      </div>

      <div className="flex gap-2">
        <button className="button" onClick={() => toggleMutation.mutate(true)}>
          자동매매 ON
        </button>
        <button className="button bg-slate-700 hover:bg-slate-800" onClick={() => toggleMutation.mutate(false)}>
          자동매매 OFF
        </button>
      </div>

      <p className="text-sm text-slate-600">
        선택 전략: {strategy}, 최대 손실: {maxLossPct}%
      </p>
      <p className="text-sm text-slate-600">{message}</p>
    </section>
  );
}
