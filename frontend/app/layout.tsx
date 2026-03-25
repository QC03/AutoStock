import type { Metadata } from "next";
import { ReactNode } from "react";

import AppNav from "@/components/AppNav";
import AppProviders from "@/components/providers/AppProviders";

import "./globals.css";

export const metadata: Metadata = {
  title: "AutoStock Frontend",
  description: "AutoStock trading dashboard",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="ko">
      <body>
        <AppProviders>
          <div className="mx-auto min-h-screen max-w-5xl p-4">
            <header className="mb-6 border-b border-slate-200 pb-3">
              <h1 className="mb-2 text-xl font-semibold">AutoStock</h1>
              <AppNav />
            </header>
            {children}
          </div>
        </AppProviders>
      </body>
    </html>
  );
}
