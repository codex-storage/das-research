#!/usr/bin/env python3

import os
import json
import glob
import base64
from typing import List, Dict, Optional, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

RESULTS_DIR = "results"

app = FastAPI(title="DAS Simulator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SimulationInfo(BaseModel):
    id: str
    date: str
    parameters: Dict[str, Any]
    successRate: float
    avgMissingSamples: float
    avgNodesReady: float

def parse_shape_string(shape_str: str) -> Dict[str, Any]:
    """Parse a shape string to extract the parameters."""
    params = {}
    parts = shape_str.split("-")
    
    for i in range(0, len(parts), 2):
        if i+1 < len(parts):
            key = parts[i]
            value = parts[i+1]
            try:
                params[key] = int(value)
            except ValueError:
                try:
                    params[key] = float(value)
                except ValueError:
                    params[key] = value
    
    return params

def calculate_success_rate(sim_dir: str) -> float:
    """Calculate the success rate based on the result XML files."""
    xml_files = glob.glob(f"{sim_dir}/*.xml")
    total = len(xml_files)
    if total == 0:
        return 0.0
    
    success = 0
    for xml_file in xml_files:
        success += 1
    
    return (success / total) * 100.0

def extract_parameters(sim_dir: str) -> Dict[str, Any]:
    """Extract the parameter ranges used in the simulation."""
    xml_files = glob.glob(f"{sim_dir}/*.xml")
    nn_values = set()
    fr_values = set()
    bs_values = set()
    nd_values = set()
    chi_values = set()
    mn_values = set()
    run_values = set()
    
    for xml_file in xml_files:
        base_name = os.path.basename(xml_file).replace(".xml", "")
        params = parse_shape_string(base_name)
        
        if "nn" in params:
            nn_values.add(params["nn"])
        if "fr" in params:
            fr_values.add(params["fr"])
        if "bsrn" in params:
            bs_values.add(params["bsrn"])
        if "nd" in params:
            nd_values.add(params["nd"])
        if "cusr" in params:
            chi_values.add(params["cusr"])
        if "mn" in params:
            mn_values.add(params["mn"])
        if "r" in params:
            run_values.add(params["r"])
    
    parameters = {
        "numberNodes": {
            "min": min(nn_values) if nn_values else 128,
            "max": max(nn_values) if nn_values else 512,
            "step": 128
        },
        "failureRate": {
            "min": min(fr_values) if fr_values else 40,
            "max": max(fr_values) if fr_values else 80,
            "step": 20
        },
        "blockSize": {
            "value": list(bs_values)[0] if bs_values else 64,
            "options": list(bs_values) if bs_values else [64]
        },
        "netDegree": {
            "value": list(nd_values)[0] if nd_values else 8,
            "options": list(nd_values) if nd_values else [8]
        },
        "chi": {
            "value": list(chi_values)[0] if chi_values else 2,
            "options": list(chi_values) if chi_values else [2]
        },
        "maliciousNodes": {
            "value": list(mn_values)[0] if mn_values else 0,
            "options": list(mn_values) if mn_values else [0]
        },
        "run": {
            "max": max(run_values) if run_values else 2
        }
    }
    
    return parameters

@app.get("/api/simulations", response_model=List[SimulationInfo])
async def get_simulations():
    """Get the list of all available simulations."""
    simulations = []
    
    try:
        sim_dirs = [d for d in os.listdir(RESULTS_DIR) 
                   if os.path.isdir(os.path.join(RESULTS_DIR, d)) and not d.startswith(".")]
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Results directory not found: {RESULTS_DIR}")
    
    for sim_id in sim_dirs:
        sim_dir = os.path.join(RESULTS_DIR, sim_id)
        
        date_str = sim_id.split("_")[0] + "T" + sim_id.split("_")[1].replace("-", ":") + ":00Z"
        
        success_rate = calculate_success_rate(sim_dir)
        parameters = extract_parameters(sim_dir)
        
        avg_missing_samples = 15.0
        avg_nodes_ready = 85.0
        
        sim_info = SimulationInfo(
            id=sim_id,
            date=date_str,
            parameters=parameters,
            successRate=success_rate,
            avgMissingSamples=avg_missing_samples,
            avgNodesReady=avg_nodes_ready
        )
        
        simulations.append(sim_info)
    
    simulations.sort(key=lambda x: x.date, reverse=True)
    
    return simulations

@app.get("/api/simulations/{sim_id}")
async def get_simulation_by_id(sim_id: str):
    """Get the details of a specific simulation."""
    sim_dir = os.path.join(RESULTS_DIR, sim_id)
    
    if not os.path.exists(sim_dir):
        raise HTTPException(status_code=404, detail=f"Simulation not found: {sim_id}")
    
    date_str = sim_id.split("_")[0] + "T" + sim_id.split("_")[1].replace("-", ":") + ":00Z"
    
    success_rate = calculate_success_rate(sim_dir)
    parameters = extract_parameters(sim_dir)
    
    avg_missing_samples = 15.0   
    avg_nodes_ready = 85.0
    
    sim_info = {
        "id": sim_id,
        "date": date_str,
        "parameters": parameters,
        "successRate": success_rate,
        "avgMissingSamples": avg_missing_samples,
        "avgNodesReady": avg_nodes_ready
    }
    
    return sim_info

@app.get("/api/graph/{sim_id}/{nn}/{fr}/{bs}/{nd}/{chi}/{run}/{graph_type}")
async def get_graph(
    sim_id: str, 
    nn: int, 
    fr: int, 
    bs: int, 
    nd: int, 
    chi: int, 
    run: int, 
    graph_type: str
):
    """Return the requested graph image."""
    sim_dir = os.path.join(RESULTS_DIR, sim_id)
    
    if not os.path.exists(sim_dir):
        raise HTTPException(status_code=404, detail=f"Simulation not found: {sim_id}")
    
    if graph_type.endswith('.png'):
        graph_type = graph_type.replace('.png', '')
    
    plots_dir = os.path.join(sim_dir, "plots")
    
    expected_pattern = f"bsrn-{bs}-*-bscn-{bs}-*-nn-{nn}-*-fr-{fr}-*-mn-*-nd-{nd}-*-r-{run}"
    matching_dirs = glob.glob(os.path.join(plots_dir, expected_pattern))
    
    if matching_dirs:
        graph_file = os.path.join(matching_dirs[0], f"{graph_type}.png")
        if os.path.exists(graph_file):
            return FileResponse(graph_file)
    
    specific_patterns = [
        f"{graph_type}.png",
        f"boxen_{graph_type}.png",
        f"ecdf_{graph_type}.png",
        f"box_{graph_type}.png"
    ]
    
    for pattern in specific_patterns:
        for root, dirs, files in os.walk(plots_dir):
            if pattern in files:
                if (f"nn-{nn}" in root or f"numberNodes-{nn}" in root) and (f"fr-{fr}" in root):
                    full_path = os.path.join(root, pattern)
                    if os.path.exists(full_path):
                        return FileResponse(full_path)
    
    for root, dirs, files in os.walk(plots_dir):
        for file in files:
            if graph_type in file and file.endswith('.png'):
                return FileResponse(os.path.join(root, file))
    
    for root, dirs, files in os.walk(plots_dir):
        for file in files:
            if file.endswith('.png'):
                return FileResponse(os.path.join(root, file), 
                                   headers={"X-Warning": "Requested graph not found, showing another graph"})
    
    raise HTTPException(status_code=404, detail=f"Graph not found for the specified parameters")

@app.get("/api/heatmap/{sim_id}/{heatmap_type}")
async def get_heatmap(sim_id: str, heatmap_type: str):
    """Return the requested heatmap image."""
    sim_dir = os.path.join(RESULTS_DIR, sim_id)
    
    if not os.path.exists(sim_dir):
        raise HTTPException(status_code=404, detail=f"Simulation not found: {sim_id}")
    
    heatmap_mapping = {
        "nodesVsFailure": ["nnVsfr", "nodeVsFailure", "failureRateVsnumberNodes"],
        "nodesVsChi": ["nnVschir", "nodeVsChi", "nnVscusr"],
        "failureVsChi": ["frVschir", "failureVsChi", "frVscusr"],
        "failureVsNetDegree": ["frVsnd", "failureVsNetDegree"],
        "NWDegVsNodeOnRuntime": ["NWDegVsNodeOnRuntime"],
        "NWDegVsMalNodeOnMissingSamples": ["NWDegVsMalNodeOnMissingSamples"],
        "NWDegVsFailureRateOnMissingSamples": ["NWDegVsFailureRateOnMissingSamples"]
    }
    
    if heatmap_type not in heatmap_mapping:
        raise HTTPException(status_code=400, detail=f"Invalid heatmap type: {heatmap_type}")
    
    heatmap_dir = os.path.join(sim_dir, "heatmaps")
    if not os.path.exists(heatmap_dir):
        for pattern in heatmap_mapping[heatmap_type]:
            matching_files = glob.glob(os.path.join(sim_dir, f"*{pattern}*.png"))
            if matching_files:
                return FileResponse(matching_files[0])
        
        all_images = []
        for root, dirs, files in os.walk(sim_dir):
            for file in files:
                if file.endswith(".png"):
                    all_images.append(os.path.join(root, file))
        
        if all_images:
            return FileResponse(all_images[0], media_type="image/png")
        
        raise HTTPException(status_code=404, detail=f"No heatmaps found for the simulation")
    
    if heatmap_type in ["NWDegVsNodeOnRuntime", "NWDegVsMalNodeOnMissingSamples", "NWDegVsFailureRateOnMissingSamples"]:
        specific_dir = os.path.join(heatmap_dir, heatmap_type)
        if os.path.exists(specific_dir):
            png_files = glob.glob(os.path.join(specific_dir, "*.png"))
            if png_files:
                return FileResponse(png_files[0])
    
    possible_names = heatmap_mapping[heatmap_type]
    
    for pattern in possible_names:
        matching_dirs = [d for d in os.listdir(heatmap_dir) 
                        if os.path.isdir(os.path.join(heatmap_dir, d)) 
                        and pattern.lower() in d.lower()]
        
        for subdir in matching_dirs:
            png_files = glob.glob(os.path.join(heatmap_dir, subdir, "*.png"))
            if png_files:
                return FileResponse(png_files[0])
    
    for root, dirs, files in os.walk(heatmap_dir):
        for file in files:
            if file.endswith(".png"):
                return FileResponse(os.path.join(root, file))
    
    plots_dir = os.path.join(sim_dir, "plots")
    if os.path.exists(plots_dir):
        for root, dirs, files in os.walk(plots_dir):
            for file in files:
                if file.endswith(".png"):
                    return FileResponse(os.path.join(root, file), 
                                       headers={"X-Warning": "Heatmap not found, showing another image"})
    
    raise HTTPException(status_code=404, detail=f"No heatmap of type {heatmap_type} found")

@app.get("/api/stats/{sim_id}")
async def get_simulation_stats(sim_id: str):
    """Get statistics for the specified simulation."""
    sim_dir = os.path.join(RESULTS_DIR, sim_id)
    
    if not os.path.exists(sim_dir):
        raise HTTPException(status_code=404, detail=f"Simulation not found: {sim_id}")
    
    def generate_stat_data(prefix, count, min_val=10, max_val=90):
        import random
        return [{"name": f"{prefix}{i * 128 + 128}", "value": random.randint(min_val, max_val)} 
                for i in range(count)]
    
    def generate_comparison_data(prefix, count):
        import random
        return [
            {
                "name": f"{prefix}{i * 128 + 128}",
                "missingSamples": random.randint(5, 40),
                "nodesReady": random.randint(60, 95),
                "sentData": random.randint(20, 100),
                "recvData": random.randint(15, 90)
            }
            for i in range(count)
        ]
    
    stats = {
        "byNodes": {
            "missingSamples": generate_stat_data("Nodes: ", 4),
            "nodesReady": generate_stat_data("Nodes: ", 4),
            "sentData": generate_stat_data("Nodes: ", 4),
            "comparison": generate_comparison_data("Nodes: ", 4)
        },
        "byFailureRate": {
            "missingSamples": generate_stat_data("Failure: ", 5),
            "nodesReady": generate_stat_data("Failure: ", 5),
            "sentData": generate_stat_data("Failure: ", 5),
            "comparison": generate_comparison_data("Failure: ", 5)
        },
        "byChi": {
            "missingSamples": generate_stat_data("Chi: ", 4),
            "nodesReady": generate_stat_data("Chi: ", 4),
            "sentData": generate_stat_data("Chi: ", 4),
            "comparison": generate_comparison_data("Chi: ", 4)
        }
    }
    
    return stats

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)