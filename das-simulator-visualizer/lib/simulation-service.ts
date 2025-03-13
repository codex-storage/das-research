// Base API URL - Adjust based on where your API is running
const API_BASE_URL = "http://localhost:8000/api";

interface Simulation {
  id: string;
  date: string;
  parameters: {
    numberNodes: {
      min: number;
      max: number;
      step: number;
    };
    failureRate: {
      min: number;
      max: number;
      step: number;
    };
    blockSize: {
      value: number;
      options: number[];
    };
    netDegree: {
      value: number;
      options: number[];
    };
    chi: {
      value: number;
      options: number[];
    };
    maliciousNodes?: {
      value: number;
      options: number[];
    };
    run: {
      max: number;
    };
  };
  successRate: number;
  avgMissingSamples: number;
  avgNodesReady: number;
}

// Helper function to handle fetch errors
const handleFetchError = (error: any, fallbackMessage: string) => {
  console.error(fallbackMessage, error);
  throw new Error(fallbackMessage);
};

// Fetch all simulations
export const fetchSimulations = async (): Promise<Simulation[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/simulations`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    handleFetchError(error, "Error fetching simulations");
    throw error;
  }
};

// Fetch a specific simulation by ID
export const fetchSimulationById = async (id: string): Promise<Simulation> => {
  try {
    const response = await fetch(`${API_BASE_URL}/simulations/${id}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    handleFetchError(error, `Error fetching simulation with ID: ${id}`);
    
    throw error;
  }
};

// Get URL for a specific graph
export const getGraphUrl = async (
  simulationId: string,
  numberNodes: number,
  failureRate: number,
  blockSize: number,
  netDegree: number,
  chi: number,
  run: number,
  graphType: string,
): Promise<string> => {
  try {
    // Modify the graphType based on the selection to match new file structure
    let modifiedGraphType = graphType;
    
    // Map common graph types to their file names
    const graphTypeMap: Record<string, string> = {
      'missingSamples': 'missingSegments',
      'nodesReady': 'nodesReady',
      'sentData': 'sentData',
      'recvData': 'recvData',
      'dupData': 'dupData',
      'RowColDist': 'RowColDist',
      'restoreRowCount': 'restoreRowCount',
      'restoreColumnCount': 'restoreColumnCount',
      'messagesSent': 'messagesSent',
      'messagesRecv': 'messagesRecv'
    };
    
    if (graphTypeMap[graphType]) {
      modifiedGraphType = graphTypeMap[graphType];
    }
    
    // Direct URL to the image - allow ECDF and boxen variations
    return `${API_BASE_URL}/graph/${simulationId}/${numberNodes}/${failureRate}/${blockSize}/${netDegree}/${chi}/${run}/${modifiedGraphType}`;
  } catch (error) {
    console.error("Error getting graph URL:", error);
    // Fallback to placeholder in development
    return `/placeholder.svg?height=300&width=500&text=${graphType}_n${numberNodes}_f${failureRate}_b${blockSize}_d${netDegree}_c${chi}_r${run}`;
  }
};

// Get URL for a specific heatmap
export const getHeatmapUrl = async (simulationId: string, heatmapType: string): Promise<string> => {
  try {
    // Direct URL to the image
    return `${API_BASE_URL}/heatmap/${simulationId}/${heatmapType}`;
  } catch (error) {
    console.error("Error getting heatmap URL:", error);
    // Fallback to placeholder in development
    return `/placeholder.svg?height=300&width=500&text=Heatmap_${heatmapType}_${simulationId}`;
  }
};

// Get statistics for a simulation
export const getSimulationStats = async (simulationId: string): Promise<any> => {
  try {
    const response = await fetch(`${API_BASE_URL}/stats/${simulationId}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    handleFetchError(error, `Error fetching statistics for simulation: ${simulationId}`);
    throw error;
  }
};