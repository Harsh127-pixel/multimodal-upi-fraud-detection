<script setup>
import { ref } from "vue";

const riskScore = ref(15);
const status = ref("Safe");

const detectionModes = [
  {
    title: "Voice Analysis",
    icon: "🎙️",
    description:
      "Real-time deepfake and impersonation detection in audio calls.",
    status: "Monitoring",
    color: "blue",
  },
  {
    title: "NLP Text Scan",
    icon: "💬",
    description: "Scanning messages for phishing patterns and scam triggers.",
    status: "Active",
    color: "purple",
  },
  {
    title: "UPI Risk Fusion",
    icon: "💳",
    description:
      "Combining behavioral data with transaction history for risk scoring.",
    status: "Ready",
    color: "emerald",
  },
];
</script>

<template>
  <div class="app-container">
    <nav class="navbar animate-fade-in">
      <div class="logo">
        <span class="gradient-text">SafeUPI</span>
      </div>
      <div class="nav-links">
        <a href="#">Dashboard</a>
        <a href="#">Reports</a>
        <a href="#">Settings</a>
      </div>
      <button class="btn-primary">Connect Wallet</button>
    </nav>

    <main class="content">
      <!-- Hero Section -->
      <section class="hero animate-fade-in">
        <h1 class="hero-title">
          Multimodal <span class="gradient-text">Fraud Intelligence</span>
        </h1>
        <p class="hero-subtitle">
          Protecting your UPI transactions with coordinated AI models across
          voice, text, and behavioral data.
        </p>
      </section>

      <!-- Risk Overview -->
      <section class="risk-overview animate-fade-in">
        <div class="glass-card risk-panel">
          <div class="risk-meter">
            <svg viewBox="0 0 100 100" class="circular-chart">
              <path
                class="circle-bg"
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                transform="translate(32, 32)"
              />
              <path
                class="circle"
                :stroke-dasharray="`${riskScore}, 100`"
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                transform="translate(32, 32)"
              />
              <text x="50" y="55" class="percentage">{{ riskScore }}%</text>
            </svg>
          </div>
          <div class="risk-info">
            <h2>Current Risk Profile</h2>
            <p :class="['status-badge', status.toLowerCase()]">{{ status }}</p>
            <p class="info-text">
              System is actively monitoring all channels. No immediate threats
              detected.
            </p>
          </div>
        </div>
      </section>

      <!-- Detection Grid -->
      <section class="detection-grid">
        <div
          v-for="mode in detectionModes"
          :key="mode.title"
          class="glass-card mode-card animate-fade-in"
        >
          <div class="card-icon">{{ mode.icon }}</div>
          <h3>{{ mode.title }}</h3>
          <p>{{ mode.description }}</p>
          <div class="card-footer">
            <span class="status-indicator">
              <span
                class="dot"
                :style="{
                  background:
                    mode.color === 'blue'
                      ? 'var(--primary)'
                      : mode.color === 'purple'
                        ? 'var(--secondary)'
                        : 'var(--success)',
                }"
              ></span>
              {{ mode.status }}
            </span>
            <button class="btn-outline">Analyze</button>
          </div>
        </div>
      </section>
    </main>

    <footer class="footer">
      <p>&copy; 2026 SafeUPI Multimodal Detection. All Rights Reserved.</p>
    </footer>
  </div>
</template>

<style scoped>
.app-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}

.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 2rem 0;
}

.logo {
  font-size: 1.8rem;
  font-weight: 800;
  letter-spacing: -0.05em;
}

.nav-links {
  display: flex;
  gap: 2.5rem;
}

.nav-links a {
  text-decoration: none;
  color: var(--text-muted);
  font-weight: 500;
  transition: color 0.2s;
}

.nav-links a:hover {
  color: var(--text);
}

.content {
  padding-top: 4rem;
}

.hero {
  text-align: center;
  margin-bottom: 6rem;
}

.hero-title {
  font-size: 4.5rem;
  line-height: 1;
  margin-bottom: 1.5rem;
  font-weight: 900;
}

.hero-subtitle {
  font-size: 1.25rem;
  color: var(--text-muted);
  max-width: 600px;
  margin: 0 auto;
}

.risk-overview {
  margin-bottom: 4rem;
}

.risk-panel {
  display: flex;
  align-items: center;
  gap: 3rem;
  background: linear-gradient(
    135deg,
    rgba(30, 41, 59, 1),
    rgba(15, 23, 42, 0.8)
  );
}

.risk-meter {
  width: 200px;
  height: 200px;
}

.circular-chart {
  display: block;
  margin: 10px auto;
  max-width: 100%;
  max-height: 250px;
}

.circle-bg {
  fill: none;
  stroke: rgba(255, 255, 255, 0.05);
  stroke-width: 3;
}

.circle {
  fill: none;
  stroke-width: 3;
  stroke-linecap: round;
  stroke: var(--primary);
  filter: drop-shadow(0 0 5px var(--primary));
  transition: stroke-dasharray 0.3s ease;
}

.percentage {
  fill: var(--text);
  font-size: 0.6rem;
  font-weight: 700;
  text-anchor: middle;
}

.risk-info h2 {
  font-size: 2rem;
  margin-bottom: 1rem;
}

.status-badge {
  display: inline-block;
  padding: 0.25rem 1rem;
  border-radius: 999px;
  font-size: 0.875rem;
  font-weight: 700;
  text-transform: uppercase;
  margin-bottom: 1rem;
}

.status-badge.safe {
  background: rgba(34, 197, 94, 0.1);
  color: var(--success);
  border: 1px solid rgba(34, 197, 94, 0.2);
}

.info-text {
  color: var(--text-muted);
}

.detection-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin-bottom: 6rem;
}

.mode-card {
  display: flex;
  flex-direction: column;
}

.card-icon {
  font-size: 2.5rem;
  margin-bottom: 1.5rem;
}

.mode-card h3 {
  font-size: 1.5rem;
  margin-bottom: 1rem;
}

.mode-card p {
  color: var(--text-muted);
  line-height: 1.6;
  margin-bottom: 2rem;
  flex-grow: 1;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: var(--text-muted);
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  box-shadow: 0 0 10px currentColor;
}

.footer {
  text-align: center;
  padding: 4rem 0;
  color: var(--text-muted);
  border-top: 1px solid var(--border);
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 3rem;
  }
  .risk-panel {
    flex-direction: column;
    text-align: center;
  }
}
</style>
