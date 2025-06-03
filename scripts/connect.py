from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

class Neo4jConnection:
    def __init__(self, uri, user, password):
        self.__uri = uri
        self.__user = user
        self.__password = password
        self.__driver = None

        try:
            self.__driver = GraphDatabase.driver(self.__uri, auth=(self.__user, self.__password))
            self.__driver.verify_connectivity()
        except Exception as e:
            print(f"Failed to create the driver: {e}")

    def close(self):
        if self.__driver is not None:
            self.__driver.close()
            print("Neo4j connection closed.")

    def query(self, query, parameters=None, db=None):
        if self.__driver is None:
            print("Driver not initialized.")
            return None

        try:
            records, summary, keys = self.__driver.execute_query(
                query, parameters, database_=db if db else "neo4j"
            )
            return records, summary, keys
        except Exception as e:
            print(f"Query failed: {e}")
            return None, None, None
        

# Example driver code 
if __name__ == "__main__":
    conn = Neo4jConnection(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    # Example query to create a node
    records, _, _ = conn.query("CREATE (n:Person {name: 'Alice'}) RETURN n")

    # Example query display the current node count
    records, _, _ = conn.query("MATCH (n) RETURN count(n) AS node_count")
    if records:
       print(f"Current node count: {records[0]['node_count']}")

    # # Example query to delete a node
    # records, _, _ = conn.query("MATCH (n:Person {name: 'Alice'}) DELETE n")

    # conn.close()