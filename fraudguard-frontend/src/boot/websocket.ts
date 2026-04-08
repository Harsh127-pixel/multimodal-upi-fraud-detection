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

  // Derive WS URL from the API_URL environment variable
  const apiUrl = process.env.API_URL || 'http://localhost:8000/api'
  const wsBase = apiUrl.replace('http://', 'ws://').replace('https://', 'wss://').replace('/api', '')
  const wsUrl = `${wsBase}/ws/alerts/${encodeURIComponent(userId)}`
  
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
