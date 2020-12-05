# HRRR Forecast Graphics

Christina Holt
CSPB 4253
Fall 2020
Final Project

# Description

An interactive service that grabs gridded NOAA HRRR (High-resolution Rapid
Refresh) forecasts from GCP via a Pub/Sub service and generates standard maps of
forecast data per user request.

# Requirements

## Google Cloud Services

- Compute Engine Instance for hosting front end
- Kubernetes Cluster
- Persistent Storage Bucket
- Pub/sub

## Software

- Flask
- Redis Database
- RabbitMQ
- MiniConda
- NOAA-GSL Web Graphics Python Package
