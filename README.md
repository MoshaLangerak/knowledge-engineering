# Knowledge Engineering Project

Welcome to the Knowledge Engineering project, this repository provides a reproducible setup for building and sharing a knowledge graph using Neo4j and Python.

## Neo4j & Python

This guide will help you set up Neo4j locally, connect it with Python, and structure your project for easy collaboration and sharing via GitHub.

### 1. Download and Install Neo4j Desktop

- Visit the [official Neo4j Download page](https://neo4j.com/download/).
- Download the version for your operating system (Windows, macOS, Linux).
- Follow the installation instructions:

### 2. Create A Local Database (Project)

**Inside Neo4j Desktop:**
1. Click **"New"** or **"Add"** and select **"Project"**.  
     _Example name: `LondonSupplyDemand`_
2. Within your project, click **"Add"** → **"Local DBMS"**.
3. Name your database.  
     _Example: `london-data-db`_
4. Set a password (e.g., `neo4jpassword`).  
     _Default username: `neo4j`_
5. Click **"Create"** and then **"Start"** your database.
6. Open the Neo4j Browser by clicking **"Open"** next to your database.  
     - Use this web interface to run Cypher queries.

**Connection details:**
- **Bolt URL:** `neo4j://localhost:7687`
- **Username:** `neo4j`
- **Password:** (the one you set)


## Running the Project

### 1. Add environment variables

- Create a `.env` file in the root directory of your project.
- Add the following lines to the `.env` file:

```plaintext
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
```
- Replace `your_password` with the password you set for your Neo4j database.
- Save the `.env` file.

### 2. Install Python Dependencies
- Install the required packages:
```bash
pip install -r requirements.txt
```

### 3. (optional) Move the CSV files
- Move the CSV files from the `data/processed` folder to the `import` folder of Neo4j.
- Go to the Neo4j Desktop application, select the three dots next to your database, and click on **"Open Folder"**.
- Select the `import` folder and move the CSV files there.

### 4. Run the Project
- To run the project, execute the following command in your terminal:
```bash
python streamlit run .\knowledge-graph-app\src\app.py
```