/// <reference types="vitest" />
import { defineConfig, mergeConfig } from 'vitest/config';
import viteConfig from './vite.config';

/**
 * Vitest configuration for ForgeLedger Test frontend.
 * Extends the base Vite config to inherit path aliases, plugins, and CSS modules settings.
 * Configures jsdom environment, React Testing Library setup, and coverage thresholds.
 */
export default mergeConfig(
  viteConfig,
  defineConfig({
    test: {
      globals: true,
      environment: 'jsdom',
      setupFiles: ['./src/__tests__/setup.ts'],
      include: ['src/**/*.{test,spec}.{ts,tsx}'],
      exclude: ['node_modules', 'dist'],
      css: {
        modules: {
          classNameStrategy: 'non-scoped',
        },
      },
      coverage: {
        provider: 'v8',
        reporter: ['text', 'text-summary', 'lcov'],
        reportsDirectory: './coverage',
        include: ['src/**/*.{ts,tsx}'],
        exclude: [
          'src/__tests__/**',
          'src/main.tsx',
          'src/vite-env.d.ts',
          '**/*.d.ts',
          '**/*.config.{ts,js}',
        ],
        thresholds: {
          lines: 70,
          branches: 70,
          functions: 70,
          statements: 70,
        },
      },
      reporters: ['default'],
      passWithNoTests: true,
      restoreMocks: true,
    },
  })
);
