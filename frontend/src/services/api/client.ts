/**
 * Resilient HTTP Client for API Communications
 */

export class ApiError extends Error {
  status: number;
  detail: unknown;

  constructor(message: string, status: number = 500, detail?: unknown) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.detail = detail;
  }
}

const BASE_URL = import.meta.env.VITE_API_URL || '';
const DEFAULT_TIMEOUT_MS = 20000;

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${BASE_URL}${endpoint}`;
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), DEFAULT_TIMEOUT_MS);

  const config: RequestInit = {
    ...options,
    signal: controller.signal,
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
      ...options.headers,
    },
  };

  try {
    const response = await fetch(url, config);
    clearTimeout(timeoutId);

    if (!response.ok) {
      let errorMessage = `HTTP error ${response.status}: ${response.statusText}`;
      let errorDetail: unknown = null;
      try {
        const body = await response.json();
        errorDetail = body;
        if (body && typeof body.detail === 'string') {
          errorMessage = body.detail;
        } else if (body && body.detail) {
          errorMessage = JSON.stringify(body.detail);
        } else if (body && body.message) {
          errorMessage = body.message;
        }
      } catch {
        // Body is not JSON, use default status text
      }
      throw new ApiError(errorMessage, response.status, errorDetail);
    }

    return (await response.json()) as T;
  } catch (error: unknown) {
    clearTimeout(timeoutId);
    if (error instanceof ApiError) {
      throw error;
    }
    if (error instanceof DOMException && error.name === 'AbortError') {
      throw new ApiError(`Yêu cầu quá hạn sau ${DEFAULT_TIMEOUT_MS / 1000}s. Vui lòng thử lại.`, 408);
    }
    const message = error instanceof Error ? error.message : 'Không thể kết nối đến máy chủ';
    throw new ApiError(message, 0);
  }
}

export const apiClient = {
  get: <T>(endpoint: string) => request<T>(endpoint, { method: 'GET' }),
  post: <T>(endpoint: string, body: unknown) =>
    request<T>(endpoint, {
      method: 'POST',
      body: JSON.stringify(body),
    }),
};
