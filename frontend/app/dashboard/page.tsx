"use client";

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
    return <div className="card">로그인이 필요합니다. 먼저 로그인/회원가입을 진행하세요.</div>;
  }

  return (
    <section className="grid gap-4 md:grid-cols-2">
      <div className="card space-y-2">
        <h2 className="text-lg font-semibold">포트폴리오 현황</h2>
        <p>현금: {portfolioQuery.data?.cash ?? 0}</p>
        <p>총 자산: {portfolioQuery.data?.total_value ?? 0}</p>
        <p>평가손익: {portfolioQuery.data?.total_unrealized_pnl ?? 0}</p>
      </div>

      <div className="card space-y-2">
        <h2 className="text-lg font-semibold">수익률/거래 지표</h2>
        <p>총 주문 수: {performanceQuery.data?.order_count ?? 0}</p>
        <p>매수 건수: {performanceQuery.data?.buy_count ?? 0}</p>
        <p>매도 건수: {performanceQuery.data?.sell_count ?? 0}</p>
        <p>누적 체결 금액: {performanceQuery.data?.notional ?? 0}</p>
      </div>

      <div className="card md:col-span-2">
        <h3 className="mb-2 text-base font-semibold">보유 종목</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200 text-left">
                <th className="py-2">종목</th>
                <th className="py-2">수량</th>
                <th className="py-2">평균가</th>
                <th className="py-2">현재가</th>
                <th className="py-2">평가손익</th>
              </tr>
            </thead>
            <tbody>
              {(portfolioQuery.data?.positions ?? []).map((item) => (
                <tr key={String(item.symbol)} className="border-b border-slate-100">
                  <td className="py-2">{item.symbol}</td>
                  <td className="py-2">{item.quantity}</td>
                  <td className="py-2">{item.avg_price}</td>
                  <td className="py-2">{item.market_price}</td>
                  <td className="py-2">{item.unrealized_pnl}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}
