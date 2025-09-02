#!/usr/bin/env python3
"""
Simple Academic Domain Setup - Fixed Version
"""

import json
from pathlib import Path


def create_academic_structure():
    """Create the academic domain structure."""
    base_path = Path("fine_tuning/datasets/academic_domains")

    # Create all directories
    domains = {
        "mathematics": ["algebra", "geometry", "trigonometry", "calculus"],
        "english": ["creative_writing", "reading_comprehension", "american_literature"],
        "art": [
            "foundational",
            "abstract",
            "history_of_art",
            "performing",
            "music_theory",
            "visual_arts",
        ],
        "history": [
            "civics",
            "world_history",
            "us_history",
            "regional_history",
            "economics",
        ],
        "science": [
            "environmental_science",
            "physics",
            "astronomy",
            "forensic_science",
            "oceanography",
            "botany",
            "earth_science",
            "geology",
            "physical_science",
            "zoology",
            "anatomy",
            "computer_science",
            "food_science",
        ],
        "foreign_language": ["spanish", "french", "italian"],
    }

    for domain, subdomains in domains.items():
        domain_path = base_path / domain
        domain_path.mkdir(parents=True, exist_ok=True)

        for subdomain in subdomains:
            subdomain_path = domain_path / subdomain
            subdomain_path.mkdir(parents=True, exist_ok=True)

        # Special case for regional history
        if domain == "history":
            wv_path = domain_path / "regional_history" / "west_virginia"
            wv_path.mkdir(parents=True, exist_ok=True)

        print(f"✅ Created {domain} with {len(subdomains)} subdomains")

    # Create tool mapping
    tool_mapping = {
        "mathematics": {
            "specialist": "phi3_mathematics_tutor",
            "voice": "jarvis",
            "tools": ["calculator", "graphing", "latex_renderer", "equation_solver"],
        },
        "english": {
            "specialist": "phi3_english_tutor",
            "voice": "alan",
            "tools": ["text_analyzer", "writing_assistant", "literature_database"],
        },
        "art": {
            "specialist": "phi3_art_tutor",
            "voice": "amy",
            "tools": [
                "image_analyzer",
                "color_palette",
                "music_notation",
                "timeline_creator",
            ],
        },
        "history": {
            "specialist": "phi3_history_tutor",
            "voice": "jarvis",
            "tools": ["timeline_creator", "map_generator", "primary_source_analyzer"],
        },
        "science": {
            "specialist": "phi3_science_tutor",
            "voice": "jarvis",
            "tools": [
                "data_analyzer",
                "simulation_runner",
                "lab_guide",
                "formula_renderer",
            ],
        },
        "foreign_language": {
            "specialist": "phi3_language_tutor",
            "voice": "amy",
            "tools": [
                "translator",
                "pronunciation_guide",
                "grammar_checker",
                "culture_guide",
            ],
        },
    }

    # Save tool mapping
    config_path = base_path / "domain_tool_mapping.json"
    with open(config_path, "w") as f:
        json.dump(tool_mapping, f, indent=2)

    print(f"🔧 Created tool mapping: {config_path}")

    # Create simple README files
    for domain, config in tool_mapping.items():
        domain_path = base_path / domain
        readme_content = f"""# {domain.title()} Domain

## Specialist: {config['specialist']}
## Voice: {config['voice']}
## Tools: {', '.join(config['tools'])}

## Subdomains:
{chr(10).join(f"- {sub}" for sub in domains[domain])}

## Training Data Structure:
- training_examples.jsonl
- tool_integration.jsonl  
- socratic_questioning.jsonl
- assessment_examples.jsonl
"""

        readme_path = domain_path / "README.md"
        with open(readme_path, "w") as f:
            f.write(readme_content)

        print(f"📝 Created README: {domain}/README.md")

    print("\n🎉 Academic Domain Structure Complete!")
    print(f"✅ {len(domains)} major domains")
    total_subdomains = sum(len(subs) for subs in domains.values())
    print(f"✅ {total_subdomains} subdomains")
    print("🚀 Ready for specialized training data generation!")


if __name__ == "__main__":
    create_academic_structure()
