import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import App from '../App';

/**
 * Smoke tests for the root App component.
 *
 * Verifies that the application renders without crashing and displays
 * expected placeholder content for the Phase 0 skeleton.
 */
describe('App', () => {
  it('renders without crashing', () => {
    const { container } = render(<App />);
    expect(container).toBeDefined();
  });

  it('displays the application title on the dashboard', () => {
    render(<App />);
    const heading = screen.getByText('ForgeLedger Test');
    expect(heading).toBeDefined();
    expect(heading.tagName).toBe('H1');
  });

  it('displays the application description', () => {
    render(<App />);
    const description = screen.getByText(
      'Lightweight financial ledger for tracking income and expenses.'
    );
    expect(description).toBeDefined();
  });

  it('displays the dashboard placeholder message', () => {
    render(<App />);
    const placeholder = screen.getByText('Dashboard coming soon.');
    expect(placeholder).toBeDefined();
  });
});
