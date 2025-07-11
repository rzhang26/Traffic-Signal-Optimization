# Traffic-Signal-Optimization
make a project (some form of data science based community optimization algorithm / ai) for specific district
inspiration: https://youtu.be/9ye0zbif5ME?si=k7GVHHZh62Msyfus (find repo somewhere: "EcoVision" for the Designpreneurs AI Design Hackathon)

*imperfect* traffic signal opimization tool-- fails to take into account certain things like population density, etc

Workflow
- Traffic Trengs Identification
  - input county location within NYS
  - specify streets / Area
  - specify range of dates (month to month basis)
  - display a summary page
    - graphs (eg. day vs. traffic_density vs. time vs. other vars, etc... (Look at recorded vars in datasets)) --> choose best 3 relevant vars 
    - AI generated summaries of trends for each graph + correlation coefficients
    - Interactive map highlighting a selected zone (ie. county, series of streets, town or something)
- Signal Optimization
    - graphs displaying predicted trends based on optimized changes (baseline metrics: vehicle delay, throughput, queue length, etc)
    - AI generated suggestions for signal optimization
      - timing changes (potentially) and frequency changes of those timing changes (also potentially) of particular traffic lights
    - Interactive map highlighting a selected zone (ie. county, series of streets, town or something)

Components
- Frontend
  - UI/UX Design w/ interactive features
  - Data visualizations
- Backend
  - Logic functions (eg. submit query to gemini, among others...)
    - Rule-based optimization (e.g. longest queue gets green)
    - ML-based predictions of peak traffic times or flow improvements
    - Possibly integrate existing libraries like SUMO (Simulation of Urban Mobility) for signal timing simulation
  - GeminiAPI free tier (trend summaries)
  - Libraries for data visualization (eg. MatPlotLib, numPy, others...)
  - Data Preprocessing (Handle missing values, outliers, or anomalies + standardize units and timestamps + geocode locations if data comes in lat/lng format, etc)
  - DB (Could be fake) + DBMS of local traffic data + API (NYS 511 API or NYC Open Data portal (for traffic sensor data, signal timing, congestion))

Tech Stack:
- Frontend
  - React + Tailwind CSS for fast dev.
  - Plotly.js or Chart.js for interactive visualizations.
  - Leaflet or Mapbox for maps.
- Backend
  - Flask / FastAPI (Python) for handling data logic.
  - SQLite / Firebase for DBMS.
  - Pandas, NumPy, Matplotlib, Seaborn for preprocessing + graphs.
  - OpenAI API (if allowed), or Gemini API (if free tier suffices).
