"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";

import { dashboardApi } from "@/lib/api/endpoints";
import { useAuthToken } from "@/hooks/useAuthToken";

export default function DashboardPage() {
  const { token } = useAuthToken();

  const portfolioQuery = useQuery({
    queryKey: ["portfolio", token],
    queryFn: () => dashboardApi.portfolio(token),
    enabled: Boolean(token),
  });

  const performanceQuery = useQuery({
    queryKey: ["performance", token],
    queryFn: () => dashboardApi.performance(token),
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

  const isLoading = portfolioQuery.isLoading || performanceQuery.isLoading;

  return (
    <section className="space-y-4">
      <div className="card">
        <h2 className="mb-3 text-lg font-semibold">요약</h2>
        {isLoading ? (
          <div className="text-sm text-slate-500">로딩 중...</div>
        ) : (
          <div className="grid gap-2 text-sm md:grid-cols-2">
            <p>현금: ${portfolioQuery.data?.cash.toFixed(2) ?? 0}</p>
            <p>총 자산: ${portfolioQuery.data?.total_value.toFixed(2) ?? 0}</p>
            <p>평가손익: ${portfolioQuery.data?.total_unrealized_pnl.toFixed(2) ?? 0}</p>
            <p>총 주문 수: {performanceQuery.data?.order_count ?? 0}</p>
            <p>매수 건수: {performanceQuery.data?.buy_count ?? 0}</p>
            <p>매도 건수: {performanceQuery.data?.sell_count ?? 0}</p>
            <p>누적 체결 금액: ${performanceQuery.data?.notional.toFixed(2) ?? 0}</p>
          </div>
        )}
      </div>

      <div className="card">
        <h3 className="mb-3 text-lg font-semibold">보유 종목</h3>
        {isLoading ? (
          <div className="text-sm text-slate-500">로딩 중...</div>
        ) : (portfolioQuery.data?.positions ?? []).length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="border-b border-slate-200 text-left">
                  <th className="py-2">종목</th>
                  <th className="py-2 text-right">수량</th>
                  <th className="py-2 text-right">평균가</th>
                  <th className="py-2 text-right">현재가</th>
                  <th className="py-2 text-right">평가손익</th>
                </tr>
              </thead>
              <tbody>
                {(portfolioQuery.data?.positions ?? []).map((item) => (
                  <tr key={String(item.symbol)} className="border-b border-slate-100">
                    <td className="py-2">{item.symbol}</td>
                    <td className="py-2 text-right">{item.quantity}</td>
                    <td className="py-2 text-right">${item.avg_price.toFixed(2)}</td>
                    <td className="py-2 text-right">${item.market_price.toFixed(2)}</td>
                    <td className="py-2 text-right">${item.unrealized_pnl.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-sm text-slate-500">
            보유 종목이 없습니다. <Link href="/stocks/AAPL" className="text-brand-600">종목 거래하기</Link>
          </div>
        )}
      </div>
    </section>
  );
}
