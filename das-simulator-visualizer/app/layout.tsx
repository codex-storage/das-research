import type React from "react"
import { SimulationProvider } from "@/components/simulation-provider"
import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "DAS Simulator Visualizer",
  description: "Visualize Data Availability Sampling simulation results",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <SimulationProvider>{children}</SimulationProvider>
      </body>
    </html>
  )
}

