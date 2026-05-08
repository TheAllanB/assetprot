const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

function getTokens(): { accessToken: string | null; refreshToken: string | null } {
  if (typeof window === "undefined") {
    return { accessToken: null, refreshToken: null };
  }
  return {
    accessToken: localStorage.getItem("access_token"),
    refreshToken: localStorage.getItem("refresh_token"),
  };
}

function setTokens(tokens: TokenPair): void {
  localStorage.setItem("access_token", tokens.access_token);
  localStorage.setItem("refresh_token", tokens.refresh_token);
}

function clearTokens(): void {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
}

async function fetchApi<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const { accessToken } = getTokens();
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...options.headers,
  };

  if (accessToken) {
    (headers as Record<string, string>)["Authorization"] = `Bearer ${accessToken}`;
  }

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: { message: "Request failed" } }));
    throw new Error(error.error?.message || `HTTP ${response.status}`);
  }

  return response.json();
}

export const api = {
  auth: {
    register: (data: { email: string; password: string; org_name: string }) =>
      fetchApi<{ success: boolean; data: TokenPair }>("/auth/register", {
        method: "POST",
        body: JSON.stringify(data),
      }),

    login: (data: { email: string; password: string }) =>
      fetchApi<{ success: boolean; data: TokenPair }>("/auth/login", {
        method: "POST",
        body: JSON.stringify(data),
      }).then((res) => {
        setTokens(res.data);
        return res;
      }),

    refresh: () => {
      const { refreshToken } = getTokens();
      return fetchApi<{ success: boolean; data: TokenPair }>("/auth/refresh", {
        method: "POST",
        body: JSON.stringify({ refresh_token: refreshToken }),
      }).then((res) => {
        setTokens(res.data);
        return res;
      });
    },

    me: () =>
      fetchApi<{ success: boolean; data: { user: { id: string; email: string; org_id: string } } }>(
        "/auth/me"
      ),

    logout: () => {
      clearTokens();
    },
  },

  assets: {
    list: (offset = 0, limit = 20) =>
      fetchApi<{
        success: boolean;
        data: import("./types").Asset[];
        meta: { total: number; offset: number; limit: number };
      }>(`/api/v1/assets?offset=${offset}&limit=${limit}`),

    get: (id: string) =>
      fetchApi<{ success: boolean; data: import("./types").Asset }>(`/api/v1/assets/${id}`),

    upload: async (formData: FormData) => {
      const { accessToken } = getTokens();
      const response = await fetch(`${API_URL}/api/v1/assets`, {
        method: "POST",
        headers: accessToken
          ? { Authorization: `Bearer ${accessToken}` }
          : undefined,
        body: formData,
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ error: { message: "Upload failed" } }));
        throw new Error(error.error?.message || `HTTP ${response.status}`);
      }

      return response.json();
    },
  },

  violations: {
    list: (offset = 0, limit = 20) =>
      fetchApi<{
        success: boolean;
        data: import("./types").Violation[];
        meta: { total: number; offset: number; limit: number };
      }>(`/api/v1/violations?offset=${offset}&limit=${limit}`),
  },

  scanRuns: {
    list: (offset = 0, limit = 20) =>
      fetchApi<{
        success: boolean;
        data: import("./types").ScanRun[];
        meta: { total: number; offset: number; limit: number };
      }>(`/api/v1/scan-runs?offset=${offset}&limit=${limit}`),

    trigger: (assetId: string) =>
      fetchApi<{ success: boolean; data: { scan_run_id: string; status: string } }>(
        "/api/v1/scan-runs",
        {
          method: "POST",
          body: JSON.stringify({ asset_id: assetId }),
        }
      ),
  },

  tasks: {
    getStatus: (taskId: string) =>
      fetchApi<{
        success: boolean;
        data: import("./types").TaskStatus;
      }>(`/api/v1/tasks/${taskId}`),
  },
};