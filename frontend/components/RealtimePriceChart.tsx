"use client";

import { useEffect, useMemo, useState } from "react";
import {
  CartesianGrid,
  ComposedChart,
  Area,
  Line,
  ResponsiveContainer,
  TooltipProps,
  Tooltip,
  XAxis,
  YAxis,
  ReferenceLine,
} from "recharts";

type Point = {
  time: string;
  price: number;
};

type Props = {
  symbol: string;
};

export default function RealtimePriceChart({ symbol }: Props) {
  const [points, setPoints] = useState<Point[]>([]);

  useEffect(() => {
    const key = `autostock:chart:${symbol}`;
    const raw = window.sessionStorage.getItem(key);
    if (!raw) return;
    try {
      const cached = JSON.parse(raw) as Point[];
      if (Array.isArray(cached) && cached.length > 0) {
        setPoints(cached.slice(-40));
      }
    } catch {
      window.sessionStorage.removeItem(key);
    }
  }, [symbol]);

  useEffect(() => {
    const baseWs = (process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000").replace("http", "ws");
    const socket = new WebSocket(`${baseWs}/ws/quotes/${symbol}`);

    socket.onmessage = (event) => {
      const payload = JSON.parse(event.data) as { symbol?: string; price?: number; timestamp?: string; error?: string };
      if (payload.error || payload.price === undefined || payload.timestamp === undefined) return;

      const date = new Date(payload.timestamp);
      setPoints((current) => {
        const next = [...current, { time: date.toLocaleTimeString(), price: payload.price as number }];
        return next.slice(-40);
      });
    };

    socket.onerror = () => {
      setPoints((current) => current);
    };

    return () => socket.close();
  }, [symbol]);

  useEffect(() => {
    const key = `autostock:chart:${symbol}`;
    window.sessionStorage.setItem(key, JSON.stringify(points.slice(-40)));
  }, [points, symbol]);

  const latestPrice = useMemo(() => points[points.length - 1]?.price ?? 0, [points]);
  const basePrice = useMemo(() => points[0]?.price ?? 0, [points]);
  const highPrice = useMemo(() => (points.length ? Math.max(...points.map((point) => point.price)) : 0), [points]);
  const lowPrice = useMemo(() => (points.length ? Math.min(...points.map((point) => point.price)) : 0), [points]);
  const priceDiff = useMemo(() => latestPrice - basePrice, [latestPrice, basePrice]);
  const diffPct = useMemo(() => (basePrice > 0 ? (priceDiff / basePrice) * 100 : 0), [basePrice, priceDiff]);
  const isUp = priceDiff >= 0;
  const trendColor = isUp ? "#dc2626" : "#2563eb";

  const formatPrice = (value: number) =>
    new Intl.NumberFormat("ko-KR", { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(value);

  const CustomTooltip = ({ active, payload }: TooltipProps<number, string>) => {
    if (!active || !payload || payload.length === 0) return null;
    const point = payload[0]?.payload as Point;
    return (
      <div className="rounded-md border border-slate-200 bg-white p-2 text-xs shadow-sm">
        <p className="text-slate-600">{point?.time ?? "-"}</p>
        <p className="font-semibold">{formatPrice(point?.price ?? 0)}원</p>
      </div>
    );
  };

  return (
    <div className="card h-80">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-lg font-semibold">실시간 시세 ({symbol})</h3>
        <div className="text-right text-sm">
          <p className="text-slate-700">현재가: {formatPrice(latestPrice)}원</p>
          <p className={isUp ? "text-red-600" : "text-blue-600"}>
            {isUp ? "+" : ""}
            {formatPrice(priceDiff)} ({isUp ? "+" : ""}
            {diffPct.toFixed(2)}%)
          </p>
          <p className="text-xs text-slate-500">
            고가 {formatPrice(highPrice)} / 저가 {formatPrice(lowPrice)}
          </p>
        </div>
      </div>
      <ResponsiveContainer width="100%" height="85%">
        <ComposedChart data={points} margin={{ top: 5, right: 8, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="priceFill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={trendColor} stopOpacity={0.22} />
              <stop offset="95%" stopColor={trendColor} stopOpacity={0.02} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis dataKey="time" tick={{ fontSize: 11 }} minTickGap={20} />
          <YAxis
            orientation="right"
            domain={["dataMin", "dataMax"]}
            tick={{ fontSize: 11 }}
            tickFormatter={(value) => `${Number(value).toFixed(0)}`}
            width={64}
          />
          <ReferenceLine y={basePrice || undefined} stroke="#94a3b8" strokeDasharray="4 4" />
          {highPrice > 0 && (
            <ReferenceLine
              y={highPrice}
              stroke="#fca5a5"
              strokeDasharray="3 3"
              label={{ value: `고가 ${formatPrice(highPrice)}`, position: "insideTopRight", fill: "#b91c1c", fontSize: 11 }}
            />
          )}
          {lowPrice > 0 && (
            <ReferenceLine
              y={lowPrice}
              stroke="#93c5fd"
              strokeDasharray="3 3"
              label={{ value: `저가 ${formatPrice(lowPrice)}`, position: "insideBottomRight", fill: "#1d4ed8", fontSize: 11 }}
            />
          )}
          <Tooltip content={<CustomTooltip />} />
          <Area type="linear" dataKey="price" stroke="none" fill="url(#priceFill)" isAnimationActive={false} />
          <Line type="monotone" dataKey="price" stroke={trendColor} strokeWidth={2} dot={false} isAnimationActive={false} />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
