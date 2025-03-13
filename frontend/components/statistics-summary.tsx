"use client"

import { useEffect, useState } from "react"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts"
import { AlertCircle } from "lucide-react"

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Skeleton } from "@/components/ui/skeleton"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { getSimulationStats } from "@/lib/simulation-service"

interface StatisticsSummaryProps {
  simulation: any
}

export function StatisticsSummary({ simulation }: StatisticsSummaryProps) {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [stats, setStats] = useState<any>(null)
  const [statType, setStatType] = useState("byNodes")

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true)
        setError(null)

        // Get the statistics for the simulation
        const data = await getSimulationStats(simulation.id)
        setStats(data)
      } catch (err) {
        console.error("Error loading statistics:", err)
        setError("Failed to load statistics. Please try again later.")
      } finally {
        setLoading(false)
      }
    }

    fetchStats()
  }, [simulation.id])

  if (loading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-full" />
        <Skeleton className="h-[300px] w-full" />
      </div>
    )
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Error</AlertTitle>
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    )
  }

  if (!stats) {
    return (
      <Alert>
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>No data available</AlertTitle>
        <AlertDescription>No statistics available for this simulation.</AlertDescription>
      </Alert>
    )
  }

  return (
    <div className="space-y-6">
      <Tabs value={statType} onValueChange={setStatType} className="w-full">
        <TabsList className="grid grid-cols-3 w-full">
          <TabsTrigger value="byNodes">By Nodes</TabsTrigger>
          <TabsTrigger value="byFailureRate">By Failure Rate</TabsTrigger>
          <TabsTrigger value="byChi">By Chi</TabsTrigger>
        </TabsList>
      </Tabs>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Missing Samples</CardTitle>
            <CardDescription>Average percentage of missing samples</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[200px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={stats[statType].missingSamples}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="value" fill="#8884d8" name="Missing Samples (%)" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Nodes Ready</CardTitle>
            <CardDescription>Average percentage of nodes ready</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[200px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={stats[statType].nodesReady}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="value" fill="#82ca9d" name="Nodes Ready (%)" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Data Sent</CardTitle>
            <CardDescription>Average amount of data sent</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[200px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={stats[statType].sentData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="value" fill="#ffc658" name="Data Sent (KB)" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Performance Comparison</CardTitle>
          <CardDescription>
            Comparison of key metrics across different{" "}
            {statType === "byNodes" ? "node counts" : statType === "byFailureRate" ? "failure rates" : "chi values"}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={stats[statType].comparison}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="missingSamples" fill="#8884d8" name="Missing Samples (%)" />
                <Bar dataKey="nodesReady" fill="#82ca9d" name="Nodes Ready (%)" />
                <Bar dataKey="sentData" fill="#ffc658" name="Data Sent (KB)" />
                <Bar dataKey="recvData" fill="#ff8042" name="Data Received (KB)" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

