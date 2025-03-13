// heatmap-viewer.tsx
import React, { useEffect, useState } from "react";
import Image from "next/image";
import { AlertCircle } from "lucide-react";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { getHeatmapUrl } from "@/lib/simulation-service";

interface HeatmapViewerProps {
  simulation: any;
  fullscreen?: boolean;
}

export function HeatmapViewer({ simulation, fullscreen = false }: HeatmapViewerProps) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [heatmapType, setHeatmapType] = useState("nodesVsFailure");
  const [heatmapUrl, setHeatmapUrl] = useState<string | null>(null);

  const heatmapTypes = [
    { id: "nodesVsFailure", label: "Nodes vs Failure" },
    { id: "nodesVsChi", label: "Nodes vs Chi" },
    { id: "failureVsChi", label: "Failure vs Chi" },
    { id: "failureVsNetDegree", label: "Failure vs Net Degree" },
    { id: "NWDegVsNodeOnRuntime", label: "Network Degree vs Nodes" },
    { id: "NWDegVsMalNodeOnMissingSamples", label: "Net Degree vs Malicious Nodes" },
    { id: "NWDegVsFailureRateOnMissingSamples", label: "Net Degree vs Failure Rate" },
  ];

  useEffect(() => {
    const fetchHeatmap = async () => {
      try {
        setLoading(true);
        setError(null);

        // Get the heatmap URL based on the heatmap type
        const url = await getHeatmapUrl(simulation.id, heatmapType);
        setHeatmapUrl(url);
      } catch (err) {
        console.error("Error loading heatmap:", err);
        setError("Failed to load heatmap. Please try again later.");
      } finally {
        setLoading(false);
      }
    };

    fetchHeatmap();
  }, [simulation.id, heatmapType]);

  return (
    <div className="space-y-4">
      <Tabs value={heatmapType} onValueChange={setHeatmapType} className="w-full">
        <TabsList className="grid grid-cols-2 md:grid-cols-4 w-full">
          {heatmapTypes.map((type) => (
            <TabsTrigger key={type.id} value={type.id}>
              {type.label}
            </TabsTrigger>
          ))}
        </TabsList>
      </Tabs>

      <div className={`w-full ${fullscreen ? "h-[600px]" : "h-[300px]"} relative`}>
        {loading ? (
          <Skeleton className={`w-full ${fullscreen ? "h-[600px]" : "h-[300px]"}`} />
        ) : error ? (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        ) : !heatmapUrl ? (
          <Alert>
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>No data available</AlertTitle>
            <AlertDescription>No heatmap data available for the selected parameters.</AlertDescription>
          </Alert>
        ) : (
          <Image
            src={heatmapUrl}
            alt={`${heatmapType} heatmap`}
            fill
            className="object-contain"
            onError={() => setError("Failed to load heatmap image.")}
          />
        )}
      </div>
    </div>
  );
}