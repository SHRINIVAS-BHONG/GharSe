import { api } from '../api/client';

let keepAliveTimer = null;

/**
 * Initializes a 5-minute background ping system to keep the
 * Render backend awake and prevent the 15-minute free-tier inactivity shutdown.
 */
export function initKeepAlive(intervalMinutes = 5) {
  if (keepAliveTimer) return;

  const ping = async () => {
    try {
      await api.get('/health');
    } catch {
      // Non-blocking background heartbeat
    }
  };

  // Immediate ping when the user returns/focuses the tab
  if (typeof document !== 'undefined') {
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'visible') {
        ping();
      }
    });
  }

  // Periodic heartbeat every 5 minutes (300,000ms)
  const ms = intervalMinutes * 60 * 1000;
  keepAliveTimer = setInterval(ping, ms);

  // Trigger initial keepalive ping
  setTimeout(ping, 1500);
}

