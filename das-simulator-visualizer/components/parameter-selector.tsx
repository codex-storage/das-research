import React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

interface ParameterSelectorProps {
  parameters: any;
  selectedParams: any;
  onParamChange: (param: string, value: any) => void;
}

export function ParameterSelector({ parameters, selectedParams, onParamChange }: ParameterSelectorProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Parameter Selection</CardTitle>
        <CardDescription>Adjust parameters to view different simulation results</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <div className="flex justify-between">
            <Label htmlFor="numberNodes">Number of Nodes</Label>
            <span className="text-sm">{selectedParams.numberNodes}</span>
          </div>
          <Slider
            id="numberNodes"
            min={parameters.numberNodes.min}
            max={parameters.numberNodes.max}
            step={parameters.numberNodes.step || 128}
            value={[selectedParams.numberNodes]}
            onValueChange={(value) => onParamChange("numberNodes", value[0])}
          />
        </div>

        <div className="space-y-2">
          <div className="flex justify-between">
            <Label htmlFor="failureRate">Failure Rate (%)</Label>
            <span className="text-sm">{selectedParams.failureRate}%</span>
          </div>
          <Slider
            id="failureRate"
            min={parameters.failureRate.min}
            max={parameters.failureRate.max}
            step={parameters.failureRate.step || 10}
            value={[selectedParams.failureRate]}
            onValueChange={(value) => onParamChange("failureRate", value[0])}
          />
        </div>

        {parameters.maliciousNodes && (
          <div className="space-y-2">
            <div className="flex justify-between">
              <Label htmlFor="maliciousNodes">Malicious Nodes (%)</Label>
              <span className="text-sm">{selectedParams.maliciousNodes || 0}%</span>
            </div>
            <Slider
              id="maliciousNodes"
              min={0}
              max={100}
              step={20}
              value={[selectedParams.maliciousNodes || 0]}
              onValueChange={(value) => onParamChange("maliciousNodes", value[0])}
            />
          </div>
        )}

        <div className="space-y-2">
          <Label htmlFor="blockSize">Block Size</Label>
          <Select
            value={selectedParams.blockSize.toString()}
            onValueChange={(value) => onParamChange("blockSize", Number.parseInt(value))}
          >
            <SelectTrigger id="blockSize">
              <SelectValue placeholder="Select block size" />
            </SelectTrigger>
            <SelectContent>
              {parameters.blockSize.options?.map((option: number) => (
                <SelectItem key={option} value={option.toString()}>
                  {option}
                </SelectItem>
              )) || <SelectItem value={parameters.blockSize.value.toString()}>{parameters.blockSize.value}</SelectItem>}
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="netDegree">Network Degree</Label>
          <Select
            value={selectedParams.netDegree.toString()}
            onValueChange={(value) => onParamChange("netDegree", Number.parseInt(value))}
          >
            <SelectTrigger id="netDegree">
              <SelectValue placeholder="Select network degree" />
            </SelectTrigger>
            <SelectContent>
              {parameters.netDegree.options?.map((option: number) => (
                <SelectItem key={option} value={option.toString()}>
                  {option}
                </SelectItem>
              )) || <SelectItem value={parameters.netDegree.value.toString()}>{parameters.netDegree.value}</SelectItem>}
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="chi">Custody Size</Label>
          <Select
            value={selectedParams.chi.toString()}
            onValueChange={(value) => onParamChange("chi", Number.parseInt(value))}
          >
            <SelectTrigger id="chi">
              <SelectValue placeholder="Select custody size" />
            </SelectTrigger>
            <SelectContent>
              {parameters.chi.options?.map((option: number) => (
                <SelectItem key={option} value={option.toString()}>
                  {option}
                </SelectItem>
              )) || <SelectItem value={parameters.chi.value.toString()}>{parameters.chi.value}</SelectItem>}
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="run">Run</Label>
          <Select
            value={selectedParams.run.toString()}
            onValueChange={(value) => onParamChange("run", Number.parseInt(value))}
          >
            <SelectTrigger id="run">
              <SelectValue placeholder="Select run" />
            </SelectTrigger>
            <SelectContent>
              {Array.from({ length: parameters.run.max + 1 }, (_, i) => (
                <SelectItem key={i} value={i.toString()}>
                  Run {i}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </CardContent>
    </Card>
  );
}