import React from 'react';
import ReactDOM from 'react-dom/client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import App from './App';

/**
 * QueryClient instance configured for the ForgeLedger application.
 * 
 * Default options:
 * - staleTime: 30 seconds to reduce unnecessary refetches for a single-user app
 * - retry: 1 attempt on failure (network resilience without excessive retries)
 * - refetchOnWindowFocus: disabled to prevent unexpected UI updates during form editing
 */
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30 * 1000,
      retry: 1,
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: 0,
    },
  },
});

const rootElement = document.getElementById('root');

if (!rootElement) {
  throw new Error(
    'Root element not found. Ensure index.html contains a <div id="root"></div> element.'
  );
}

ReactDOM.createRoot(rootElement).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </React.StrictMode>
);
