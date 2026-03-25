"use client";

import { useEffect, useMemo, useState } from "react";
import {
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
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

  const latestPrice = useMemo(() => points[points.length - 1]?.price ?? 0, [points]);

  return (
    <div className="card h-80">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-lg font-semibold">실시간 시세 차트 ({symbol})</h3>
        <span className="text-sm text-slate-600">현재가: {latestPrice.toFixed(2)}</span>
      </div>
      <ResponsiveContainer width="100%" height="85%">
        <LineChart data={points}>
          <XAxis dataKey="time" tick={{ fontSize: 12 }} />
          <YAxis domain={["auto", "auto"]} tick={{ fontSize: 12 }} />
          <Tooltip />
          <Line type="monotone" dataKey="price" stroke="#0284c7" strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
