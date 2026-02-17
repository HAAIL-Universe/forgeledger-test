/**
 * ForgeLedger Test — Axios API Client Configuration
 *
 * Centralized Axios instance with base URL, timeout, and error interceptors.
 * All API client modules (transactions.ts, categories.ts) import this instance
 * rather than creating their own. This module handles HTTP-level concerns only:
 * request/response serialization, error normalization, and base configuration.
 *
 * MUST NOT contain React hooks, component state, or UI rendering logic.
 * MUST NOT perform client-side validation or data transformation beyond JSON mapping.
 */

import axios, { AxiosError, AxiosInstance, AxiosResponse, InternalAxiosRequestConfig } from "axios";
import type { ErrorResponse } from "../types";

/**
 * Resolve the API base URL from environment or defaults.
 *
 * In development, Vite proxies `/api` to the backend server.
 * In production, the backend serves the frontend static files,
 * so relative paths work directly.
 */
const resolveBaseUrl = (): string => {
  // Vite exposes env vars prefixed with VITE_
  const envBaseUrl = import.meta.env.VITE_API_BASE_URL;
  if (envBaseUrl && typeof envBaseUrl === "string") {
    return envBaseUrl;
  }
  // Default: relative /api prefix (works in both dev proxy and prod)
  return "/api";
};

/** Default request timeout in milliseconds */
const DEFAULT_TIMEOUT_MS = 15_000;

/**
 * Create and configure the shared Axios instance.
 *
 * @returns Configured Axios instance for all API communication
 */
const createApiClient = (): AxiosInstance => {
  const client = axios.create({
    baseURL: resolveBaseUrl(),
    timeout: DEFAULT_TIMEOUT_MS,
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
  });

  // -- Request Interceptor ------------------------------------------
  client.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
      // Placeholder: attach auth headers here if auth is added later.
      // No authentication in MVP — single-user application.
      return config;
    },
    (error: AxiosError) => {
      return Promise.reject(error);
    }
  );

  // -- Response Interceptor -----------------------------------------
  client.interceptors.response.use(
    (response: AxiosResponse) => {
      // Pass successful responses through unmodified
      return response;
    },
    (error: AxiosError<ErrorResponse>) => {
      // Normalize error shape for consumers
      if (error.response) {
        // Server responded with an error status code
        const { status, data } = error.response;

        const normalizedError: ApiError = {
          status,
          message: extractErrorMessage(data, status),
          details: data?.details ?? null,
          timestamp: data?.timestamp ?? new Date().toISOString(),
          originalError: error,
        };

        return Promise.reject(normalizedError);
      }

      if (error.request) {
        // Request was made but no response received (network error)
        const networkError: ApiError = {
          status: 0,
          message: "Network error. Please check your connection and try again.",
          details: null,
          timestamp: new Date().toISOString(),
          originalError: error,
        };

        return Promise.reject(networkError);
      }

      // Something went wrong setting up the request
      const setupError: ApiError = {
        status: -1,
        message: error.message || "An unexpected error occurred.",
        details: null,
        timestamp: new Date().toISOString(),
        originalError: error,
      };

      return Promise.reject(setupError);
    }
  );

  return client;
};

/**
 * Extract a human-readable error message from the API error response.
 *
 * @param data - The error response body from the API
 * @param status - The HTTP status code
 * @returns A user-friendly error message string
 */
const extractErrorMessage = (
  data: ErrorResponse | undefined | null,
  status: number
): string => {
  if (data?.message) {
    return data.message;
  }

  if (data?.error) {
    return data.error;
  }

  // Fallback messages based on status code
  switch (status) {
    case 400:
      return "Invalid request. Please check your input and try again.";
    case 404:
      return "The requested resource was not found.";
    case 422:
      return "Validation error. Please check the form fields.";
    case 500:
      return "Internal server error. Please try again later.";
    default:
      return `Request failed with status ${status}.`;
  }
};

/**
 * Normalized API error structure used throughout the frontend.
 * All API client consumers catch this shape instead of raw AxiosError.
 */
export interface ApiError {
  /** HTTP status code (0 for network errors, -1 for setup errors) */
  status: number;
  /** Human-readable error message */
  message: string;
  /** Additional error details from the API, if any */
  details: Record<string, unknown> | null;
  /** ISO 8601 timestamp of when the error occurred */
  timestamp: string;
  /** Original Axios error for debugging */
  originalError: AxiosError;
}

/**
 * Type guard to check if an unknown error is an ApiError.
 *
 * @param error - The error to check
 * @returns True if the error matches the ApiError shape
 */
export const isApiError = (error: unknown): error is ApiError => {
  return (
    typeof error === "object" &&
    error !== null &&
    "status" in error &&
    "message" in error &&
    "originalError" in error
  );
};

/** Shared Axios instance — import this in all API client modules */
const apiClient: AxiosInstance = createApiClient();

export default apiClient;
