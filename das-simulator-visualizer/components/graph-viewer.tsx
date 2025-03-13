import React, { useEffect, useState } from "react";
import Image from "next/image";
import { AlertCircle } from "lucide-react";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Skeleton } from "@/components/ui/skeleton";
import { getGraphUrl } from "@/lib/simulation-service";

interface GraphViewerProps {
  simulation: any;
  parameters: any;
  graphType: string;
  fullscreen?: boolean;
}

export function GraphViewer({ simulation, parameters, graphType, fullscreen = false }: GraphViewerProps) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [graphUrl, setGraphUrl] = useState<string | null>(null);

  useEffect(() => {
    const fetchGraph = async () => {
      try {
        setLoading(true);
        setError(null);

        const url = await getGraphUrl(
          simulation.id,
          parameters.numberNodes,
          parameters.failureRate,
          parameters.blockSize,
          parameters.netDegree,
          parameters.chi,
          parameters.run,
          graphType,
        );

        setGraphUrl(url);
      } catch (err) {
        console.error("Error loading graph:", err);
        setError("Failed to load graph. Please try again later.");
      } finally {
        setLoading(false);
      }
    };

    fetchGraph();
  }, [simulation.id, parameters, graphType]);

  return (
    <div className={`w-full ${fullscreen ? "h-[600px]" : "h-[300px]"} relative`}>
      {loading ? (
        <Skeleton className={`w-full ${fullscreen ? "h-[600px]" : "h-[300px]"}`} />
      ) : error ? (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      ) : !graphUrl ? (
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>No data available</AlertTitle>
          <AlertDescription>No graph data available for the selected parameters.</AlertDescription>
        </Alert>
      ) : (
        <Image
          src={graphUrl}
          alt={`${graphType} graph for the selected parameters`}
          fill
          className="object-contain"
          onError={() => setError("Failed to load graph image.")}
        />
      )}
    </div>
  );
}