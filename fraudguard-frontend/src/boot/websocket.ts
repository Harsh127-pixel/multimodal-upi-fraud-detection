import { boot } from 'quasar/wrappers';
import { useFraudStore } from 'src/stores/fraudStore';

let socket: WebSocket | null = null;
let reconnectAttempts = 0;
const maxReconnectAttempts = 5;

const connect = (userId: string) => {
  if (reconnectAttempts >= maxReconnectAttempts) {
    console.error('WebSocket: Max reconnect attempts reached');
    return;
  }

  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  // Standardizing on localhost:8000 for development as requested
  const wsUrl = `${protocol}//localhost:8000/ws/alerts/${encodeURIComponent(userId)}`;
  
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
    console.warn('WebSocket: Disconnected');
    reconnectAttempts++;
    setTimeout(() => connect(userId), 3000);
  };

  socket.onerror = (error) => {
    console.error('WebSocket: Error', error);
  };
};

export const disconnect = () => {
  if (socket) {
    socket.close();
    socket = null;
  }
};

export default boot(async () => {
  // Use email as ID for now matching the verification curl
  const userId = 'me@upi';
  connect(userId);
});
