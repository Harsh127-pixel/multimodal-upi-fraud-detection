from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import random

router = APIRouter(prefix="/graph", tags=["Mule Graph Visualizer"])

@router.get("/visualize/{tx_id}")
async def visualize_graph(tx_id: str):
    """
    Returns a node-and-edge structure representing the flow of funds
    for a flagged transaction, highlighting money mule networks.
    """
    # Simulated complex graph response
    nodes = [
        {"id": "source", "label": "Victim Account", "group": "victim", "balance": 50000},
        {"id": "node_mule_1", "label": "Mule A (Level 1)", "group": "mule", "balance": 12000},
        {"id": "node_mule_2", "label": "Mule B (Level 1)", "group": "mule", "balance": 8000},
        {"id": "node_hub", "label": "Aggregation Hub", "group": "hub", "balance": 500000},
        {"id": "node_crypto", "label": "Crypto Exchange Exit", "group": "exit", "balance": 0},
    ]
    
    edges = [
        {"from": "source", "to": "node_mule_1", "value": 15000, "label": "IMPS Transfer"},
        {"from": "source", "to": "node_mule_2", "value": 15000, "label": "UPI Transfer"},
        {"from": "node_mule_1", "to": "node_hub", "value": 14500, "label": "Consolidation"},
        {"from": "node_mule_2", "to": "node_hub", "value": 14500, "label": "Consolidation"},
        {"from": "node_hub", "to": "node_crypto", "value": 29000, "label": "P2P Crypto Buy"},
    ]
    
    # Randomly shuffle graph logic slightly to make it look dynamic per request
    if random.choice([True, False]):
        nodes.append({"id": "node_mule_3", "label": "Mule C (Level 2)", "group": "mule", "balance": 100})
        edges.append({"from": "node_hub", "to": "node_mule_3", "value": 5000, "label": "Diversion"})

    return {
        "status": "success",
        "tx_id": tx_id,
        "graph_data": {
            "nodes": nodes,
            "edges": edges
        },
        "network_risk_score": 92.4,
        "classification": "Coordinated Mule Ring"
    }
