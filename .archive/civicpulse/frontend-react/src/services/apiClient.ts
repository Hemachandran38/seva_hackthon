/**
 * CivicPulse API Client
 *
 * Centralized HTTP client for all backend API requests.
 * Handles base URL, headers, error handling, and response parsing.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

export interface ApiErrorResponse {
  status: number;
  detail: string;
  timestamp?: string;
}

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
    public detail?: string
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

/**
 * Type-safe fetch wrapper with error handling
 */
async function apiFetch<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  try {
    const response = await fetch(url, {
      ...options,
      headers,
      timeout: 30000, // 30 second timeout
    } as any);

    // Handle non-JSON responses
    const contentType = response.headers.get('content-type');
    let data: any;

    if (contentType?.includes('application/json')) {
      data = await response.json();
    } else {
      data = await response.text();
    }

    // Handle error responses
    if (!response.ok) {
      const errorMessage = typeof data === 'object' && data?.detail
        ? data.detail
        : `HTTP ${response.status}`;

      throw new ApiError(
        response.status,
        errorMessage,
        typeof data === 'object' ? JSON.stringify(data) : data
      );
    }

    return data as T;
  } catch (error) {
    // Re-throw ApiError as-is
    if (error instanceof ApiError) {
      throw error;
    }

    // Network or parse errors
    if (error instanceof TypeError) {
      throw new ApiError(
        0,
        `Network error: ${error.message}`,
        error.message
      );
    }

    // Unknown errors
    throw new ApiError(
      500,
      `Unknown error: ${error instanceof Error ? error.message : String(error)}`,
      String(error)
    );
  }
}

/**
 * GET request
 */
export function apiGet<T>(endpoint: string, queryParams?: Record<string, any>): Promise<T> {
  let url = endpoint;

  if (queryParams) {
    const params = new URLSearchParams();
    Object.entries(queryParams).forEach(([key, value]) => {
      if (value !== null && value !== undefined && value !== '') {
        if (Array.isArray(value)) {
          value.forEach(v => params.append(key, String(v)));
        } else {
          params.set(key, String(value));
        }
      }
    });

    const query = params.toString();
    if (query) {
      url = `${endpoint}${endpoint.includes('?') ? '&' : '?'}${query}`;
    }
  }

  return apiFetch<T>(url, {
    method: 'GET',
  });
}

/**
 * POST request
 */
export function apiPost<T>(endpoint: string, data?: any): Promise<T> {
  return apiFetch<T>(endpoint, {
    method: 'POST',
    body: data ? JSON.stringify(data) : undefined,
  });
}

/**
 * PATCH request
 */
export function apiPatch<T>(endpoint: string, data: any): Promise<T> {
  return apiFetch<T>(endpoint, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

/**
 * PUT request
 */
export function apiPut<T>(endpoint: string, data: any): Promise<T> {
  return apiFetch<T>(endpoint, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

/**
 * DELETE request
 */
export function apiDelete<T>(endpoint: string): Promise<T> {
  return apiFetch<T>(endpoint, {
    method: 'DELETE',
  });
}

export const apiClient = {
  get: apiGet,
  post: apiPost,
  patch: apiPatch,
  put: apiPut,
  delete: apiDelete,
  baseUrl: API_BASE_URL,
};
