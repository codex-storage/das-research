import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { format, parseISO } from "date-fns"
import { Badge } from "./ui/badge"

interface SimulationMetadataProps {
  simulation: any
}

const formatDate = (dateString: string) => {
  try {
    if (dateString && dateString.includes('T') && dateString.endsWith(':00Z')) {
      dateString = dateString.replace(':00Z', 'Z');
    }
    
    const date = parseISO(dateString);
    return format(date, "PPP 'at' p");
  } catch (error) {
    console.error("Error formatting date:", dateString, error);
    
    try {
      if (dateString && dateString.includes("_")) {
        const parts = dateString.split("_");
        if (parts.length >= 2) {
          const datePart = parts[0];
          const timePart = parts[1].replace(/-/g, ":");
          return `${datePart} at ${timePart}`;
        }
      }
      
      return dateString || "Date unavailable";
    } catch (e) {
      return "Date unavailable";
    }
  }
};

export function SimulationMetadata({ simulation }: SimulationMetadataProps) {
  if (!simulation) {
    return <div>Loading...</div>;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Simulation Details</CardTitle>
        <CardDescription>Run on {formatDate(simulation.date || simulation.id)}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <h4 className="text-sm font-medium mb-2">Parameter Ranges</h4>
          <div className="grid grid-cols-2 gap-y-2 text-sm">
            <div className="text-muted-foreground">Nodes:</div>
            <div>
              {simulation.parameters.numberNodes.min}-{simulation.parameters.numberNodes.max}
            </div>
            <div className="text-muted-foreground">Failure Rate:</div>
            <div>
              {simulation.parameters.failureRate.min}%-{simulation.parameters.failureRate.max}%
            </div>
            <div className="text-muted-foreground">Block Size:</div>
            <div>{simulation.parameters.blockSize.value}</div>
            <div className="text-muted-foreground">Net Degree:</div>
            <div>{simulation.parameters.netDegree.value}</div>
            <div className="text-muted-foreground">Chi:</div>
            <div>{simulation.parameters.chi.value}</div>
            <div className="text-muted-foreground">Runs:</div>
            <div>{simulation.parameters.run.max + 1}</div>
          </div>
        </div>
        <div>
          <h4 className="text-sm font-medium mb-2">Overall Performance</h4>
          <div className="grid grid-cols-2 gap-y-2 text-sm">
            <div className="text-muted-foreground">Success Rate:</div>
            <div>
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
            <div className="text-muted-foreground">Avg. Missing Samples:</div>
            <div>{simulation.avgMissingSamples.toFixed(2)}%</div>
            <div className="text-muted-foreground">Avg. Nodes Ready:</div>
            <div>{simulation.avgNodesReady.toFixed(2)}%</div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}