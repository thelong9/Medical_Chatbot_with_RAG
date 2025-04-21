import os
import logging
from retry import retry
from neo4j import GraphDatabase

HOSPITALS_CSV_PATH = os.getenv("HOSPITALS_CSV_PATH")
PAYERS_CSV_PATH = os.getenv("PAYERS_CSV_PATH")
PHYSICIANS_CSV_PATH = os.getenv("PHYSICIANS_CSV_PATH")
PATIENTS_CSV_PATH = os.getenv("PATIENTS_CSV_PATH")
VISITS_CSV_PATH = os.getenv("VISITS_CSV_PATH")
REVIEWS_CSV_PATH = os.getenv("REVIEWS_CSV_PATH")
EXAMPLE_CYPHER_CSV_PATH = os.getenv("EXAMPLE_CYPHER_CSV_PATH")

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

LOGGER = logging.getLogger(__name__)

NODES = ["Hospital", "Payer", "Physician", "Patient", "Visit", "Review"]

def _set_uniqueness_constraints(tx, node):
    query = f"""CREATE CONSTRAINT IF NOT EXISTS FOR (n:{node})
        REQUIRE n.id IS UNIQUE;"""
    _ = tx.run(query, {})

@retry(tries=100, delay=10)
def load_hospital_graph_from_csv() -> None:
    """Load structured hospital CSV data following
    a specific ontology into Neo4j"""

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    LOGGER.info("Setting uniqueness constraints on nodes")
    with driver.session(database="neo4j") as session:
        for node in NODES:
            session.execute_write(_set_uniqueness_constraints, node)

    LOGGER.info("Loading hospital nodes")
    with driver.session(database="neo4j") as session:
        query = f"""
        LOAD CSV WITH HEADERS
        FROM '{HOSPITALS_CSV_PATH}' AS hospitals
        MERGE (h:Hospital {{id: toInteger(hospitals.hospital_id),
                            name: hospitals.hospital_name,
                            state_name: hospitals.hospital_state}});
        """
        _ = session.run(query, {})

    LOGGER.info("Loading payer nodes")
    with driver.session(database="neo4j") as session:
        query = f"""
        LOAD CSV WITH HEADERS
        FROM '{PAYERS_CSV_PATH}' AS payers
        MERGE (p:Payer {{id: toInteger(payers.payer_id),
        name: payers.payer_name}});
        """
        _ = session.run(query, {})

    LOGGER.info("Loading physician nodes")
    with driver.session(database="neo4j") as session:
        query = f"""
        LOAD CSV WITH HEADERS
        FROM '{PHYSICIANS_CSV_PATH}' AS physicians
        MERGE (p:Physician {{id: toInteger(physicians.physician_id),
                            name: physicians.physician_name,
                            dob: physicians.physician_dob,
                            grad_year: physicians.physician_grad_year,
                            school: physicians.medical_school,
                            salary: toFloat(physicians.salary)
                            }});
        """
        _ = session.run(query, {})

    LOGGER.info("Loading visit nodes")
    with driver.session(database="neo4j") as session:
        query = f"""
        LOAD CSV WITH HEADERS FROM '{VISITS_CSV_PATH}' AS visits
        MERGE (v:Visit {{id: toInteger(visits.visit_id),
                            room_number: toInteger(visits.room_number),
                            admission_type: visits.admission_type,
                            admission_date: visits.date_of_admission,
                            test_results: visits.test_results,
                            status: visits.visit_status
        }})
            ON CREATE SET v.chief_complaint = visits.chief_complaint
            ON MATCH SET v.chief_complaint = visits.chief_complaint
            ON CREATE SET v.treatment_description = visits.treatment_description
            ON MATCH SET v.treatment_description = visits.treatment_description
            ON CREATE SET v.diagnosis = visits.primary_diagnosis
            ON MATCH SET v.diagnosis = visits.primary_diagnosis
            ON CREATE SET v.discharge_date = visits.discharge_date
            ON MATCH SET v.discharge_date = visits.discharge_date
         """
        _ = session.run(query, {})

    LOGGER.info("Loading patient nodes")
    with driver.session(database="neo4j") as session:
        query = f"""
        LOAD CSV WITH HEADERS
        FROM '{PATIENTS_CSV_PATH}' AS patients
        MERGE (p:Patient {{id: toInteger(patients.patient_id),
                        name: patients.patient_name,
                        sex: patients.patient_sex,
                        dob: patients.patient_dob,
                        blood_type: patients.patient_blood_type
                        }});
        """
        _ = session.run(query, {})

    LOGGER.info("Loading review nodes")
    with driver.session(database="neo4j") as session:
        query = f"""
        LOAD CSV WITH HEADERS
        FROM '{REVIEWS_CSV_PATH}' AS reviews
        MERGE (r:Review {{id: toInteger(reviews.review_id),
                         text: reviews.review,
                         patient_name: reviews.patient_name,
                         physician_name: reviews.physician_name,
                         hospital_name: reviews.hospital_name
                        }});
        """
        _ = session.run(query, {})

    LOGGER.info("Loading question nodes")
    with driver.session(database="neo4j") as session:
        query = f"""
        LOAD CSV WITH HEADERS
        FROM '{EXAMPLE_CYPHER_CSV_PATH}' AS questions
        MERGE (Q:Question {{
                         question: questions.question,
                         cypher: questions.cypher
                        }});
        """
        _ = session.run(query, {})

    LOGGER.info("Loading 'AT' relationships")
    with driver.session(database="neo4j") as session:
        query = f"""
        LOAD CSV WITH HEADERS FROM '{VISITS_CSV_PATH}' AS row
        MATCH (source: `Visit` {{ `id`: toInteger(trim(row.`visit_id`)) }})
        MATCH (target: `Hospital` {{ `id`:
        toInteger(trim(row.`hospital_id`))}})
        MERGE (source)-[r: `AT`]->(target)
        """
        _ = session.run(query, {})

    LOGGER.info("Loading 'WRITES' relationships")
    with driver.session(database="neo4j") as session:
        query = f"""
        LOAD CSV WITH HEADERS FROM '{REVIEWS_CSV_PATH}' AS reviews
            MATCH (v:Visit {{id: toInteger(reviews.visit_id)}})
            MATCH (r:Review {{id: toInteger(reviews.review_id)}})
            MERGE (v)-[writes:WRITES]->(r)
        """
        _ = session.run(query, {})

    LOGGER.info("Loading 'TREATS' relationships")
    with driver.session(database="neo4j") as session:
        query = f"""
        LOAD CSV WITH HEADERS FROM '{VISITS_CSV_PATH}' AS visits
            MATCH (p:Physician {{id: toInteger(visits.physician_id)}})
            MATCH (v:Visit {{id: toInteger(visits.visit_id)}})
            MERGE (p)-[treats:TREATS]->(v)
        """
        _ = session.run(query, {})

    LOGGER.info("Loading 'COVERED_BY' relationships")
    with driver.session(database="neo4j") as session:
        query = f"""
        LOAD CSV WITH HEADERS FROM '{VISITS_CSV_PATH}' AS visits
            MATCH (v:Visit {{id: toInteger(visits.visit_id)}})
            MATCH (p:Payer {{id: toInteger(visits.payer_id)}})
            MERGE (v)-[covered_by:COVERED_BY]->(p)
            ON CREATE SET
                covered_by.service_date = visits.discharge_date,
                covered_by.billing_amount = toFloat(visits.billing_amount)
        """
        _ = session.run(query, {})

    LOGGER.info("Loading 'HAS' relationships")
    with driver.session(database="neo4j") as session:
        query = f"""
        LOAD CSV WITH HEADERS FROM '{VISITS_CSV_PATH}' AS visits
            MATCH (p:Patient {{id: toInteger(visits.patient_id)}})
            MATCH (v:Visit {{id: toInteger(visits.visit_id)}})
            MERGE (p)-[has:HAS]->(v)
        """
        _ = session.run(query, {})

    LOGGER.info("Loading 'EMPLOYS' relationships")
    with driver.session(database="neo4j") as session:
        query = f"""
        LOAD CSV WITH HEADERS FROM '{VISITS_CSV_PATH}' AS visits
            MATCH (h:Hospital {{id: toInteger(visits.hospital_id)}})
            MATCH (p:Physician {{id: toInteger(visits.physician_id)}})
            MERGE (h)-[employs:EMPLOYS]->(p)
        """
        _ = session.run(query, {})


@retry(tries=100, delay=10)
def load_hospital_graph_from_csv_test():
    """Load structured hospital CSV data following
    a specific ontology into Neo4j"""

    driver = GraphDatabase.driver(
        NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
    )

    LOGGER.info("Setting uniqueness constraints on nodes")
    with driver.session(database="neo4j") as session:
        for node in NODES:
            session.execute_write(_set_uniqueness_constraints, node)
             
    load_queries = [
        {
            "name": "Hospital",
            "query": f"""
            LOAD CSV WITH HEADERS
            FROM '{HOSPITALS_CSV_PATH}' AS row
            WITH row WHERE row.hospital_id IS NOT NULL AND trim(row.hospital_id) <> ""
            MERGE (h:Hospital {{
                id: toInteger(row.hospital_id)
            }})
            SET h.name = row.hospital_name,
                h.state_name = row.hospital_state
            """
        },
        {
            "name": "Payer",
            "query": f"""
            LOAD CSV WITH HEADERS
            FROM '{PAYERS_CSV_PATH}' AS row
            WITH row WHERE row.payer_id IS NOT NULL AND trim(row.payer_id) <> ""
            MERGE (p:Payer {{
                id: toInteger(row.payer_id)
            }})
            SET p.name = row.payer_name
            """
        },
        {
            "name": "Physician",
            "query": f"""
            LOAD CSV WITH HEADERS
            FROM '{PHYSICIANS_CSV_PATH}' AS row
            WITH row WHERE row.physician_id IS NOT NULL AND trim(row.physician_id) <> ""
            MERGE (phy:Physician {{
                id: toInteger(row.physician_id)
            }})
            SET phy.name = row.physician_name,
                phy.dob = CASE
                    WHEN trim(row.physician_dob) = "" THEN null
                    WHEN trim(row.physician_dob) = "NULL" THEN null
                    ELSE date(row.physician_dob)
                END,
                phy.graduated_date = CASE
                    WHEN trim(row.physician_grad_year) = "" THEN null
                    WHEN trim(row.physician_grad_year) = "NULL" THEN null
                    ELSE date(row.physician_grad_year)
                END,
                phy.medical_school = row.medical_school,
                phy.salary = toFloat(row.salary)
            """
        },
        {
            "name": "Review",
            "query": f"""
            LOAD CSV WITH HEADERS
            FROM '{REVIEWS_CSV_PATH}' AS row
            WITH row WHERE row.review_id IS NOT NULL AND trim(row.review_id) <> ""
            MERGE (r:Review {{
                review_id: toInteger(row.review_id)
            }})
            SET r.visit_id = toInteger(row.visit_id),
                r.content = row.review,
                r.physician_name = row.physician_name,
                r.hospital_name = row.hospital_name,
                r.patient_name = row.patient_name
            """
        },
        {
            "name": "Visit",
            "query": f"""
            LOAD CSV WITH HEADERS
            FROM '{VISITS_CSV_PATH}' AS row
            WITH row WHERE row.visit_id IS NOT NULL AND trim(row.visit_id) <> ""
            MERGE (v:Visit {{
                visit_id: toInteger(row.visit_id)
            }})
            SET v.patient_id = toInteger(row.patient_id),
                v.date_of_admission = CASE
                    WHEN trim(row.date_of_admission) = "" THEN null
                    WHEN trim(row.date_of_admission) = "NULL" THEN null
                    ELSE date(row.date_of_admission)
                END,
                v.billing_amount = toFloat(row.billing_amount),
                v.room_number = toInteger(row.room_number),
                v.admission_type = row.admission_type,
                v.discharge_date = CASE
                    WHEN trim(row.discharge_date) = "" THEN null
                    WHEN trim(row.discharge_date) = "NULL" THEN null
                    ELSE date(row.discharge_date)
                END,
                v.test_results = row.test_results,
                v.physician_id = toInteger(row.physician_id),
                v.payer_id = toInteger(row.payer_id),
                v.hospital_id = toInteger(row.hospital_id),
                v.chief_complaint = coalesce(row.chief_complaint, "Unknown"),
                v.treatment_description = coalesce(row.treatment_description, "Unknown"),
                v.primary_diagnosis = coalesce(row.primary_diagnosis, "Unknown"),
                v.visit_status = row.visit_status
            """
        },
        {
            "name": "Patient",
            "query": f"""
            LOAD CSV WITH HEADERS
            FROM '{PATIENTS_CSV_PATH}' AS row
            WITH row WHERE row.patient_id IS NOT NULL AND trim(row.patient_id) <> ""
            MERGE (p:Patient {{
                id: toInteger(row.patient_id)
            }})
            SET p.patient_name = row.patient_name,
                p.patient_sex = row.patient_sex,
                p.patient_dob = CASE
                    WHEN trim(row.patient_dob) = "" THEN null
                    WHEN trim(row.patient_dob) = "NULL" THEN null
                    ELSE date(row.patient_dob)
                END,
                p.patient_blood_type = row.patient_blood_type
            """
        }
    ]
    
    LOGGER.info("Loading hospital nodes")
    with driver.session(database="neo4j") as session:
        for load_query in load_queries:
            LOGGER.info(f"Loading {load_query['name']} nodes")
            _ = session.run(load_query["query"], {})
            
            
            
    relationship_queries = [
        # Hospital EMPLOYS Physician (FIXED)
        """
        MATCH (h:Hospital), (phy:Physician)
        WHERE h.id = phy.hospital_id
        MERGE (h)-[:EMPLOYS]->(phy)
        RETURN count(*) AS count
        """,
        
        # Physician TREATS Visit (FIXED)
        """
        MATCH (phy:Physician), (v:Visits)
        WHERE phy.id = v.physician_id
        MERGE (phy)-[:TREATS]->(v)
        RETURN count(*) AS count
        """,
        
        # Patient HAS Visit (FIXED)
        """
        MATCH (p:Patient), (v:Visits)
        WHERE p.id = v.patient_id
        MERGE (p)-[:HAS]->(v)
        RETURN count(*) AS count
        """,
        
        # Visit AT Hospital (FIXED)
        """
        MATCH (v:Visits), (h:Hospital)
        WHERE v.hospital_id = h.id
        MERGE (v)-[:AT]->(h)
        RETURN count(*) AS count
        """,
        
        # Payer COVERED_BY Visit (FIXED)
        """
        MATCH (pay:Payer), (v:Visits)
        WHERE pay.id = v.payer_id
        MERGE (pay)-[:COVERED_BY {
            billing_amount: v.billing_amount,
            service_date: v.date_of_admission
        }]->(v)
        RETURN count(*) AS count
        """,
        
        # Physician WRITES Review (FIXED)
        """
        MATCH (phy:Physician), (r:Review)
        WHERE phy.name = r.physician_name
        MERGE (phy)-[:WRITES]->(r)
        RETURN count(*) AS count
        """
    ]
    
    with driver.session(database="neo4j") as session:
        for query in relationship_queries:
            try:
                result = session.run(query)
                LOGGER.info(f"Created relationships: {result.consume().counters.relationships_created}")
            except Exception as e:
                LOGGER.error(f"Failed to create relationships: {str(e)}")
            
            
if __name__ == "__main__":
    load_hospital_graph_from_csv() 
    