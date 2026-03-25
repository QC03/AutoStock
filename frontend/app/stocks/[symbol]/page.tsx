"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useMutation, useQuery } from "@tanstack/react-query";

import RealtimePriceChart from "@/components/RealtimePriceChart";
import { dataApi, tradingApi } from "@/lib/api/endpoints";
import { useAuthToken } from "@/hooks/useAuthToken";

const SELECTED_SYMBOLS_KEY = "autostock:stocks:selected-symbols";
const QUICK_SYMBOLS = ["AAPL", "MSFT", "TSLA", "NVDA", "AMZN", "GOOGL"] as const;

const normalizeSymbol = (value: string) => value.trim().toUpperCase().replace(/[^A-Z0-9.-]/g, "");

const signalFromRsi = (rsi?: number) => {
  if (rsi === undefined) return "HOLD";
  if (rsi < 30) return "BUY";
  if (rsi > 70) return "SELL";
  return "HOLD";
};

type StockAccordionBlockProps = {
  symbol: string;
  expanded: boolean;
  onToggle: (symbol: string) => void;
  onRemove: (symbol: string) => void;
  isRemovable: boolean;
};

function StockAccordionBlock({ symbol, expanded, onToggle, onRemove, isRemovable }: StockAccordionBlockProps) {
  const quoteQuery = useQuery({
    queryKey: ["quote", symbol],
    queryFn: () => dataApi.quote(symbol),
  });

  const indicatorQuery = useQuery({
    queryKey: ["indicators", symbol],
    queryFn: () => dataApi.indicators(symbol),
  });

  const signal = signalFromRsi(indicatorQuery.data?.rsi_14);

  return (
    <article className="rounded-xl border border-slate-200 bg-white shadow-sm">
      <div className="flex items-center justify-between gap-3 px-4 py-3">
        <button
          type="button"
          className="flex flex-1 items-center justify-between text-left"
          onClick={() => onToggle(symbol)}
        >
          <div>
            <p className="text-base font-semibold text-slate-900">{symbol}</p>
            <p className="text-xs text-slate-500">
              현재가: {quoteQuery.isLoading ? "로딩 중..." : `$${quoteQuery.data?.price.toFixed(2) ?? "-"}`}
            </p>
          </div>
          <span className="text-sm text-slate-500">{expanded ? "▲" : "▼"}</span>
        </button>

        {isRemovable && (
          <button
            type="button"
            className="rounded-md border border-slate-200 px-2 py-1 text-xs text-slate-500 hover:border-slate-300 hover:text-slate-700"
            onClick={() => onRemove(symbol)}
          >
            제거
          </button>
        )}
      </div>

      {expanded && (
        <div className="space-y-3 border-t border-slate-100 px-4 py-4">
          <div className="grid gap-2 text-sm text-slate-700 md:grid-cols-3">
            <p>RSI: {indicatorQuery.data?.rsi_14?.toFixed(2) ?? "-"}</p>
            <p>MACD: {indicatorQuery.data?.macd?.toFixed(4) ?? "-"}</p>
            <p>신호: {signal}</p>
          </div>
          <RealtimePriceChart symbol={symbol} />
        </div>
      )}
    </article>
  );
}

export default function StockDetailPage() {
  const { token } = useAuthToken();
  const params = useParams<{ symbol: string }>();
  const routeSymbol = normalizeSymbol(params.symbol ?? "AAPL") || "AAPL";
  const [symbols, setSymbols] = useState<string[]>([routeSymbol]);
  const [expandedSymbol, setExpandedSymbol] = useState<string>(routeSymbol);
  const [isSymbolsHydrated, setIsSymbolsHydrated] = useState(false);
  const [newSymbol, setNewSymbol] = useState("");
  const [quantity, setQuantity] = useState(1);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const activeSymbol = expandedSymbol || symbols[0] || routeSymbol;

  useEffect(() => {
    const raw = window.sessionStorage.getItem(SELECTED_SYMBOLS_KEY);
    if (!raw) {
      setSymbols([routeSymbol]);
      setExpandedSymbol(routeSymbol);
      setIsSymbolsHydrated(true);
      return;
    }
    try {
      const parsed = JSON.parse(raw) as string[];
      const normalized = parsed.map((item) => normalizeSymbol(item)).filter((item) => item.length > 0);
      const unique = Array.from(new Set([routeSymbol, ...normalized]));
      setSymbols(unique);
      setExpandedSymbol(unique[0]);
    } catch {
      setSymbols([routeSymbol]);
      setExpandedSymbol(routeSymbol);
      window.sessionStorage.removeItem(SELECTED_SYMBOLS_KEY);
    } finally {
      setIsSymbolsHydrated(true);
    }
  }, [routeSymbol]);

  useEffect(() => {
    if (!isSymbolsHydrated) return;
    if (symbols.length === 0) return;
    window.sessionStorage.setItem(SELECTED_SYMBOLS_KEY, JSON.stringify(symbols));
  }, [symbols, isSymbolsHydrated]);

  const activeIndicatorQuery = useQuery({
    queryKey: ["indicators", activeSymbol],
    queryFn: () => dataApi.indicators(activeSymbol),
    enabled: Boolean(activeSymbol),
  });

  const activeSignal = useMemo(() => signalFromRsi(activeIndicatorQuery.data?.rsi_14), [activeIndicatorQuery.data?.rsi_14]);

  const addSymbol = (raw: string) => {
    const normalized = normalizeSymbol(raw);
    if (!normalized) {
      setError("종목 코드를 입력하세요.");
      return;
    }

    setSymbols((current) => {
      if (current.includes(normalized)) return current;
      return [normalized, ...current];
    });

    setExpandedSymbol(normalized);
    setNewSymbol("");
    setError("");
    setSuccess("");
  };

  const removeSymbol = (target: string) => {
    setSymbols((current) => {
      if (current.length <= 1) return current;
      const next = current.filter((item) => item !== target);
      if (expandedSymbol === target) {
        setExpandedSymbol(next[0] ?? routeSymbol);
      }
      return next;
    });
  };

  const toggleSymbolBlock = (target: string) => {
    setExpandedSymbol((current) => (current === target ? "" : target));
  };

  const buyMutation = useMutation({
    mutationFn: () =>
      tradingApi.placeOrder(token, {
        symbol: activeSymbol,
        side: "BUY",
        quantity,
        order_type: "MARKET",
      }),
    onSuccess: (result) => {
      setSuccess(`매수 성공: ${result.status} @ $${result.price.toFixed(2)}`);
      setError("");
      setTimeout(() => setSuccess(""), 3000);
    },
    onError: () => {
      setError("매수 실패: 로그인 또는 주문 파라미터를 확인하세요.");
      setSuccess("");
    },
  });

  const sellMutation = useMutation({
    mutationFn: () =>
      tradingApi.placeOrder(token, {
        symbol: activeSymbol,
        side: "SELL",
        quantity,
        order_type: "MARKET",
      }),
    onSuccess: (result) => {
      setSuccess(`매도 성공: ${result.status} @ $${result.price.toFixed(2)}`);
      setError("");
      setTimeout(() => setSuccess(""), 3000);
    },
    onError: () => {
      setError("매도 실패: 로그인 또는 보유수량을 확인하세요.");
      setSuccess("");
    },
  });

  if (!token) {
    return (
      <section className="card text-center">
        <p className="text-slate-600">거래를 시작하려면 로그인하세요.</p>
        <Link href="/login" className="mt-3 inline-block font-medium text-brand-600 hover:text-brand-700">
          로그인하기
        </Link>
      </section>
    );
  }

  return (
    <section className="space-y-4">
      <div className="card space-y-3">
        <h2 className="text-xl font-semibold">종목 상세</h2>
        <p className="text-sm text-slate-600">원하는 종목을 추가하면 블록으로 쌓이고, 블록을 눌러 차트를 펼칠 수 있습니다.</p>

        <div className="flex flex-wrap gap-2">
          {QUICK_SYMBOLS.map((item) => (
            <button
              key={item}
              type="button"
              className="rounded-md border border-slate-300 px-3 py-1.5 text-xs font-medium text-slate-700 hover:border-slate-400"
              onClick={() => addSymbol(item)}
            >
              + {item}
            </button>
          ))}
        </div>

        <div className="flex flex-wrap gap-2">
          <input
            className="input w-44"
            placeholder="예: AAPL"
            value={newSymbol}
            onChange={(event) => setNewSymbol(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter") {
                event.preventDefault();
                addSymbol(newSymbol);
              }
            }}
          />
          <button className="button" type="button" onClick={() => addSymbol(newSymbol)}>
            종목 추가
          </button>
        </div>
      </div>

      <div className="space-y-3">
        {symbols.map((item) => (
          <StockAccordionBlock
            key={item}
            symbol={item}
            expanded={expandedSymbol === item}
            onToggle={toggleSymbolBlock}
            onRemove={removeSymbol}
            isRemovable={symbols.length > 1}
          />
        ))}
      </div>

      <div className="card space-y-4">
        <h3 className="text-lg font-semibold">주문 ({activeSymbol})</h3>
        <p className="text-sm text-slate-600">현재 신호: {activeSignal}</p>
        <div className="flex flex-wrap items-end gap-3">
          <div>
            <label htmlFor="quantity" className="mb-1 block text-sm">수량</label>
            <input
              id="quantity"
              className="input w-32"
              type="number"
              min={1}
              value={quantity}
              onChange={(event) => setQuantity(Math.max(1, Number(event.target.value)))}
            />
          </div>
          <div className="flex gap-2">
            <button
              className="button"
              onClick={() => buyMutation.mutate()}
              disabled={buyMutation.isPending || !token}
            >
              {buyMutation.isPending ? "처리 중..." : "매수"}
            </button>
            <button
              className="button bg-slate-700 hover:bg-slate-800"
              onClick={() => sellMutation.mutate()}
              disabled={sellMutation.isPending || !token}
            >
              {sellMutation.isPending ? "처리 중..." : "매도"}
            </button>
          </div>
        </div>

        {error && <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</div>}
        {success && <div className="rounded-md bg-green-50 p-3 text-sm text-green-700">{success}</div>}
      </div>
    </section>
  );
}