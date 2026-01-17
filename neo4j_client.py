# neo4j_client.py
from neo4j import GraphDatabase, basic_auth
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure ici selon ton installation
NEO4J_URI = os.environ.get("NEO4J_URI", "neo4j://127.0.0.1:7687")
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "miraclemind123")

_driver = None

def get_driver():
    global _driver
    if _driver is None:
        _driver = GraphDatabase.driver(NEO4J_URI, auth=basic_auth(NEO4J_USER, NEO4J_PASSWORD))
    return _driver

def run_query(query: str, params: dict = None, fetch: bool = False):
    """
    Execute une requête Cypher.
    - Si fetch=True retourne la liste de résultats (list of dict).
    - Sinon retourne None.
    """
    driver = get_driver()
    params = params or {}
    with driver.session() as session:
        try:
            if fetch:
                result = session.run(query, params)
                records = [dict(record) for record in result]
                return records
            else:
                session.run(query, params)
                return None
        except Exception as e:
            logger.exception("Neo4j query failed: %s", e)
            raise
