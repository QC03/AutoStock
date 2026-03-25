"use client";

import { QueryClientProvider } from "@tanstack/react-query";
import { ReactNode } from "react";

import { queryClient } from "@/lib/query-client";

type Props = {
  children: ReactNode;
};

export default function AppProviders({ children }: Props) {
  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
}
