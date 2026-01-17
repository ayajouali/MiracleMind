# populate_graph_enhanced.py
from neo4j_client import run_query
from domain_config import get_concepts_for_domain, get_all_domains

def create_concept(name, description="", difficulty=1, domain="mathematics", subcategory=None):
    run_query("""
    MERGE (c:Concept {name: $name})
    SET c.description = $description, 
        c.difficulty = $difficulty,
        c.domain = $domain,
        c.subcategory = $subcategory
    """, {"name": name, "description": description, "difficulty": difficulty, "domain": domain, "subcategory": subcategory})

def add_dependency(prereq, concept):
    try:
        run_query("""
        MATCH (a:Concept {name:$prereq}), (b:Concept {name:$concept})
        MERGE (b)-[:REQUIRES]->(a)
        """, {"prereq": prereq, "concept": concept})
        print(f"✓ {concept} requires {prereq}")
    except Exception as e:
        print(f"⚠ Could not add dependency {prereq} -> {concept}: {e}")

def create_student(student_id, name, preferred_domains=None):
    if preferred_domains is None:
        preferred_domains = ["mathematics"]
    run_query("""
    MERGE (s:Student {id:$id})
    SET s.name = $name, s.preferred_domains = $domains, s.created_at = datetime()
    """, {"id": student_id, "name": name, "domains": preferred_domains})

def mark_completed(student_id, concept_name, score=0.0, time_spent_minutes=None):
    try:
        run_query("""
        MATCH (s:Student {id:$id}), (c:Concept {name:$name})
        MERGE (s)-[r:COMPLETED]->(c)
        SET r.score = $score, 
            r.completed_at = datetime(),
            r.time_spent_minutes = $time_spent
        """, {"id": student_id, "name": concept_name, "score": score, "time_spent": time_spent_minutes})
        print(f"✓ {student_id} completed {concept_name}")
    except Exception as e:
        print(f"⚠ Could not mark {concept_name} for {student_id}: {e}")

def seed_domain(domain_key):
    concepts = get_concepts_for_domain(domain_key)
    print(f"\n🌱 Seeding domain: {domain_key} ({len(concepts)} concepts)")
    for name, desc, diff, subcat in concepts:
        create_concept(name, desc, diff, domain_key, subcat)
    sorted_concepts = sorted(concepts, key=lambda x: x[2])
    for i in range(1, len(sorted_concepts)):
        current = sorted_concepts[i]
        prereqs = [c for c in sorted_concepts[:i] if c[3] == current[3] and c[2] < current[2]]
        if prereqs:
            add_dependency(prereqs[-1][0], current[0])

def seed_all_domains():
    domains = get_all_domains()
    for domain_key in domains.keys():
        seed_domain(domain_key)
    return list(domains.keys())

def create_sample_students():
    students = [
        {
            "id": "student_1",
            "name": "Aya Jouali",
            "domains": ["mathematics", "physics", "computer_science"],
            "completed": [("Arithmetic", 0.85, 15), ("Algebra Basics", 0.75, 30)]
        },
        {
            "id": "student_2",
            "name": "Omar El Amrani",
            "domains": ["computer_science", "mathematics"],
            "completed": [("Variables & Types", 0.95, 10), ("Arithmetic", 0.90, 10)]
        }
    ]
    for student in students:
        create_student(student["id"], student["name"], student["domains"])
        for concept_name, score, time in student["completed"]:
            mark_completed(student["id"], concept_name, score, time)
    return [s["id"] for s in students]

def add_cross_domain_dependencies():
    cross_deps = [
        ("Arithmetic", "Stoichiometry"),
        ("Algebra Basics", "Newton's Laws"),
        ("Functions", "Recursion")
    ]
    for prereq, concept in cross_deps:
        add_dependency(prereq, concept)

def get_database_stats():
    stats = run_query("""
    MATCH (c:Concept)
    RETURN c.domain AS domain, count(*) AS count
    ORDER BY count DESC
    """, fetch=True)
    print("\nConcepts by domain:")
    for row in stats:
        print(f"  {row['domain']}: {row['count']}")
    total = run_query("MATCH (c:Concept) RETURN count(c) AS total", fetch=True)
    print(f"\nTotal concepts: {total[0]['total']}")
    students = run_query("MATCH (s:Student) RETURN count(s) AS total", fetch=True)
    print(f"Total students: {students[0]['total']}")
    deps = run_query("MATCH ()-[r:REQUIRES]->() RETURN count(r) AS total", fetch=True)
    print(f"Total dependencies: {deps[0]['total']}")

def main():
    print("\n🚀 SEEDING ALL DOMAINS")
    domains = seed_all_domains()
    add_cross_domain_dependencies()
    students = create_sample_students()
    get_database_stats()
    print("\n✅ Database initialized!")
    print(f"Domains seeded: {', '.join(domains)}")
    print(f"Sample students: {', '.join(students)}")
    return students

if __name__ == "__main__":
    main()
