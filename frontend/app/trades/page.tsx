"use client";

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
    return <div className="card">로그인이 필요합니다.</div>;
  }

  return (
    <section className="card">
      <h2 className="mb-3 text-lg font-semibold">매매 내역</h2>
      <div className="overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead>
            <tr className="border-b border-slate-200 text-left">
              <th className="py-2">시각</th>
              <th className="py-2">종목</th>
              <th className="py-2">구분</th>
              <th className="py-2">수량</th>
              <th className="py-2">가격</th>
              <th className="py-2">상태</th>
            </tr>
          </thead>
          <tbody>
            {(tradesQuery.data ?? []).map((item, index) => (
              <tr key={`${item.created_at}-${index}`} className="border-b border-slate-100">
                <td className="py-2">{new Date(item.created_at).toLocaleString()}</td>
                <td className="py-2">{item.symbol}</td>
                <td className="py-2">{item.side}</td>
                <td className="py-2">{item.quantity}</td>
                <td className="py-2">{item.price}</td>
                <td className="py-2">{item.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
