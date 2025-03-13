// Base API URL - Ajustar según donde se esté ejecutando tu API
const API_BASE_URL = "http://localhost:8000/api";

// Interfaces para tipado
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

// Función auxiliar para manejar errores de fetch
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
    
    // En modo desarrollo, podríamos devolver datos de prueba como fallback
    if (process.env.NODE_ENV === "development") {
      console.warn("Using mock data as fallback in development mode");
      return generateMockSimulations();
    }
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
    
    // En modo desarrollo, podríamos devolver datos de prueba como fallback
    if (process.env.NODE_ENV === "development") {
      console.warn("Using mock data as fallback in development mode");
      return getMockSimulation(id);
    }
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
    
    // URL directa a la imagen - allow ECDF and boxen variations
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
    // URL directa a la imagen
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
    
    // En modo desarrollo, podríamos devolver datos de prueba como fallback
    if (process.env.NODE_ENV === "development") {
      console.warn("Using mock data as fallback in development mode");
      return getMockStats();
    }
    throw error;
  }
};

// ----------------------
// Funciones auxiliares para datos de prueba (fallback)
// ----------------------

const randomInRange = (min: number, max: number) => Math.floor(Math.random() * (max - min + 1)) + min;

// Generate mock simulation data
const generateMockSimulations = (): Simulation[] => {
  const simulations = [];

  // Generate 10 mock simulations
  for (let i = 0; i < 10; i++) {
    const date = new Date();
    date.setDate(date.getDate() - i * 3); // Space them out by 3 days

    const id = `${date.toISOString().split("T")[0].replace(/-/g, "")}_${randomInRange(10, 99)}_DAS`;

    simulations.push({
      id,
      date: date.toISOString(),
      parameters: {
        numberNodes: {
          min: 128,
          max: 512,
          step: 128,
        },
        failureRate: {
          min: 40,
          max: 80,
          step: 10,
        },
        blockSize: {
          value: 64,
          options: [32, 64, 128],
        },
        netDegree: {
          value: 8,
          options: [4, 8, 16],
        },
        chi: {
          value: 2,
          options: [1, 2, 3, 4],
        },
        maliciousNodes: {
          value: 0,
          options: [0, 20, 40, 60],
        },
        run: {
          max: 2,
        },
      },
      successRate: randomInRange(30, 95),
      avgMissingSamples: randomInRange(5, 40),
      avgNodesReady: randomInRange(60, 95),
    });
  }

  return simulations;
};

// Get mock simulation by ID
const getMockSimulation = (id: string): Simulation => {
  return {
    id,
    date: new Date().toISOString(),
    parameters: {
      numberNodes: { min: 128, max: 512, step: 128 },
      failureRate: { min: 40, max: 80, step: 10 },
      blockSize: { value: 64, options: [32, 64, 128] },
      netDegree: { value: 8, options: [4, 8, 16] },
      chi: { value: 2, options: [1, 2, 3, 4] },
      maliciousNodes: { value: 0, options: [0, 20, 40, 60] },
      run: { max: 2 },
    },
    successRate: 75,
    avgMissingSamples: 20,
    avgNodesReady: 80,
  };
};

// Get mock statistics
const getMockStats = () => {
  const generateStatData = (prefix: string, count: number) => {
    return Array.from({ length: count }, (_, i) => ({
      name: `${prefix}${i === 0 ? 128 : i === 1 ? 256 : i === 2 ? 384 : 512}`,
      value: randomInRange(10, 90),
    }));
  };

  const generateComparisonData = (prefix: string, count: number) => {
    return Array.from({ length: count }, (_, i) => ({
      name: `${prefix}${i === 0 ? 128 : i === 1 ? 256 : i === 2 ? 384 : 512}`,
      missingSamples: randomInRange(5, 40),
      nodesReady: randomInRange(60, 95),
      sentData: randomInRange(20, 100),
      recvData: randomInRange(15, 90),
    }));
  };

  return {
    byNodes: {
      missingSamples: generateStatData("Nodes: ", 4),
      nodesReady: generateStatData("Nodes: ", 4),
      sentData: generateStatData("Nodes: ", 4),
      comparison: generateComparisonData("Nodes: ", 4),
    },
    byFailureRate: {
      missingSamples: generateStatData("Failure: ", 5),
      nodesReady: generateStatData("Failure: ", 5),
      sentData: generateStatData("Failure: ", 5),
      comparison: generateComparisonData("Failure: ", 5),
    },
    byChi: {
      missingSamples: generateStatData("Chi: ", 4),
      nodesReady: generateStatData("Chi: ", 4),
      sentData: generateStatData("Chi: ", 4),
      comparison: generateComparisonData("Chi: ", 4),
    },
  };
};