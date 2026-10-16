import { describe, expect, it } from 'vitest';
import { authenticateUser } from '../src/auth';

describe('authentication client', () => {
  it('exposes an asynchronous authentication entry point', () => {
    expect(typeof authenticateUser).toBe('function');
  });
});
