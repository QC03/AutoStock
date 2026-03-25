"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";

import { dashboardApi } from "@/lib/api/endpoints";
import { useAuthToken } from "@/hooks/useAuthToken";

export default function TradesPage() {
  const { token } = useAuthToken();

  const tradesQuery = useQuery({
    queryKey: ["trades", token],
    queryFn: () => dashboardApi.trades(token),
    enabled: Boolean(token),
  });

  if (!token) {
    return (
      <section className="card text-center">
        <p className="text-slate-600">로그인이 필요합니다.</p>
        <Link href="/login" className="mt-3 inline-block font-medium text-brand-600 hover:text-brand-700">
          로그인하기
        </Link>
      </section>
    );
  }

  const trades = tradesQuery.data ?? [];
  const isLoading = tradesQuery.isLoading;

  return (
    <section className="card space-y-4">
      <h2 className="text-lg font-semibold">매매 내역</h2>

      {isLoading ? (
        <div className="text-center text-slate-500">로딩 중...</div>
      ) : trades.length > 0 ? (
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200 text-left">
                <th className="py-2">시각</th>
                <th className="py-2">종목</th>
                <th className="py-2">구분</th>
                <th className="py-2 text-right">수량</th>
                <th className="py-2 text-right">가격</th>
                <th className="py-2">상태</th>
              </tr>
            </thead>
            <tbody>
              {trades.map((item, index) => (
                <tr key={`${item.created_at}-${index}`} className="border-b border-slate-100">
                  <td className="py-2 text-slate-600">{new Date(item.created_at).toLocaleString()}</td>
                  <td className="py-2">{item.symbol}</td>
                  <td className="py-2">{item.side}</td>
                  <td className="py-2 text-right">{item.quantity}</td>
                  <td className="py-2 text-right">${item.price.toFixed(2)}</td>
                  <td className="py-2">{item.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="text-center text-slate-500">
          <p className="mb-2">매매 내역이 없습니다.</p>
          <Link href="/stocks/AAPL" className="text-sm font-medium text-brand-600 hover:text-brand-700">
            종목 거래하기
          </Link>
        </div>
      )}
    </section>
  );
}
