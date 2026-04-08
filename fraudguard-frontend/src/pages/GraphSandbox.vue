<template>
  <q-page class="page-wrapper">
    <div class="header-section fade-up fade-up-1">
      <div class="row items-center justify-between">
        <div>
          <div class="page-title sora">Mule-Account Graph Visualizer</div>
          <div class="page-subtitle">Interactive tracing of illicit financial flows</div>
        </div>
        <q-btn color="primary" icon="refresh" label="Regenerate Traces" @click="fetchGraph" outline class="mono" />
      </div>
    </div>

    <div class="graph-container fg-card fade-up fade-up-2">
      <div class="canvas-wrap">
        <div v-if="loading" class="row justify-center items-center full-height">
          <q-spinner-dots size="40px" color="blue" />
        </div>
        
        <!-- Very Basic D3/SVG Mock Visualization built with raw Vue -->
        <svg v-else class="graph-svg" viewBox="0 0 800 500">
           <!-- Edges -->
           <path v-for="(edge, i) in edges" :key="'e'+i"
                 :d="getEdgePath(edge)" 
                 class="edge-line" />
                 
           <text v-for="(edge, i) in edges" :key="'et'+i"
                 :x="getEdgeMidX(edge)" :y="getEdgeMidY(edge) - 10" 
                 class="edge-label mono">{{ edge.label }} (₹{{ edge.value }})</text>

           <!-- Nodes -->
           <g v-for="node in nodes" :key="node.id" :transform="`translate(${node.x}, ${node.y})`" class="node-group" @click="selectedNode = node">
              <circle r="30" :class="['node-circle', `group-${node.group}`]" />
              <text y="45" text-anchor="middle" class="node-label sora">{{ node.label }}</text>
              <text y="-4" text-anchor="middle" class="node-icon material-icons">{{ getNodeIcon(node.group) }}</text>
           </g>
        </svg>
      </div>
      
      <div class="inspector-panel" v-if="selectedNode">
         <div class="mono text-grey">INSPECTING NODE</div>
         <div class="sora text-h6 q-mt-sm">{{ selectedNode.label }}</div>
         <q-separator dark class="q-my-md" />
         <div class="row align-center q-mb-sm">
           <span class="text-grey-5 col-5">Node ID:</span> 
           <span class="mono">{{ selectedNode.id }}</span>
         </div>
         <div class="row align-center q-mb-sm">
           <span class="text-grey-5 col-5">Role Type:</span> 
           <span class="text-capitalize">{{ selectedNode.group }}</span>
         </div>
         <div class="row align-center q-mb-sm">
           <span class="text-grey-5 col-5">Balance:</span> 
           <span class="mono">₹{{ selectedNode.balance }}</span>
         </div>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { api } from 'src/boot/axios'
import { useQuasar } from 'quasar'

const $q = useQuasar()
const loading = ref(true)

interface GraphNode {
  id: string; label: string; group: string; balance: number;
  x?: number; y?: number; // assigned by layout
}

interface GraphEdge {
  from: string; to: string; value: number; label: string;
}

const nodes = ref<GraphNode[]>([])
const edges = ref<GraphEdge[]>([])
const selectedNode = ref<GraphNode | null>(null)

// Very basic manual layout mapping for demo purposes
const manualLayout: Record<string, {x:number, y:number}> = {
  'source': {x: 100, y: 250},
  'node_mule_1': {x: 350, y: 150},
  'node_mule_2': {x: 350, y: 350},
  'node_mule_3': {x: 550, y: 400},
  'node_hub': {x: 550, y: 250},
  'node_crypto': {x: 750, y: 250}
}

function getNodeIcon(group: string) {
  if (group === 'victim') return 'person'
  if (group === 'mule') return 'masks'
  if (group === 'hub') return 'account_balance'
  return 'currency_bitcoin'
}

function getEdgePath(edge: GraphEdge) {
  const n1 = nodes.value.find(n => n.id === edge.from)
  const n2 = nodes.value.find(n => n.id === edge.to)
  if (!n1 || !n2 || !n1.x || !n1.y || !n2.x || !n2.y) return ''
  return `M ${n1.x} ${n1.y} L ${n2.x} ${n2.y}`
}

function getEdgeMidX(edge: GraphEdge) {
  const n1 = nodes.value.find(n => n.id === edge.from)
  const n2 = nodes.value.find(n => n.id === edge.to)
  return ((n1?.x || 0) + (n2?.x || 0)) / 2
}

function getEdgeMidY(edge: GraphEdge) {
  const n1 = nodes.value.find(n => n.id === edge.from)
  const n2 = nodes.value.find(n => n.id === edge.to)
  return ((n1?.y || 0) + (n2?.y || 0)) / 2
}

async function fetchGraph() {
  loading.value = true
  selectedNode.value = null
  try {
    const res = await api.get('/graph/visualize/TX-RAND')
    const rawNodes = res.data.graph_data.nodes as GraphNode[]
    nodes.value = rawNodes.map(n => ({ ...n, ...manualLayout[n.id] }))
    edges.value = res.data.graph_data.edges
  } catch {
    $q.notify({color:'negative', message: 'Failed to load graph data'})
  } finally {
    loading.value = false
  }
}

onMounted(fetchGraph)
</script>

<style scoped lang="scss">
.page-wrapper {
  padding: 32px;
  max-width: 1200px;
  margin: 0 auto;
}

.graph-container {
  height: 600px;
  margin-top: 30px;
  background: var(--fg-surface-dark);
  position: relative;
  overflow: hidden;
  display: flex;
}

.canvas-wrap {
  flex: 1;
  background-image: 
    linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
  background-size: 30px 30px;
  position: relative;
}

.graph-svg {
  width: 100%;
  height: 100%;
}

.node-group {
  cursor: pointer;
  transition: transform 0.2s;
  &:hover {
     transform: scale(1.05); /* Needs proper svg origin mapping for prod, but mock hover is fine */
  }
}

.node-circle {
  fill: #1A2238;
  stroke-width: 3px;
  
  &.group-victim { stroke: #3b82f6; fill: rgba(59, 130, 246, 0.2); }
  &.group-mule { stroke: #ef4444; fill: rgba(239, 68, 68, 0.2); }
  &.group-hub { stroke: #f59e0b; fill: rgba(245, 158, 11, 0.2); }
  &.group-exit { stroke: #10b981; fill: rgba(16, 185, 129, 0.2); }
}

.node-icon {
  fill: white;
  font-size: 24px;
}

.node-label {
  fill: var(--fg-text-primary);
  font-size: 13px;
  font-weight: 500;
}

.edge-line {
  stroke: rgba(255,255,255,0.2);
  stroke-width: 2px;
  fill: none;
  stroke-dasharray: 4,4;
  animation: dash 20s linear infinite;
}

.edge-label {
  fill: var(--fg-text-secondary);
  font-size: 11px;
  text-anchor: middle;
}

@keyframes dash {
  to {
    stroke-dashoffset: -200;
  }
}

.inspector-panel {
  width: 300px;
  border-left: 1px solid var(--fg-border);
  background: var(--fg-surface);
  padding: 24px;
}
</style>
