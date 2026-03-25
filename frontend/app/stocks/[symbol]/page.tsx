"use client";

import { useMemo, useState } from "react";
import { useParams } from "next/navigation";
import { useMutation, useQuery } from "@tanstack/react-query";

import RealtimePriceChart from "@/components/RealtimePriceChart";
import { dataApi, tradingApi } from "@/lib/api/endpoints";
import { useAuthToken } from "@/hooks/useAuthToken";

export default function StockDetailPage() {
  const { token } = useAuthToken();
  const params = useParams<{ symbol: string }>();
  const symbol = (params.symbol ?? "AAPL").toUpperCase();
  const [quantity, setQuantity] = useState(1);
  const [message, setMessage] = useState("");

  const quoteQuery = useQuery({
    queryKey: ["quote", symbol],
    queryFn: () => dataApi.quote(symbol),
  });

  const indicatorQuery = useQuery({
    queryKey: ["indicators", symbol],
    queryFn: () => dataApi.indicators(symbol),
  });

  const signal = useMemo(() => {
    const rsi = indicatorQuery.data?.rsi_14;
    if (rsi === undefined) return "HOLD";
    if (rsi < 30) return "BUY";
    if (rsi > 70) return "SELL";
    return "HOLD";
  }, [indicatorQuery.data?.rsi_14]);

  const buyMutation = useMutation({
    mutationFn: () =>
      tradingApi.placeOrder(token, {
        symbol,
        side: "BUY",
        quantity,
        order_type: "MARKET",
      }),
    onSuccess: (result) => setMessage(`매수 성공: ${result.status} @ ${result.price}`),
    onError: () => setMessage("매수 실패: 로그인 또는 주문 파라미터를 확인하세요."),
  });

  const sellMutation = useMutation({
    mutationFn: () =>
      tradingApi.placeOrder(token, {
        symbol,
        side: "SELL",
        quantity,
        order_type: "MARKET",
      }),
    onSuccess: (result) => setMessage(`매도 성공: ${result.status} @ ${result.price}`),
    onError: () => setMessage("매도 실패: 로그인 또는 보유수량을 확인하세요."),
  });

  return (
    <section className="space-y-4">
      <div className="card grid gap-3 md:grid-cols-3">
        <div>
          <h2 className="text-lg font-semibold">{symbol}</h2>
          <p>현재가: {quoteQuery.data?.price ?? 0}</p>
        </div>
        <div>
          <p>RSI: {indicatorQuery.data?.rsi_14 ?? 0}</p>
          <p>MACD: {indicatorQuery.data?.macd ?? 0}</p>
        </div>
        <div>
          <p className="font-medium">AI 예측 신호(단순 규칙): {signal}</p>
        </div>
      </div>

      <RealtimePriceChart symbol={symbol} />

      <div className="card flex flex-wrap items-end gap-2">
        <div className="w-24">
          <label className="mb-1 block text-sm">수량</label>
          <input
            className="input"
            type="number"
            min={1}
            value={quantity}
            onChange={(event) => setQuantity(Math.max(1, Number(event.target.value)))}
          />
        </div>
        <button className="button" onClick={() => buyMutation.mutate()}>
          시장가 매수
        </button>
        <button className="button bg-rose-600 hover:bg-rose-700" onClick={() => sellMutation.mutate()}>
          시장가 매도
        </button>
        <p className="text-sm text-slate-600">{message}</p>
      </div>
    </section>
  );
}
