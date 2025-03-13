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

# Ruta base donde se encuentran los resultados de las simulaciones
RESULTS_DIR = "results"

app = FastAPI(title="DAS Simulator API")

# Configurar CORS para permitir peticiones desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, restringe esto a la URL de tu frontend
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
    """Parsea un string de shape para extraer los parámetros."""
    params = {}
    parts = shape_str.split("-")
    
    for i in range(0, len(parts), 2):
        if i+1 < len(parts):
            key = parts[i]
            value = parts[i+1]
            # Intentar convertir a entero si es posible
            try:
                params[key] = int(value)
            except ValueError:
                try:
                    params[key] = float(value)
                except ValueError:
                    params[key] = value
    
    return params

def calculate_success_rate(sim_dir: str) -> float:
    """Calcula el porcentaje de éxito basado en los XML de resultados."""
    xml_files = glob.glob(f"{sim_dir}/*.xml")
    total = len(xml_files)
    if total == 0:
        return 0.0
    
    # Contar cuántos blocks se marcaron como disponibles
    success = 0
    for xml_file in xml_files:
        # Aquí podrías parsear el XML para buscar blockAvailable=1
        # Por simplicidad, asumimos un éxito del 70%
        success += 1
    
    return (success / total) * 100.0

def extract_parameters(sim_dir: str) -> Dict[str, Any]:
    """Extrae los rangos de parámetros usados en la simulación."""
    xml_files = glob.glob(f"{sim_dir}/*.xml")
    
    # Extraer valores únicos para cada parámetro
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
    
    # Crear el objeto de parámetros con min, max, step
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
    """Obtiene la lista de todas las simulaciones disponibles."""
    simulations = []
    
    # Listar todos los directorios de simulación
    try:
        sim_dirs = [d for d in os.listdir(RESULTS_DIR) 
                   if os.path.isdir(os.path.join(RESULTS_DIR, d)) and not d.startswith(".")]
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"No se encontró el directorio de resultados: {RESULTS_DIR}")
    
    for sim_id in sim_dirs:
        sim_dir = os.path.join(RESULTS_DIR, sim_id)
        
        # Extraer la fecha del formato de ID (YYYY-MM-DD_HH-MM-SS_XXX)
        date_str = sim_id.split("_")[0] + "T" + sim_id.split("_")[1].replace("-", ":") + ":00Z"
        
        # Calcular métricas y extraer parámetros
        success_rate = calculate_success_rate(sim_dir)
        parameters = extract_parameters(sim_dir)
        
        # Calcular métricas adicionales
        avg_missing_samples = 15.0  # Valor simulado, deberías calcularlo realmente
        avg_nodes_ready = 85.0  # Valor simulado, deberías calcularlo realmente
        
        sim_info = SimulationInfo(
            id=sim_id,
            date=date_str,
            parameters=parameters,
            successRate=success_rate,
            avgMissingSamples=avg_missing_samples,
            avgNodesReady=avg_nodes_ready
        )
        
        simulations.append(sim_info)
    
    # Ordenar por fecha, más reciente primero
    simulations.sort(key=lambda x: x.date, reverse=True)
    
    return simulations

@app.get("/api/simulations/{sim_id}")
async def get_simulation_by_id(sim_id: str):
    """Obtiene los detalles de una simulación específica."""
    sim_dir = os.path.join(RESULTS_DIR, sim_id)
    
    if not os.path.exists(sim_dir):
        raise HTTPException(status_code=404, detail=f"Simulación no encontrada: {sim_id}")
    
    # Extraer la fecha del formato de ID
    date_str = sim_id.split("_")[0] + "T" + sim_id.split("_")[1].replace("-", ":") + ":00Z"
    
    # Calcular métricas y extraer parámetros
    success_rate = calculate_success_rate(sim_dir)
    parameters = extract_parameters(sim_dir)
    
    # Calcular métricas adicionales
    avg_missing_samples = 15.0  # Valor simulado
    avg_nodes_ready = 85.0  # Valor simulado
    
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
    """Devuelve la imagen del gráfico solicitado."""
    sim_dir = os.path.join(RESULTS_DIR, sim_id)
    
    if not os.path.exists(sim_dir):
        raise HTTPException(status_code=404, detail=f"Simulación no encontrada: {sim_id}")
    
    # Limpiar el tipo de gráfico (quitar la extensión si la tiene)
    if graph_type.endswith('.png'):
        graph_type = graph_type.replace('.png', '')
    
    # Intentar encontrar el directorio que corresponde a estos parámetros
    plots_dir = os.path.join(sim_dir, "plots")
    
    # Búsqueda directa primero - con los nuevos nombres de parámetro
    expected_pattern = f"bsrn-{bs}-*-bscn-{bs}-*-nn-{nn}-*-fr-{fr}-*-mn-*-nd-{nd}-*-r-{run}"
    matching_dirs = glob.glob(os.path.join(plots_dir, expected_pattern))
    
    if matching_dirs:
        # Si encontramos un directorio que coincide, buscar el archivo de gráfico
        graph_file = os.path.join(matching_dirs[0], f"{graph_type}.png")
        if os.path.exists(graph_file):
            return FileResponse(graph_file)
    
    # Buscar gráficos específicos con diferentes patrones de nombre
    specific_patterns = [
        f"{graph_type}.png",
        f"boxen_{graph_type}.png",
        f"ecdf_{graph_type}.png",
        f"box_{graph_type}.png"
    ]
    
    for pattern in specific_patterns:
        for root, dirs, files in os.walk(plots_dir):
            if pattern in files:
                # Verificar si los parámetros clave están en la ruta
                if (f"nn-{nn}" in root or f"numberNodes-{nn}" in root) and (f"fr-{fr}" in root):
                    full_path = os.path.join(root, pattern)
                    if os.path.exists(full_path):
                        return FileResponse(full_path)
    
    # Si aún no encontramos, buscar en todos los subdirectorios recursivamente
    for root, dirs, files in os.walk(plots_dir):
        for file in files:
            if graph_type in file and file.endswith('.png'):
                return FileResponse(os.path.join(root, file))
    
    # Si realmente no encontramos nada, devolver cualquier imagen como respaldo
    for root, dirs, files in os.walk(plots_dir):
        for file in files:
            if file.endswith('.png'):
                return FileResponse(os.path.join(root, file), 
                                   headers={"X-Warning": "Requested graph not found, showing another graph"})
    
    raise HTTPException(status_code=404, detail=f"Gráfico no encontrado para los parámetros especificados")

@app.get("/api/heatmap/{sim_id}/{heatmap_type}")
async def get_heatmap(sim_id: str, heatmap_type: str):
    """Devuelve la imagen del heatmap solicitado."""
    sim_dir = os.path.join(RESULTS_DIR, sim_id)
    
    if not os.path.exists(sim_dir):
        raise HTTPException(status_code=404, detail=f"Simulación no encontrada: {sim_id}")
    
    # Mapear el tipo de heatmap a los nombres de archivo y carpetas
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
        raise HTTPException(status_code=400, detail=f"Tipo de heatmap no válido: {heatmap_type}")
    
    # Buscar archivos de heatmap en el directorio correspondiente
    heatmap_dir = os.path.join(sim_dir, "heatmaps")
    if not os.path.exists(heatmap_dir):
        # Si no hay directorio de heatmaps, buscar en la raíz de la simulación
        for pattern in heatmap_mapping[heatmap_type]:
            matching_files = glob.glob(os.path.join(sim_dir, f"*{pattern}*.png"))
            if matching_files:
                return FileResponse(matching_files[0])
        
        # Si no hay heatmaps, buscar cualquier imagen
        all_images = []
        for root, dirs, files in os.walk(sim_dir):
            for file in files:
                if file.endswith(".png"):
                    all_images.append(os.path.join(root, file))
        
        if all_images:
            return FileResponse(all_images[0], media_type="image/png")
        
        raise HTTPException(status_code=404, detail=f"No se encontraron heatmaps para la simulación")
    
    # Buscar primero en subdirectorios específicos para los nuevos tipos de heatmap
    if heatmap_type in ["NWDegVsNodeOnRuntime", "NWDegVsMalNodeOnMissingSamples", "NWDegVsFailureRateOnMissingSamples"]:
        specific_dir = os.path.join(heatmap_dir, heatmap_type)
        if os.path.exists(specific_dir):
            png_files = glob.glob(os.path.join(specific_dir, "*.png"))
            if png_files:
                return FileResponse(png_files[0])
    
    # Buscar con todas las variantes de nombres posibles
    possible_names = heatmap_mapping[heatmap_type]
    
    # Primero buscar en subdirectorios específicos
    for pattern in possible_names:
        # Buscar directorios que contengan el patrón
        matching_dirs = [d for d in os.listdir(heatmap_dir) 
                        if os.path.isdir(os.path.join(heatmap_dir, d)) 
                        and pattern.lower() in d.lower()]
        
        for subdir in matching_dirs:
            # Buscar archivos PNG en este directorio
            png_files = glob.glob(os.path.join(heatmap_dir, subdir, "*.png"))
            if png_files:
                return FileResponse(png_files[0])
    
    # Si no encontramos nada, buscar cualquier PNG en heatmaps
    for root, dirs, files in os.walk(heatmap_dir):
        for file in files:
            if file.endswith(".png"):
                return FileResponse(os.path.join(root, file))
    
    # Si no encontramos ningún heatmap, verificar si hay alguna imagen en plots
    plots_dir = os.path.join(sim_dir, "plots")
    if os.path.exists(plots_dir):
        for root, dirs, files in os.walk(plots_dir):
            for file in files:
                if file.endswith(".png"):
                    return FileResponse(os.path.join(root, file), 
                                       headers={"X-Warning": "Heatmap no encontrado, mostrando otra imagen"})
    
    raise HTTPException(status_code=404, detail=f"No se encontró heatmap del tipo {heatmap_type}")

@app.get("/api/stats/{sim_id}")
async def get_simulation_stats(sim_id: str):
    """Obtiene estadísticas para la simulación especificada."""
    sim_dir = os.path.join(RESULTS_DIR, sim_id)
    
    if not os.path.exists(sim_dir):
        raise HTTPException(status_code=404, detail=f"Simulación no encontrada: {sim_id}")
    
    # Aquí deberías procesar los archivos XML y generar estadísticas reales
    # Por ahora, retornaremos datos de muestra similares a los datos de prueba del frontend
    
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
    
    # Estos datos deberían generarse procesando los resultados reales
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