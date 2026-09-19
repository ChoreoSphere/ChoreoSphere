# NISAR Temporal Change & 3D Visualization Platform

An interactive platform for processing, analyzing, and visualizing Earth surface changes over time using NASA-ISRO Synthetic Aperture Radar (NISAR) data.

## 🛰️ Project Overview

The NASA-ISRO Synthetic Aperture Radar (NISAR) mission provides high-resolution SAR data capable of observing surface changes—including land deformation, glacier dynamics, forest canopy shifts, and ecosystem monitoring—with a consistent 12-day repeat orbit. 

This project aims to build an end-to-end open-source pipeline and interactive 3D web platform to ingest NISAR radar data, process temporal SAR time-series, and visualize surface dynamics through interactive, multi-dimensional timelines.

## 🌟 Core Features & Goals

- **Automated Data Ingestion:** Programmatic search and download pipeline for NISAR datasets from NASA/ASF DAAC.
- **Change & Displacement Analytics:** Processing engine to analyze backscatter variation and interferometric surface changes over time.
- **Geospatial API & Backend:** Scalable backend layer to manage, index, and serve tile layers and pixel-level time-series data.
- **Interactive 3D Timeline Visualizer:** Web interface with temporal scrubbing controls, split-screen change comparisons, and 3D surface rendering.

## 👥 Sub-Team Focus Areas

- **Model & InSAR Pipeline:** Data ingestion, radar signal processing, and change detection model development.
- **Backend & Spatial API:** Database architecture, spatial data indexing, and API endpoint services.
- **3D & Web Frontend:** Interactive UI, temporal scrubbing controls, and 3D geospatial viewport rendering.

## 🚀 Getting Started

*(Detailed installation, local development setup, and API usage instructions will be updated as the core architecture is established.)*

### Prerequisites
- Git
- Python 3.10+
- Node.js (v18+)

## 🤝 Contributing

This repository uses a structured feature-branch workflow. All contributions are submitted via Pull Requests targeting the `main` branch and require review by the respective sub-team lead before merging.
