# DAS Simulator Visualizer

This web application provides a visualization interface for Data Availability Sampling (DAS) simulation results. It allows you to browse, analyze, and compare simulation runs with different parameters, view detailed graphs, and explore parameter relationships through heatmaps.

## Features

- **Simulation List**: Browse and filter all available simulation runs
- **Detailed Graphs**: Visualize various metrics from simulation runs:
- **Heatmaps**: Explore parameter relationships:
- **Parameter Exploration**: Adjust simulation parameters to see their impact on results
- **Statistics**: View aggregated statistics across parameter combinations

## Architecture

The application consists of two main components:

1. **Frontend**: React-based web UI with Next.js framework
2. **Backend**: FastAPI server that processes and serves simulation data

## Running the Application

### Prerequisites

- Node.js 18.x or later
- Python 3.9 or later
- DAS Simulator results (XML files in `results/` directory)

### Backend Setup

1. Install Python dependencies:

```bash
pip install fastapi uvicorn pydantic
```

2. Start the backend server:

```bash
python server.py
```

The server will start on http://localhost:8000 by default.

### Frontend Setup

1. Install Node.js dependencies:

```bash
npm install
```

2. Start the development server:

```bash
npm run dev
```

3. Open your browser and navigate to http://localhost:3000

## Project Structure

```
das-simulator-visualizer/
├── app/                    # Next.js app components
│   ├── page.tsx            # Homepage (simulation list)
│   ├── simulations/[id]/   # Simulation detail pages
│   ├── globals.css         # Global styles
│   └── layout.tsx          # Layout component
├── components/             # React components
│   ├── graph-viewer.tsx    # Graph visualization component
│   ├── heatmap-viewer.tsx  # Heatmap visualization component
│   ├── parameter-selector.tsx # Parameter adjustment component
│   ├── simulation-list.tsx # Simulations listing component
│   ├── simulation-metadata.tsx # Simulation details component
│   ├── simulation-provider.tsx # Data provider component
│   ├── statistics-summary.tsx # Statistics visualization component
│   └── ui/                 # UI components (buttons, cards, etc.)
├── lib/                    # Utility functions and services
│   └── simulation-service.ts # API client for backend communication
├── public/                 # Static assets
└── package.json            # Node.js package configuration
```
## Deployment

For production deployment:

1. Build the frontend:

```bash
npm run build
```