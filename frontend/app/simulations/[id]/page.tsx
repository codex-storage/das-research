"use client"

import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { ArrowLeft, Download, Maximize } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { SimulationMetadata } from "@/components/simulation-metadata"
import { ParameterSelector } from "@/components/parameter-selector"
import { GraphViewer } from "@/components/graph-viewer"
import { HeatmapViewer } from "@/components/heatmap-viewer"
import { StatisticsSummary } from "@/components/statistics-summary"
import { useSimulation } from "@/components/simulation-provider"
import { Dialog, DialogContent, DialogTrigger } from "@/components/ui/dialog"
import { Skeleton } from "@/components/ui/skeleton"

export default function SimulationDetailPage() {
  const params = useParams()
  const router = useRouter()
  const { getSimulationById, loading } = useSimulation()
  const [simulation, setSimulation] = useState<any>(null)
  const [selectedParams, setSelectedParams] = useState<any>({
    numberNodes: 128,
    failureRate: 40,
    blockSize: 64,
    netDegree: 8,
    chi: 2,
    maliciousNodes: 0,
    run: 0,
  })
  const [graphType, setGraphType] = useState("missingSegments")

  useEffect(() => {
    const fetchSimulation = async () => {
      try {
        if (params.id) {
          const sim = getSimulationById(params.id as string)
          setSimulation(sim)
        }
      } catch (error) {
        console.error("Error fetching simulation:", error)
        // Set a default simulation or handle the error appropriately
        setSimulation(null)
      }
    }

    fetchSimulation()
  }, [params.id, getSimulationById])

  if (loading) {
    return (
      <div className="container py-6 px-4 md:px-6">
        <div className="flex items-center mb-6">
          <Button variant="ghost" size="icon" onClick={() => router.back()}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <Skeleton className="h-8 w-64 ml-2" />
        </div>
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          <Skeleton className="h-[200px] w-full" />
          <Skeleton className="h-[200px] w-full" />
          <Skeleton className="h-[200px] w-full" />
        </div>
      </div>
    )
  }

  if (!simulation) {
    return (
      <div className="container py-6 px-4 md:px-6">
        <div className="flex items-center mb-6">
          <Button variant="ghost" size="icon" onClick={() => router.back()}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <h1 className="text-xl font-semibold ml-2">Simulation not found</h1>
        </div>
        <p>The requested simulation could not be found.</p>
      </div>
    )
  }

  const handleParamChange = (param: string, value: any) => {
    setSelectedParams((prev) => ({
      ...prev,
      [param]: value,
    }))
  }

  const handleGraphTypeChange = (type: string) => {
    setGraphType(type)
  }

  return (
    <div className="container py-6 px-4 md:px-6">
      <div className="flex items-center mb-6">
        <Button variant="ghost" size="icon" onClick={() => router.back()}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <h1 className="text-xl font-semibold ml-2">Simulation: {simulation.id}</h1>
      </div>

      <div className="grid gap-6 md:grid-cols-12">
        {/* Sidebar with metadata and parameter selection */}
        <div className="md:col-span-4 lg:col-span-3 space-y-6">
          <SimulationMetadata simulation={simulation} />
          <ParameterSelector
            parameters={simulation.parameters}
            selectedParams={selectedParams}
            onParamChange={handleParamChange}
          />
        </div>

        {/* Main content area */}
        <div className="md:col-span-8 lg:col-span-9 space-y-6">
          <Tabs defaultValue="graphs" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="graphs">Graphs</TabsTrigger>
              <TabsTrigger value="heatmaps">Heatmaps</TabsTrigger>
              <TabsTrigger value="statistics">Statistics</TabsTrigger>
            </TabsList>

            <TabsContent value="graphs" className="space-y-4">
              <Card>
                <CardHeader className="pb-2">
                  <div className="flex justify-between items-center">
                    <div>
                      <CardTitle>Graph Viewer</CardTitle>
                      <CardDescription>View detailed graphs for selected parameters</CardDescription>
                    </div>
                    <div className="flex space-x-2">
                      <Dialog>
                        <DialogTrigger asChild>
                          <Button variant="outline" size="icon">
                            <Maximize className="h-4 w-4" />
                          </Button>
                        </DialogTrigger>
                        <DialogContent className="max-w-4xl">
                          <GraphViewer
                            simulation={simulation}
                            parameters={selectedParams}
                            graphType={graphType}
                            fullscreen
                          />
                        </DialogContent>
                      </Dialog>
                      <Button variant="outline" size="icon">
                        <Download className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="mb-4">
                    <Tabs value={graphType} onValueChange={handleGraphTypeChange} className="w-full">
                      <TabsList className="grid grid-cols-3 md:grid-cols-7 w-full">
                        <TabsTrigger value="missingSegments">Missing</TabsTrigger>
                        <TabsTrigger value="nodesReady">Ready</TabsTrigger>
                        <TabsTrigger value="sentData">Sent</TabsTrigger>
                        <TabsTrigger value="recvData">Received</TabsTrigger>
                        <TabsTrigger value="dupData">Duplicate</TabsTrigger>
                        <TabsTrigger value="RowColDist">Distribution</TabsTrigger>
                        <TabsTrigger value="ecdf_restoreRowCount">Row Count</TabsTrigger>
                      </TabsList>
                    </Tabs>
                  </div>
                  <GraphViewer simulation={simulation} parameters={selectedParams} graphType={graphType} />
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="heatmaps" className="space-y-4">
              <Card>
                <CardHeader className="pb-2">
                  <div className="flex justify-between items-center">
                    <div>
                      <CardTitle>Heatmap Viewer</CardTitle>
                      <CardDescription>Explore parameter relationships through heatmaps</CardDescription>
                    </div>
                    <div className="flex space-x-2">
                      <Dialog>
                        <DialogTrigger asChild>
                          <Button variant="outline" size="icon">
                            <Maximize className="h-4 w-4" />
                          </Button>
                        </DialogTrigger>
                        <DialogContent className="max-w-4xl">
                          <HeatmapViewer simulation={simulation} fullscreen />
                        </DialogContent>
                      </Dialog>
                      <Button variant="outline" size="icon">
                        <Download className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <HeatmapViewer simulation={simulation} />
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="statistics" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Statistics Summary</CardTitle>
                  <CardDescription>View aggregated statistics across all parameter combinations</CardDescription>
                </CardHeader>
                <CardContent>
                  <StatisticsSummary simulation={simulation} />
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  )
}