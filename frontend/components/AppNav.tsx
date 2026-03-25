"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/login", label: "로그인" },
  { href: "/signup", label: "회원가입" },
  { href: "/dashboard", label: "대시보드" },
  { href: "/stocks/AAPL", label: "종목상세" },
  { href: "/settings/trading", label: "매매설정" },
  { href: "/trades", label: "매매내역" },
];

export default function AppNav() {
  const pathname = usePathname();

  return (
    <nav className="flex flex-wrap gap-2">
      {links.map((item) => {
        const active = pathname.startsWith(item.href);
        return (
          <Link
            key={item.href}
            href={item.href}
            className={`rounded-md px-3 py-2 text-sm ${
              active ? "bg-brand-600 text-white" : "bg-slate-200 text-slate-700 hover:bg-slate-300"
            }`}
          >
            {item.label}
          </Link>
        );
      })}
    </nav>
  );
}
