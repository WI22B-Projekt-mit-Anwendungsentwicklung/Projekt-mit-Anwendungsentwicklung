# Projekt mit Anwendungsentwicklung

## Introduction
This project involves the development of a client-server application that processes and visualizes climate data from the **Daily Global Historical Climatology Network (GHCN)**. The system allows users to search for weather stations based on geographic coordinates and display temperature data in graphical and textual formats. The application is containerized using Docker and consists of a Flask-based backend and a MySQL database.

## Prerequisites
To use the application, the following tools are required:

- **Docker** (to run the containers)
- **Optional: Docker Desktop** (for easier management of containers and volumes)

## Installation and Execution

### Starting the Application
The application can be started using the following command:

```sh
curl -fsSL https://raw.githubusercontent.com/WI22B-Projekt-mit-Anwendungsentwicklung/Projekt-mit-Anwendungsentwicklung/main/docker-compose.yml | docker compose -f - up -d
```

The application runs on **port 8000** to avoid conflicts with **port 5000**, which is commonly occupied on macOS.

### Database
By default, the MySQL database is set up automatically on the first run. However, this process can take a long time. Alternatively, a **preconfigured Docker volume** containing the database can be downloaded and imported into **Docker Desktop** via the following link:

```
https://studentdhbwvsde-my.sharepoint.com/:u:/g/personal/marc_schuler_student_dhbw-vs_de/EXbMQsZbEUVBtlc2tf61m6oBK3yKtkfr_Vz7bs61s4N0mw?e=kKeCZS
```

## Application Structure
The application is orchestrated using Docker and consists of two containers:

- **Application Container**: Contains the **Frontend and Backend** (Flask)
- **Database Container**: Runs the MySQL database

Once started, the application can be accessed at [http://localhost:8000](http://localhost:8000).

## Code Conventions

### Frontend
- Functions are written in **camelCase**
- Variables are written in **camelCase**

### Backend
- Functions are written in **snake_case**
- Variables are written in **snake_case**