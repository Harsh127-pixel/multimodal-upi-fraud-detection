import { boot } from 'quasar/wrappers';
import { useFraudStore } from 'src/stores/fraudStore';

let socket: WebSocket | null = null;
let reconnectAttempts = 0;
const maxReconnectAttempts = 5;

export const connectWebSocket = (userId: string) => {
  if (reconnectAttempts >= maxReconnectAttempts) {
    console.error('WebSocket: Max reconnect attempts reached');
    return;
  }

  // Disconnect existing if any
  disconnect();

  const isProd = process.env.NODE_ENV === 'production'
  const wsUrl = isProd
    ? `wss://fraudguard-api.harshbhojwani.in/ws/alerts/${encodeURIComponent(userId)}`
    : `ws://127.0.0.1:8000/ws/alerts/${encodeURIComponent(userId)}`
  
  socket = new WebSocket(wsUrl);

  socket.onopen = () => {
    console.log('WebSocket: Connected to alerts stream');
    reconnectAttempts = 0;
  };

  socket.onmessage = (event) => {
    try {
      const alert = JSON.parse(event.data);
      const fraudStore = useFraudStore();
      fraudStore.addAlert(alert);
    } catch (e) {
      console.error('WebSocket: Failed to parse alert message', e);
    }
  };

  socket.onclose = () => {
    if (socket) {
      console.warn('WebSocket: Disconnected, retrying...');
      reconnectAttempts++;
      setTimeout(() => connectWebSocket(userId), 3000);
    }
  };

  socket.onerror = (error) => {
    console.error('WebSocket: Error', error);
  };
};

export const disconnect = () => {
  if (socket) {
    const s = socket;
    socket = null; // Set to null before closing to prevent onclose retry
    s.close();
  }
};

export default boot(() => {
  // We no longer connect automatically on boot.
  // Connection is handled by MainLayout when user is authenticated.
});
