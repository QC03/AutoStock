"use client";

import { useEffect, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";

import { AutoTradeConfigPayload, tradingApi } from "@/lib/api/endpoints";
import { useAuthToken } from "@/hooks/useAuthToken";

const FORM_STORAGE_KEY = "autostock:auto-trade:form";
const UNIVERSE = ["AAPL", "MSFT", "TSLA", "NVDA"] as const;

const defaultForm: AutoTradeConfigPayload = {
  strategy: "rsi_macd",
  symbols: ["AAPL", "MSFT"],
  quantity: 1,
  interval_seconds: 10,
  max_loss_pct: 5,
};

const clamp = (value: number, min: number, max: number) => Math.min(max, Math.max(min, value));

const sanitizeConfig = (
  input?: Partial<AutoTradeConfigPayload> | null
): AutoTradeConfigPayload => {
  const strategy =
    input?.strategy === "momentum" || input?.strategy === "mean_reversion" || input?.strategy === "rsi_macd"
      ? input.strategy
      : defaultForm.strategy;

  const parsedSymbols = Array.isArray(input?.symbols)
    ? input.symbols
        .map((value) => String(value).trim().toUpperCase())
        .filter((value) => UNIVERSE.includes(value as (typeof UNIVERSE)[number]))
    : [];
  const symbols = parsedSymbols.length > 0 ? Array.from(new Set(parsedSymbols)) : defaultForm.symbols;

  const quantityRaw = Number(input?.quantity);
  const quantity = Number.isFinite(quantityRaw) ? clamp(Math.round(quantityRaw), 1, 100) : defaultForm.quantity;

  const intervalRaw = Number(input?.interval_seconds);
  const interval_seconds = Number.isFinite(intervalRaw)
    ? clamp(Math.round(intervalRaw), 3, 300)
    : defaultForm.interval_seconds;

  const maxLossRaw = Number(input?.max_loss_pct);
  const max_loss_pct = Number.isFinite(maxLossRaw)
    ? clamp(Number(maxLossRaw.toFixed(2)), 1, 30)
    : defaultForm.max_loss_pct;

  return {
    strategy,
    symbols,
    quantity,
    interval_seconds,
    max_loss_pct,
  };
};

export default function TradingSettingsPage() {
  const { token } = useAuthToken();
  const isAuthenticated = Boolean(token);
  const queryClient = useQueryClient();
  const [form, setForm] = useState<AutoTradeConfigPayload>(defaultForm);
  const [isFormHydrated, setIsFormHydrated] = useState(false);
  const [message, setMessage] = useState("");

  const statusQueryKey = useMemo(() => ["auto-trade-status", token], [token]);

  const configQuery = useQuery({
    queryKey: ["auto-trade-config", token],
    queryFn: () => tradingApi.getAutoTradeConfig(token),
    enabled: Boolean(token),
  });

  const activityQuery = useQuery({
    queryKey: ["auto-trade-activity", token],
    queryFn: () => tradingApi.getAutoTradeActivity(token),
    enabled: Boolean(token),
    refetchInterval: 3000,
  });

  const statusQuery = useQuery({
    queryKey: statusQueryKey,
    queryFn: () => tradingApi.getAutoTradeStatus(token),
    enabled: Boolean(token),
  });

  useEffect(() => {
    const raw = window.localStorage.getItem(FORM_STORAGE_KEY);
    if (!raw) {
      setIsFormHydrated(true);
      return;
    }
    try {
      const parsed = JSON.parse(raw) as Partial<AutoTradeConfigPayload>;
      setForm(sanitizeConfig(parsed));
    } catch {
      window.localStorage.removeItem(FORM_STORAGE_KEY);
    } finally {
      setIsFormHydrated(true);
    }
  }, []);

  useEffect(() => {
    if (!isFormHydrated) return;
    if (!configQuery.data) return;
    const hasLocal = Boolean(window.localStorage.getItem(FORM_STORAGE_KEY));
    if (!hasLocal) {
      setForm(sanitizeConfig(configQuery.data));
    }
  }, [configQuery.data, isFormHydrated]);

  useEffect(() => {
    if (!isFormHydrated) return;
    window.localStorage.setItem(FORM_STORAGE_KEY, JSON.stringify(form));
  }, [form, isFormHydrated]);

  const toggleMutation = useMutation({
    mutationFn: async (enabled: boolean) => {
      if (!token) {
        throw new Error("로그인 상태를 확인하세요.");
      }
      const safePayload = sanitizeConfig(form);
      setForm(safePayload);
      if (enabled) {
        await tradingApi.setAutoTradeConfig(token, safePayload);
      }
      return tradingApi.toggleAutoTrade(token, enabled);
    },
    onSuccess: (data) => {
      queryClient.setQueryData(statusQueryKey, { enabled: data.enabled });
      queryClient.invalidateQueries({ queryKey: statusQueryKey });
      queryClient.invalidateQueries({ queryKey: ["auto-trade-config", token] });
      queryClient.invalidateQueries({ queryKey: ["auto-trade-activity", token] });
      statusQuery.refetch();
      setMessage(`자동매매 상태: ${data.enabled ? "ON" : "OFF"}`);
    },
    onError: (error) => setMessage(`자동매매 설정 실패: ${error.message}`),
  });

  const toggleSymbol = (symbol: string) => {
    setForm((current) => {
      const exists = current.symbols.includes(symbol);
      if (exists) {
        const next = current.symbols.filter((item) => item !== symbol);
        return { ...current, symbols: next.length > 0 ? next : [symbol] };
      }
      return { ...current, symbols: [...current.symbols, symbol] };
    });
  };

  const saveConfigMutation = useMutation({
    mutationFn: () => {
      if (!token) {
        throw new Error("로그인 상태를 확인하세요.");
      }
      const safePayload = sanitizeConfig(form);
      setForm(safePayload);
      return tradingApi.setAutoTradeConfig(token, safePayload);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["auto-trade-config", token] });
      queryClient.invalidateQueries({ queryKey: ["auto-trade-activity", token] });
      setMessage("자동매매 설정 저장 완료");
    },
    onError: (error) => setMessage(`설정 저장 실패: ${error.message}`),
  });

  if (!isAuthenticated) {
    return (
      <section className="card max-w-2xl space-y-3">
        <h2 className="text-lg font-semibold">매매 설정</h2>
        <p className="text-sm text-slate-600">자동매매 설정을 사용하려면 로그인하세요.</p>
        <Link href="/login" className="text-sm font-medium text-brand-600 hover:text-brand-700">
          로그인하기
        </Link>
      </section>
    );
  }

  return (
    <section className="card max-w-2xl space-y-4">
      <h2 className="text-lg font-semibold">매매 설정</h2>

      <div className="rounded-md border border-slate-200 p-3 text-sm">
        현재 자동매매 상태: {statusQuery.isLoading ? "확인 중..." : statusQuery.data?.enabled ? "ON" : "OFF"}
      </div>

      <div className="rounded-md border border-slate-200 p-3 text-sm space-y-1">
        <p className="font-medium">AI 현재 작업</p>
        <p>실행 중: {activityQuery.data?.running ? "예" : "아니오"}</p>
        <p>
          다음 실행: {activityQuery.data?.next_run_in_seconds === undefined || activityQuery.data?.next_run_in_seconds === null
            ? "-"
            : `${activityQuery.data.next_run_in_seconds}초 후`}
        </p>
        <p>최근 실행: {activityQuery.data?.last_run_at ? new Date(activityQuery.data.last_run_at).toLocaleString() : "-"}</p>
        <p>최근 액션: {activityQuery.data?.last_action ?? "-"}</p>
        <p>최근 종목/신호: {activityQuery.data?.last_symbol ?? "-"} / {activityQuery.data?.last_signal ?? "-"}</p>
        <p>최근 메시지: {activityQuery.data?.last_message ?? "-"}</p>
      </div>

      <div>
        <label className="mb-1 block text-sm">전략</label>
        <select
          className="input"
          value={form.strategy}
          onChange={(event) => setForm((current) => ({ ...current, strategy: event.target.value as AutoTradeConfigPayload["strategy"] }))}
        >
          <option value="rsi_macd">RSI + MACD</option>
          <option value="momentum">Momentum</option>
          <option value="mean_reversion">Mean Reversion</option>
        </select>
      </div>

      <div>
        <label className="mb-1 block text-sm">대상 종목</label>
        <div className="flex flex-wrap gap-2">
          {UNIVERSE.map((symbol) => {
            const selected = form.symbols.includes(symbol);
            return (
              <button
                key={symbol}
                type="button"
                className={selected ? "button" : "rounded-md border border-slate-300 px-3 py-2 text-sm"}
                onClick={() => toggleSymbol(symbol)}
              >
                {symbol}
              </button>
            );
          })}
        </div>
      </div>

      <div className="grid gap-3 md:grid-cols-2">
        <div>
          <label className="mb-1 block text-sm">주문 수량</label>
          <input
            className="input"
            type="number"
            min={1}
            max={100}
            value={form.quantity}
            onChange={(event) =>
              setForm((current) => {
                const parsed = Number(event.target.value);
                if (!Number.isFinite(parsed)) {
                  return current;
                }
                return { ...current, quantity: clamp(Math.round(parsed), 1, 100) };
              })
            }
          />
        </div>
        <div>
          <label className="mb-1 block text-sm">실행 주기(초)</label>
          <input
            className="input"
            type="number"
            min={3}
            max={300}
            value={form.interval_seconds}
            onChange={(event) =>
              setForm((current) => {
                const parsed = Number(event.target.value);
                if (!Number.isFinite(parsed)) {
                  return current;
                }
                return { ...current, interval_seconds: clamp(Math.round(parsed), 3, 300) };
              })
            }
          />
        </div>
      </div>

      <div>
        <label className="mb-1 block text-sm">최대 손실 한도(%)</label>
        <input
          className="input"
          type="number"
          min={1}
          max={30}
          value={form.max_loss_pct}
          onChange={(event) =>
            setForm((current) => {
              const parsed = Number(event.target.value);
              if (!Number.isFinite(parsed)) {
                return current;
              }
              return { ...current, max_loss_pct: clamp(Number(parsed.toFixed(2)), 1, 30) };
            })
          }
        />
      </div>

      <div className="flex gap-2">
        <button className="button bg-slate-700 hover:bg-slate-800" onClick={() => saveConfigMutation.mutate()} disabled={saveConfigMutation.isPending}>
          설정 저장
        </button>
        <button className="button" onClick={() => toggleMutation.mutate(true)} disabled={toggleMutation.isPending || saveConfigMutation.isPending}>
          자동매매 ON
        </button>
        <button className="button bg-slate-700 hover:bg-slate-800" onClick={() => toggleMutation.mutate(false)} disabled={toggleMutation.isPending || saveConfigMutation.isPending}>
          자동매매 OFF
        </button>
      </div>

      <p className="text-sm text-slate-600">
        전략: {form.strategy}, 종목: {form.symbols.join(", ")}, 수량: {form.quantity}, 주기: {form.interval_seconds}초, 최대 손실: {form.max_loss_pct}%
      </p>
      <p className="text-sm text-slate-600">{message}</p>
    </section>
  );
}
