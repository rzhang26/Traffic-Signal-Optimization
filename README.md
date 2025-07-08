# Traffic-Signal-Optimization
make a project (some form of data science based community optimization algorithm / ai) for specific district
inspiration: https://youtu.be/9ye0zbif5ME?si=k7GVHHZh62Msyfus (find repo somewhere: "EcoVision" for the Designpreneurs AI Design Hackathon)

Workflow
- Traffic Trengs Identification
  - input county location within NYS
  - specify streets / Area
  - specify range of dates (month to month basis)
  - display a summary page
    - graphs (eg. day vs. traffic_density vs. time vs. other vars, etc... (Look at recorded vars in datasets))
    - AI generated summaries of trends for each graph + correlation coefficients
- Signal Optimization
    - graphs displaying predicted trends based on changes
    - AI generated suggestions for signal optimization
       - timing changes (potentially) and frequency changes of those timing changes (also potentially) of particular traffic lights 

Components
- Frontend
  - UI/UX Design w/ interactive features
  - Data visualizations
- Backend
  - Logic functions (eg. submit query to gemini, among others...)
  - GeminiAPI free tier (trend summaries)
  - Libraries for data visualization (eg. MatPlotLib, numPy, others...)
  - DB (Could be fake) + DBMS of local traffic data
