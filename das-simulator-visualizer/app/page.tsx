import { SimulationList } from "@/components/simulation-list"

export default function HomePage() {
  return (
    <div className="flex flex-col min-h-screen">
      <header className="border-b bg-background">
        <div className="container flex h-16 items-center px-4 md:px-6">
          <h1 className="text-lg font-semibold">DAS Simulator Visualizer</h1>
        </div>
      </header>
      <main className="flex-1 container py-6 px-4 md:px-6">
        <SimulationList />
      </main>
      <footer className="border-t py-4 bg-background">
        <div className="container flex flex-col items-center justify-between gap-4 px-4 md:flex-row md:px-6">
          <p className="text-sm text-muted-foreground">&copy; {new Date().getFullYear()} DAS Simulator Visualizer</p>
        </div>
      </footer>
    </div>
  )
}

