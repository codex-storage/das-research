"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { format, parseISO } from "date-fns"
import { Calendar, ChevronRight, Filter, Search } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Skeleton } from "@/components/ui/skeleton"
import { useSimulation } from "./simulation-provider"
import { Badge } from "@/components/ui/badge"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Calendar as CalendarComponent } from "@/components/ui/calendar"
import { Label } from "@/components/ui/label"
import { Checkbox } from "@/components/ui/checkbox"

export function SimulationList() {
  const router = useRouter()
  const { simulations, loading, error } = useSimulation()
  const [searchTerm, setSearchTerm] = useState("")
  const [dateRange, setDateRange] = useState<{ from: Date | undefined; to: Date | undefined }>({
    from: undefined,
    to: undefined,
  })
  const [showFilters, setShowFilters] = useState(false)
  const [successFilter, setSuccessFilter] = useState<string | null>(null)

  const handleSimulationSelect = (id: string) => {
    router.push(`/simulations/${id}`)
  }

  const formatDate = (dateString: string) => {
    try {
      if (dateString.includes('T') && dateString.endsWith(':00Z')) {
        dateString = dateString.replace(':00Z', 'Z');
      }
      
      const date = parseISO(dateString);
      return format(date, "PPP");
    } catch (error) {
      console.error("Error formatting date:", dateString, error);
      
      try {
        if (dateString.includes("_")) {
          const parts = dateString.split("_");
          if (parts.length >= 2) {
            const datePart = parts[0];
            const timePart = parts[1].replace(/-/g, ":");
            return `${datePart} ${timePart}`;
          }
        }
        
        return new Date(dateString).toLocaleDateString();
      } catch (e) {
        return "Date unavailable";
      }
    }
  };

  const filteredSimulations = simulations.filter((sim) => {
    if (searchTerm && !sim.id.toLowerCase().includes(searchTerm.toLowerCase())) {
      return false
    }

    if (dateRange.from) {
      try {
        const simDate = new Date(sim.date);
        if (simDate < dateRange.from) return false;
      } catch (e) {
        console.warn("Could not parse date for filtering:", sim.date);
      }
    }
    if (dateRange.to) {
      try {
        const simDate = new Date(sim.date);
        if (simDate > dateRange.to) return false;
      } catch (e) {
        console.warn("Could not parse date for filtering:", sim.date);
      }
    }

    if (successFilter === "high" && sim.successRate < 75) {
      return false
    }
    if (successFilter === "medium" && (sim.successRate < 50 || sim.successRate >= 75)) {
      return false
    }
    if (successFilter === "low" && sim.successRate >= 50) {
      return false
    }

    return true
  })

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center p-8">
        <h2 className="text-xl font-semibold text-red-500 mb-2">Error</h2>
        <p className="text-muted-foreground">{error}</p>
        <Button className="mt-4" onClick={() => window.location.reload()}>
          Try Again
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
        <h2 className="text-2xl font-bold tracking-tight">Simulation Runs</h2>
        <div className="flex gap-2 w-full sm:w-auto">
          <div className="relative w-full sm:w-auto">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              type="search"
              placeholder="Search simulations..."
              className="w-full sm:w-[250px] pl-8"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <Popover open={showFilters} onOpenChange={setShowFilters}>
            <PopoverTrigger asChild>
              <Button variant="outline" size="icon">
                <Filter className="h-4 w-4" />
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-80">
              <div className="grid gap-4">
                <div className="space-y-2">
                  <h4 className="font-medium leading-none">Filters</h4>
                  <p className="text-sm text-muted-foreground">Filter simulation results by date and success rate</p>
                </div>
                <div className="space-y-2">
                  <Label>Date Range</Label>
                  <CalendarComponent
                    mode="range"
                    selected={dateRange}
                    onSelect={setDateRange as any}
                    className="rounded-md border"
                  />
                </div>
                <div className="space-y-2">
                  <Label>Success Rate</Label>
                  <div className="grid gap-2">
                    <div className="flex items-center space-x-2">
                      <Checkbox
                        id="success-high"
                        checked={successFilter === "high"}
                        onCheckedChange={() => setSuccessFilter(successFilter === "high" ? null : "high")}
                      />
                      <label htmlFor="success-high" className="text-sm">
                        High (75-100%)
                      </label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Checkbox
                        id="success-medium"
                        checked={successFilter === "medium"}
                        onCheckedChange={() => setSuccessFilter(successFilter === "medium" ? null : "medium")}
                      />
                      <label htmlFor="success-medium" className="text-sm">
                        Medium (50-75%)
                      </label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Checkbox
                        id="success-low"
                        checked={successFilter === "low"}
                        onCheckedChange={() => setSuccessFilter(successFilter === "low" ? null : "low")}
                      />
                      <label htmlFor="success-low" className="text-sm">
                        Low (0-50%)
                      </label>
                    </div>
                  </div>
                </div>
                <Button
                  onClick={() => {
                    setDateRange({ from: undefined, to: undefined })
                    setSuccessFilter(null)
                  }}
                >
                  Reset Filters
                </Button>
              </div>
            </PopoverContent>
          </Popover>
        </div>
      </div>

      {loading ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <Card key={i} className="overflow-hidden">
              <CardHeader className="pb-2">
                <Skeleton className="h-5 w-1/2 mb-2" />
                <Skeleton className="h-4 w-3/4" />
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-2">
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-4 w-full" />
                </div>
              </CardContent>
              <CardFooter>
                <Skeleton className="h-9 w-full" />
              </CardFooter>
            </Card>
          ))}
        </div>
      ) : filteredSimulations.length === 0 ? (
        <div className="flex flex-col items-center justify-center p-8 border rounded-lg">
          <h3 className="text-lg font-semibold mb-2">No simulations found</h3>
          <p className="text-muted-foreground text-center">
            {searchTerm || dateRange.from || dateRange.to || successFilter
              ? "Try adjusting your filters to see more results."
              : "No simulation runs are available. Run a simulation to get started."}
          </p>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {filteredSimulations.map((simulation) => (
            <Card key={simulation.id} className="overflow-hidden">
              <CardHeader className="pb-2">
                <div className="flex items-center gap-2">
                  <Calendar className="h-4 w-4 text-muted-foreground" />
                  <CardDescription>{formatDate(simulation.date || simulation.id)}</CardDescription>
                </div>
                <CardTitle className="text-lg">{simulation.id}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-y-2 text-sm">
                  <div className="text-muted-foreground">Nodes:</div>
                  <div>
                    {simulation.parameters.numberNodes.min}-{simulation.parameters.numberNodes.max}
                  </div>
                  <div className="text-muted-foreground">Failure Rate:</div>
                  <div>
                    {simulation.parameters.failureRate.min}%-{simulation.parameters.failureRate.max}%
                  </div>
                  <div className="text-muted-foreground">Success Rate:</div>
                  <div className="flex items-center">
                    <Badge
                      className={
                        simulation.successRate >= 75
                          ? "bg-green-500"
                          : simulation.successRate >= 50
                            ? "bg-yellow-500"
                            : "bg-red-500"
                      }
                    >
                      {simulation.successRate}%
                    </Badge>
                  </div>
                </div>
              </CardContent>
              <CardFooter>
                <Button className="w-full" onClick={() => handleSimulationSelect(simulation.id)}>
                  View Details
                  <ChevronRight className="ml-2 h-4 w-4" />
                </Button>
              </CardFooter>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}