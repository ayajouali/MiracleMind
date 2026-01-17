# domain_config.py
"""
Configuration des domaines d'apprentissage supportés (sans machine_learning)
"""

DOMAINS = {
    "mathematics": {
        "name": "Mathematics",
        "color": "#3B82F6",
        "icon": "📐",
        "subcategories": ["algebra", "calculus", "geometry", "statistics", "discrete_math"]
    },
    "physics": {
        "name": "Physics",
        "color": "#10B981",
        "icon": "⚛️",
        "subcategories": ["mechanics", "thermodynamics", "electromagnetism", "quantum", "relativity"]
    },
    "computer_science": {
        "name": "Computer Science",
        "color": "#8B5CF6",
        "icon": "💻",
        "subcategories": ["programming", "algorithms", "databases", "networks", "security", "ai_ml"]
    },
    "chemistry": {
        "name": "Chemistry",
        "color": "#F59E0B",
        "icon": "🧪",
        "subcategories": ["organic", "inorganic", "physical", "analytical", "biochemistry"]
    },
    "biology": {
        "name": "Biology",
        "color": "#059669",
        "icon": "🧬",
        "subcategories": ["molecular", "cellular", "genetics", "ecology", "evolution"]
    },
    "languages": {
        "name": "Languages",
        "color": "#EC4899",
        "icon": "🗣️",
        "subcategories": ["grammar", "vocabulary", "pronunciation", "writing", "literature"]
    },
    "history": {
        "name": "History",
        "color": "#EF4444",
        "icon": "📚",
        "subcategories": ["ancient", "medieval", "modern", "contemporary", "cultural"]
    },
    "engineering": {
        "name": "Engineering",
        "color": "#6366F1",
        "icon": "⚙️",
        "subcategories": ["mechanical", "electrical", "civil", "chemical", "software"]
    }
}

CONCEPT_TEMPLATES = {
    "mathematics": [
        ("Arithmetic", "Basic operations: +, -, ×, ÷", 1, "algebra"),
        ("Algebra Basics", "Variables, equations, inequalities", 2, "algebra"),
        ("Linear Equations", "Solving ax + b = c", 2, "algebra"),
        ("Quadratic Equations", "Solving ax² + bx + c = 0", 3, "algebra"),
        ("Functions", "Understanding f(x) and transformations", 3, "algebra"),
        ("Derivatives", "Rate of change and slopes", 4, "calculus"),
        ("Integrals", "Area under curves", 4, "calculus"),
        ("Limits", "Behavior as x approaches a value", 3, "calculus"),
        ("Series", "Infinite sums and convergence", 5, "calculus"),
        ("Differential Equations", "Solving dy/dx = f(x,y)", 5, "calculus"),
    ],
    "physics": [
        ("Newton's Laws", "F = ma and motion principles", 2, "mechanics"),
        ("Kinematics", "Position, velocity, acceleration", 2, "mechanics"),
        ("Energy Conservation", "Kinetic and potential energy", 3, "mechanics"),
        ("Momentum", "p = mv and collisions", 3, "mechanics"),
        ("Rotational Motion", "Angular velocity and torque", 4, "mechanics"),
        ("Electric Fields", "Coulomb's law and field lines", 3, "electromagnetism"),
        ("Magnetic Fields", "Lorentz force and induction", 4, "electromagnetism"),
        ("Thermodynamic Laws", "Heat, work, and entropy", 4, "thermodynamics"),
        ("Wave Motion", "Frequency, wavelength, amplitude", 3, "mechanics"),
        ("Quantum States", "Wave-particle duality", 5, "quantum"),
    ],
    "computer_science": [
        ("Variables & Types", "Data types and variables", 1, "programming"),
        ("Control Flow", "If/else, loops", 2, "programming"),
        ("Functions", "Defining and using functions", 2, "programming"),
        ("Arrays & Lists", "Sequential data structures", 2, "programming"),
        ("Object-Oriented Programming", "Classes, objects, inheritance", 3, "programming"),
        ("Big O Notation", "Algorithm complexity analysis", 3, "algorithms"),
        ("Sorting Algorithms", "Quicksort, mergesort, heapsort", 3, "algorithms"),
        ("Binary Search", "Efficient searching in sorted data", 2, "algorithms"),
        ("Hash Tables", "Key-value data structures", 3, "algorithms"),
        ("Graphs", "Nodes, edges, traversal algorithms", 4, "algorithms"),
        ("SQL Basics", "SELECT, INSERT, UPDATE, DELETE", 2, "databases"),
        ("Database Design", "Normalization and relationships", 3, "databases"),
        ("Recursion", "Functions calling themselves", 3, "programming"),
        ("Dynamic Programming", "Optimal substructure problems", 5, "algorithms"),
    ],
    "chemistry": [
        ("Atomic Structure", "Protons, neutrons, electrons", 1, "inorganic"),
        ("Periodic Table", "Elements and their properties", 2, "inorganic"),
        ("Chemical Bonds", "Ionic, covalent, metallic", 2, "inorganic"),
        ("Stoichiometry", "Mole calculations and conversions", 3, "inorganic"),
        ("Acids & Bases", "pH scale and reactions", 3, "inorganic"),
        ("Organic Nomenclature", "Naming organic compounds", 3, "organic"),
        ("Functional Groups", "Alcohols, aldehydes, ketones", 3, "organic"),
        ("Reaction Mechanisms", "Step-by-step reaction pathways", 4, "organic"),
        ("Thermochemistry", "Enthalpy, entropy, Gibbs energy", 4, "physical"),
        ("Chemical Kinetics", "Reaction rates and mechanisms", 4, "physical"),
    ],
    "biology": [
        ("Cell Structure", "Organelles and their functions", 2, "cellular"),
        ("DNA Structure", "Double helix and base pairing", 2, "molecular"),
        ("Protein Synthesis", "Transcription and translation", 3, "molecular"),
        ("Cell Division", "Mitosis and meiosis", 3, "cellular"),
        ("Mendelian Genetics", "Dominant and recessive traits", 3, "genetics"),
        ("Natural Selection", "Evolution mechanisms", 3, "evolution"),
        ("Ecosystems", "Energy flow and nutrient cycles", 2, "ecology"),
        ("Enzyme Kinetics", "Catalysis and inhibition", 4, "biochemistry"),
        ("Gene Expression", "Regulation and epigenetics", 4, "molecular"),
        ("Population Genetics", "Hardy-Weinberg equilibrium", 4, "genetics"),
    ],
    "languages": [
        ("Basic Vocabulary", "Common words and phrases", 1, "vocabulary"),
        ("Present Tense", "Current actions and states", 2, "grammar"),
        ("Past Tense", "Completed actions", 2, "grammar"),
        ("Future Tense", "Upcoming actions", 2, "grammar"),
        ("Articles", "Definite and indefinite articles", 2, "grammar"),
        ("Pronouns", "Subject, object, possessive", 2, "grammar"),
        ("Adjectives", "Describing nouns", 2, "grammar"),
        ("Prepositions", "Spatial and temporal relations", 3, "grammar"),
        ("Subjunctive Mood", "Hypothetical situations", 4, "grammar"),
        ("Idiomatic Expressions", "Cultural phrases", 3, "vocabulary"),
    ],
    "history": [
        ("Ancient Civilizations", "Mesopotamia, Egypt, Indus, China", 2, "ancient"),
        ("Medieval Europe", "Feudalism, knights, kingdoms", 3, "medieval"),
        ("Renaissance", "Art, science and exploration", 3, "modern"),
        ("Industrial Revolution", "Mechanization and social change", 3, "modern"),
        ("World Wars", "WWI and WWII overview", 4, "contemporary"),
        ("Cold War", "Superpower rivalry", 4, "contemporary"),
        ("Decolonization", "Independence movements", 3, "contemporary"),
        ("Modern History", "Globalization and tech", 3, "contemporary"),
        ("Cultural History", "Religion, art, customs", 2, "cultural"),
        ("Contemporary Issues", "Current events and analysis", 3, "contemporary"),
    ],
    "engineering": [
        ("Statics", "Forces in equilibrium", 2, "mechanical"),
        ("Dynamics", "Motion of rigid bodies", 3, "mechanical"),
        ("Materials", "Properties of engineering materials", 3, "mechanical"),
        ("Circuits", "Basic electrical circuits", 2, "electrical"),
        ("Thermodynamics Engineering", "Applied thermodynamics", 4, "thermal"),
        ("Control Systems", "Feedback and stability", 4, "systems"),
        ("Design Principles", "Engineering design methodology", 3, "design"),
        ("Fluid Mechanics", "Fluid behavior and flows", 3, "mechanical"),
        ("Systems Engineering", "Large-scale system design", 4, "systems"),
        ("Software Engineering", "Software lifecycle and testing", 3, "software"),
    ],
}

def get_domain_info(domain_key):
    return DOMAINS.get(domain_key)

def get_all_domains():
    return DOMAINS

def get_concepts_for_domain(domain_key):
    return CONCEPT_TEMPLATES.get(domain_key, [])
