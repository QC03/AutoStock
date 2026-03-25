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
          <div className="mx-auto min-h-screen max-w-6xl p-4 md:p-8">
            <header className="mb-6 space-y-3">
              <h1 className="text-2xl font-bold">AutoStock</h1>
              <AppNav />
            </header>
            {children}
          </div>
        </AppProviders>
      </body>
    </html>
  );
}
