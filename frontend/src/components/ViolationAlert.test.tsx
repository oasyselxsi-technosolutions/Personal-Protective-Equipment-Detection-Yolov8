

// --- Improved Mock for socket.io-client ---
// Use a top-level singleton for the mock socket to avoid initialization order issues
// Use a plain object for mockSocket and assign .on/.off after jest.mock
var mockSocket: any = {};
jest.mock('socket.io-client', () => ({
  io: jest.fn(() => mockSocket),
}));
jest.mock('socket.io-client', () => ({
  io: jest.fn(() => mockSocket),
}));

import React from 'react';
import { render, screen, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import ViolationAlert from './ViolationAlert';

// ...rest of your test code...

describe('ViolationAlert', () => {
  beforeEach(() => {
    // Always re-assign .on and .off before each test to ensure they're defined
    mockSocket.on = jest.fn((event: string, cb: (...args: any[]) => void) => {
      mockSocket[`__cb_${event}`] = cb;
    });
    mockSocket.off = jest.fn((event: string) => {
      delete mockSocket[`__cb_${event}`];
    });
    // Remove any previously registered event handlers
    Object.keys(mockSocket)
      .filter(k => k.startsWith('__cb_'))
      .forEach(k => delete mockSocket[k]);
  });

  it('renders alerts received via WebSocket', async () => {
    render(<ViolationAlert />);
    const violation = {
      type: 'No Helmet',
      location: 'Zone A',
      timestamp: '2025-07-14T12:00:00Z',
    };
    act(() => {
      mockSocket['__cb_violation_alert'](violation);
    });
    expect(await screen.findByText(/No Helmet/)).toBeInTheDocument();
    expect(screen.getByText(/Zone A/)).toBeInTheDocument();
    expect(screen.getByText(/2025-07-14T12:00:00Z/)).toBeInTheDocument();
  });

  it('shows multiple alerts in order (newest first)', async () => {
    render(<ViolationAlert />);
    const v1 = { type: 'No Vest', location: 'Zone B', timestamp: '2025-07-14T12:01:00Z' };
    const v2 = { type: 'No Gloves', location: 'Zone C', timestamp: '2025-07-14T12:02:00Z' };
    act(() => {
      mockSocket['__cb_violation_alert'](v1);
      mockSocket['__cb_violation_alert'](v2);
    });
    const alertBoxes = screen.getAllByText(/Zone/);
    expect(alertBoxes[0]).toHaveTextContent('Zone C');
    expect(alertBoxes[1]).toHaveTextContent('Zone B');
  });
});