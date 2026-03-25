import { apiClient, authHeaders } from "@/lib/api/client";

export type LoginPayload = {
  username: string;
  password: string;
};

export type OrderPayload = {
  symbol: string;
  side: "BUY" | "SELL";
  quantity: number;
  order_type?: "MARKET" | "LIMIT";
  limit_price?: number;
};

export const authApi = {
  signup: async (payload: LoginPayload) => {
    const { data } = await apiClient.post("/auth/signup", payload);
    return data as { access_token: string; token_type: string };
  },
  login: async (payload: LoginPayload) => {
    const { data } = await apiClient.post("/auth/login", payload);
    return data as { access_token: string; token_type: string };
  },
};

export const dataApi = {
  searchSymbols: async (query: string) => {
    const { data } = await apiClient.get("/data/search", { params: { query } });
    return data as Array<{ symbol: string; name: string; market: string }>;
  },
  quote: async (symbol: string) => {
    const { data } = await apiClient.get(`/data/quote/${symbol}`);
    return data as { symbol: string; price: number };
  },
  indicators: async (symbol: string) => {
    const { data } = await apiClient.get(`/data/indicators/${symbol}`);
    return data as {
      symbol: string;
      trade_date: string;
      sma_20: number;
      rsi_14: number;
      macd: number;
      macd_signal: number;
      bollinger_upper: number;
      bollinger_lower: number;
    };
  },
};

export const tradingApi = {
  placeOrder: async (token: string | null, payload: OrderPayload) => {
    const { data } = await apiClient.post("/trading/orders", payload, {
      headers: authHeaders(token),
    });
    return data as {
      id: number;
      order_id: string;
      symbol: string;
      side: string;
      order_type: string;
      quantity: number;
      price: number;
      status: string;
      reason: string;
    };
  },
  toggleAutoTrade: async (token: string | null, enabled: boolean) => {
    const { data } = await apiClient.post(
      "/trading/auto-trade",
      { enabled },
      { headers: authHeaders(token) }
    );
    return data as { enabled: boolean };
  },
};

export const dashboardApi = {
  portfolio: async (token: string | null) => {
    const { data } = await apiClient.get("/dashboard/portfolio", {
      headers: authHeaders(token),
    });
    return data as {
      cash: number;
      total_value: number;
      total_unrealized_pnl: number;
      positions: Array<{
        symbol: string;
        quantity: number;
        avg_price: number;
        market_price: number;
        market_value: number;
        unrealized_pnl: number;
      }>;
    };
  },
  trades: async (token: string | null) => {
    const { data } = await apiClient.get("/dashboard/trades", {
      headers: authHeaders(token),
    });
    return data as Array<{
      symbol: string;
      side: string;
      quantity: number;
      price: number;
      status: string;
      created_at: string;
    }>;
  },
  performance: async (token: string | null) => {
    const { data } = await apiClient.get("/dashboard/performance", {
      headers: authHeaders(token),
    });
    return data as { order_count: number; buy_count: number; sell_count: number; notional: number };
  },
};
