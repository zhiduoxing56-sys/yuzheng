export interface RuntimeConfig {
  apiBaseUrl?: string;
  websocketBaseUrl?: string;
}

let configPromise: Promise<RuntimeConfig> | undefined;

function trimTrailingSlash(value: string): string {
  return value.replace(/\/+$/, "");
}

export async function loadRuntimeConfig(): Promise<RuntimeConfig> {
  if (!configPromise) {
    configPromise = fetch("/runtime-config.json", { cache: "no-store" })
      .then(async (response) => {
        if (!response.ok) return {};
        const value = (await response.json()) as RuntimeConfig;
        return {
          apiBaseUrl: value.apiBaseUrl ? trimTrailingSlash(value.apiBaseUrl) : undefined,
          websocketBaseUrl: value.websocketBaseUrl
            ? trimTrailingSlash(value.websocketBaseUrl)
            : undefined,
        };
      })
      .catch(() => ({}));
  }
  return configPromise;
}

export async function resolveApiBaseUrl(): Promise<string> {
  if (import.meta.env.DEV) return window.location.origin;
  const runtime = await loadRuntimeConfig();
  const environment = import.meta.env.VITE_API_BASE_URL as string | undefined;
  return trimTrailingSlash(runtime.apiBaseUrl || environment || window.location.origin);
}

export async function resolveWebsocketBaseUrl(): Promise<string> {
  if (import.meta.env.DEV) return window.location.origin.replace(/^http/i, "ws");
  const runtime = await loadRuntimeConfig();
  const environment = import.meta.env.VITE_WEBSOCKET_BASE_URL as string | undefined;
  if (runtime.websocketBaseUrl || environment) {
    return trimTrailingSlash(runtime.websocketBaseUrl || environment || "");
  }
  const apiBase = await resolveApiBaseUrl();
  return apiBase.replace(/^http/i, "ws");
}
