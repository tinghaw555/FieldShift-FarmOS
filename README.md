# 🌱 AGRINEXUS – FieldShift FarmOS

### NASA Space Apps Challenge 2026

**Agricultural Decision Support System for Climate-Adaptive Crop Rotation Planning**

AGRINEXUS introduces **FieldShift FarmOS**, a web-based agricultural decision-support platform that integrates NASA Earth observation data, weather forecasts, scientific crop modelling, and farm sensor information to support climate-adaptive farming decisions.

Our goal is to help farmers better understand climate risks, evaluate crop rotation strategies, manage water resources, and make informed agricultural decisions.

---

## 🚀 Explore Our Project

### 🌐 Live Project Website

**[Access FieldShift FarmOS](https://tinghaw555.github.io/FieldShift-FarmOS/)**

Explore our interactive agricultural decision-support platform.

### 🎬 30-Second Project Video

**[Watch Our 30-Second Project Introduction](https://youtu.be/W9hq3yrWjCQ)**

A quick introduction to the agricultural challenges we aim to solve and how AGRINEXUS addresses them.

### 🎥 3-Minute Project Demonstration

**[Watch Our 3-Minute Project Demonstration]((https://youtu.be/RgTWrj-QCmM))**

Discover the main features of FieldShift FarmOS, including NASA climate data integration, crop rotation comparison, What-If analysis, and smart farm monitoring.

### 💻 Source Code and Technical Documentation

**[Explore Our GitHub Repository](https://github.com/tinghaw555/FieldShift-FarmOS)**

Access our source code, scientific methodology, system architecture, documentation, and project resources.

---
📖 How to Use FieldShift FarmOS

Step 1: Create Your Farm

Open FieldShift FarmOS and select a geographical location using the interactive map or GPS coordinates.

Enter the required farm information and create the farm.

Step 2: Explore Climate Information

Retrieve available NASA POWER historical climate information for the selected location.

Review relevant environmental conditions, including temperature, rainfall, humidity, solar radiation, and wind speed.

Step 3: Evaluate Planting Conditions

Explore climate-related conditions that may influence crop suitability and planting decisions.

Step 4: Compare Crop Rotation Strategies

Create and compare alternative crop rotation plans.

Review estimated water requirements, potential water stress, irrigation demand, and other supported indicators.

Step 5: Explore What-If Scenarios

Adjust parameters such as rainfall efficiency, irrigation availability, and soil water holding capacity.

Observe how these changes affect modelled agricultural results.

Step 6: Monitor Farm Conditions

Import compatible CSV sensor readings to visualize environmental conditions.

Where physical hardware is available and configured, sensor readings can support additional monitoring and validation activities.

Step 7: Export Results

Export supported analysis outputs and agricultural records for documentation or further study.

💻 Installation and Local Development

Option A: Open the Public Website

Visit:

https://tinghaw555.github.io/FieldShift-FarmOS/

The public website is accessible through a browser without installing software.

Features that require a backend will only function when the public API and related services are available.

Option B: Run FieldShift FarmOS Locally

For development, testing, or running the complete backend-dependent application, follow the local setup instructions.

Prerequisites

Node.js and npm (compatible with the project's Next.js version)

Python 3.9 or newer, subject to dependency compatibility

Git

1. Clone the Repository

git clone https://github.com/tinghaw555/FieldShift-FarmOS.git
cd FieldShift-FarmOS

2. Set Up the Backend

Navigate to the backend directory:

cd backend

Create a Python virtual environment:

python -m venv .venv

Activate the virtual environment.

Windows:

.venv\Scripts\activate

Linux/macOS:

source .venv/bin/activate

Install dependencies:

pip install -r requirements.txt

Initialize the database using the project's migration or setup procedure.

For the original local implementation:

python migrate_database.py

Start the backend:

uvicorn main:app --reload --host 127.0.0.1 --port 8000

The backend should become available at:

http://localhost:8000

The health endpoint can be checked at:

http://localhost:8000/api/health

3. Set Up the Frontend

Open a separate terminal and navigate to:

cd FieldShift-FarmOS/frontend

Install frontend dependencies:

npm install

Configure the local frontend environment variables according to the project's example environment configuration.

Start the development server:

npm run dev

Open:

http://localhost:3000/FieldShift-FarmOS

The exact local path depends on the currently configured Next.js basePath.

Keep the backend and frontend terminals running during local testing.

Option C: Hardware Setup

The project also contains firmware and configuration resources for optional ESP32 integration.

Refer to the hardware directory for the appropriate board configuration, wiring instructions, and firmware.

Do not commit real Wi-Fi passwords, API credentials, or device secrets to the public repository.

## 🎯 Our Mission

AGRINEXUS aims to bridge the gap between Earth observation data and practical agricultural planning.

By combining NASA POWER climate information with agricultural models and farm-specific environmental data, FieldShift FarmOS helps users explore sustainable farming strategies and better understand the potential impacts of changing climate conditions.

Our vision is to make scientific agricultural decision-support tools more accessible to farmers, particularly small-scale agricultural communities.

**Live Demo:** https://tinghaw555.github.io/FieldShift-FarmOS/

---

Made with ❤️ for farmers facing climate uncertainty
