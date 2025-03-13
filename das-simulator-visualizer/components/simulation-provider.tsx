"use client"

import { createContext, useContext, useState, useEffect, type ReactNode } from "react"
import { fetchSimulations } from "@/lib/simulation-service"

type SimulationContextType = {
  simulations: any[]
  loading: boolean
  error: string | null
  getSimulationById: (id: string) => any
  refreshSimulations: () => Promise<void>
}

const SimulationContext = createContext<SimulationContextType | undefined>(undefined)

export function SimulationProvider({ children }: { children: ReactNode }) {
  const [simulations, setSimulations] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const refreshSimulations = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await fetchSimulations()
      setSimulations(data)
    } catch (err) {
      setError("Failed to fetch simulations")
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const getSimulationById = (id: string) => {
    try {
      const cachedSimulation = simulations.find((sim) => sim.id === id)
      if (cachedSimulation) return cachedSimulation

      return {
        id,
        date: new Date().toISOString(),
        parameters: {
          numberNodes: { min: 128, max: 512, step: 128 },
          failureRate: { min: 40, max: 80, step: 10 },
          blockSize: { value: 64, options: [32, 64, 128] },
          netDegree: { value: 8, options: [4, 8, 16] },
          chi: { value: 2, options: [1, 2, 3, 4] },
          run: { max: 2 },
        },
        successRate: 75,
        avgMissingSamples: 20,
        avgNodesReady: 80,
      }
    } catch (err) {
      console.error("Error getting simulation by ID:", err)
      return {
        id,
        date: new Date().toISOString(),
        parameters: {
          numberNodes: { min: 128, max: 512, step: 128 },
          failureRate: { min: 40, max: 80, step: 10 },
          blockSize: { value: 64, options: [32, 64, 128] },
          netDegree: { value: 8, options: [4, 8, 16] },
          chi: { value: 2, options: [1, 2, 3, 4] },
          run: { max: 2 },
        },
        successRate: 0,
        avgMissingSamples: 0,
        avgNodesReady: 0,
      }
    }
  }

  useEffect(() => {
    refreshSimulations()
  }, [])

  return (
    <SimulationContext.Provider
      value={{
        simulations,
        loading,
        error,
        getSimulationById,
        refreshSimulations,
      }}
    >
      {children}
    </SimulationContext.Provider>
  )
}

export function useSimulation() {
  const context = useContext(SimulationContext)
  if (context === undefined) {
    throw new Error("useSimulation must be used within a SimulationProvider")
  }
  return context
}

