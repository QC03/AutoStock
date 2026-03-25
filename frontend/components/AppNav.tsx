"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { usePathname } from "next/navigation";
import { useAuthToken } from "@/hooks/useAuthToken";
import { tradingApi } from "@/lib/api/endpoints";

const publicLinks = [
  { href: "/login", label: "로그인" },
  { href: "/signup", label: "회원가입" },
];

const privateLinks = [
  { href: "/dashboard", label: "대시보드" },
  { href: "/stocks/AAPL", label: "종목상세" },
  { href: "/settings/trading", label: "자동매매" },
  { href: "/trades", label: "매매내역" },
];

export default function AppNav() {
  const pathname = usePathname();
  const { token, clearToken } = useAuthToken();

  const autoTradeStatusQuery = useQuery({
    queryKey: ["auto-trade-status", token],
    queryFn: () => tradingApi.getAutoTradeStatus(token),
    enabled: Boolean(token),
    refetchInterval: 5000,
  });

  const links = token ? privateLinks : publicLinks;

  const isActive = (href: string) => pathname === href || pathname.startsWith(href + "/");

  return (
    <nav className="flex flex-wrap items-center gap-4 text-sm">
      {links.map((item) => (
        <div key={item.href} className="flex items-center gap-1">
          <Link
            href={item.href}
            className={isActive(item.href) ? "font-semibold text-slate-900 underline" : "text-slate-600 hover:text-slate-900"}
          >
            {item.label}
          </Link>
          {item.href === "/settings/trading" && token && (
            <span
              className={`rounded px-1.5 py-0.5 text-xs font-medium ${
                autoTradeStatusQuery.data?.enabled ? "bg-red-100 text-red-700" : "bg-slate-100 text-slate-600"
              }`}
            >
              {autoTradeStatusQuery.isLoading ? "..." : autoTradeStatusQuery.data?.enabled ? "ON" : "OFF"}
            </span>
          )}
        </div>
      ))}
      {token && (
        <button
          onClick={() => {
            clearToken();
            window.location.href = "/login";
          }}
          className="ml-auto text-slate-600 hover:text-slate-900"
        >
          로그아웃
        </button>
      )}
    </nav>
  );
}
