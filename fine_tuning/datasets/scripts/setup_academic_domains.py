#!/usr/bin/env python3
"""
Academic Domain Configuration for Specialized Training Datasets
Configures the structured folder system for academic subject specialization.
"""

import json
from pathlib import Path
from typing import Any, Dict


class AcademicDomainOrganizer:
    """Organizes academic domains for specialized model training."""

    def __init__(self, base_path: str = "fine_tuning/datasets/academic_domains"):
        self.base_path = Path(base_path)
        self.domain_config = self._create_domain_configuration()

    def _create_domain_configuration(self) -> Dict[str, Any]:
        """Create comprehensive academic domain configuration."""
        return {
            "mathematics": {
                "description": "Mathematical reasoning and problem-solving across all levels",
                "specialist_model": "phi3_mathematics_tutor",
                "voice_preference": "jarvis",
                "primary_tools": [
                    "calculator",
                    "graphing",
                    "latex_renderer",
                    "equation_solver",
                ],
                "subdomain_mapping": {
                    "algebra": {
                        "focus": "Equations, functions, polynomials, systems",
                        "tools": ["equation_solver", "latex_renderer", "graphing"],
                        "training_emphasis": "step_by_step_solving",
                    },
                    "geometry": {
                        "focus": "Shapes, proofs, spatial reasoning, measurements",
                        "tools": ["diagram_create", "latex_renderer", "visual_proofs"],
                        "training_emphasis": "visual_reasoning",
                    },
                    "trigonometry": {
                        "focus": "Angles, triangles, periodic functions, identities",
                        "tools": ["graphing", "unit_circle", "trig_calculator"],
                        "training_emphasis": "pattern_recognition",
                    },
                    "calculus": {
                        "focus": "Limits, derivatives, integrals, applications",
                        "tools": [
                            "derivative_calculator",
                            "integral_solver",
                            "graphing",
                        ],
                        "training_emphasis": "conceptual_understanding",
                    },
                },
            },
            "english": {
                "description": "Language arts, literature, and communication skills",
                "specialist_model": "phi3_english_tutor",
                "voice_preference": "alan",
                "primary_tools": [
                    "text_analyzer",
                    "writing_assistant",
                    "literature_database",
                ],
                "subdomain_mapping": {
                    "creative_writing": {
                        "focus": "Storytelling, character development, style, voice",
                        "tools": [
                            "writing_prompts",
                            "style_analyzer",
                            "feedback_generator",
                        ],
                        "training_emphasis": "creative_guidance",
                    },
                    "reading_comprehension": {
                        "focus": "Analysis, inference, critical thinking, vocabulary",
                        "tools": [
                            "passage_analyzer",
                            "question_generator",
                            "vocabulary_builder",
                        ],
                        "training_emphasis": "analytical_thinking",
                    },
                    "american_literature": {
                        "focus": "Historical context, themes, literary movements",
                        "tools": [
                            "timeline_creator",
                            "theme_analyzer",
                            "context_provider",
                        ],
                        "training_emphasis": "historical_analysis",
                    },
                },
            },
            "art": {
                "description": "Visual arts, performing arts, music theory, and art history",
                "specialist_model": "phi3_art_tutor",
                "voice_preference": "amy",
                "primary_tools": [
                    "image_analyzer",
                    "color_palette",
                    "music_notation",
                    "timeline_creator",
                ],
                "subdomain_mapping": {
                    "foundational": {
                        "focus": "Basic principles, elements, design fundamentals",
                        "tools": [
                            "design_principles",
                            "color_wheel",
                            "composition_guide",
                        ],
                        "training_emphasis": "fundamental_concepts",
                    },
                    "abstract": {
                        "focus": "Non-representational art, conceptual thinking",
                        "tools": [
                            "concept_explorer",
                            "movement_analyzer",
                            "technique_guide",
                        ],
                        "training_emphasis": "conceptual_analysis",
                    },
                    "history_of_art": {
                        "focus": "Movements, periods, cultural context, major works",
                        "tools": [
                            "timeline_creator",
                            "comparison_tool",
                            "context_provider",
                        ],
                        "training_emphasis": "historical_context",
                    },
                    "performing": {
                        "focus": "Theater, dance, performance techniques",
                        "tools": [
                            "script_analyzer",
                            "movement_guide",
                            "performance_tips",
                        ],
                        "training_emphasis": "practical_application",
                    },
                    "music_theory": {
                        "focus": "Scales, harmony, composition, analysis",
                        "tools": [
                            "music_notation",
                            "chord_analyzer",
                            "scale_generator",
                        ],
                        "training_emphasis": "theoretical_understanding",
                    },
                    "visual_arts": {
                        "focus": "Drawing, painting, sculpture, digital art",
                        "tools": [
                            "technique_guide",
                            "medium_advisor",
                            "portfolio_builder",
                        ],
                        "training_emphasis": "skill_development",
                    },
                },
            },
            "history": {
                "description": "Historical analysis, civics, economics, and regional studies",
                "specialist_model": "phi3_history_tutor",
                "voice_preference": "jarvis",
                "primary_tools": [
                    "timeline_creator",
                    "map_generator",
                    "primary_source_analyzer",
                ],
                "subdomain_mapping": {
                    "civics": {
                        "focus": "Government systems, rights, civic participation",
                        "tools": [
                            "government_structure",
                            "rights_analyzer",
                            "civic_engagement",
                        ],
                        "training_emphasis": "civic_understanding",
                    },
                    "world_history": {
                        "focus": "Global civilizations, cultural exchange, major events",
                        "tools": [
                            "timeline_creator",
                            "cultural_comparison",
                            "event_analyzer",
                        ],
                        "training_emphasis": "global_perspective",
                    },
                    "us_history": {
                        "focus": "American development, key figures, national events",
                        "tools": [
                            "timeline_creator",
                            "document_analyzer",
                            "figure_profiles",
                        ],
                        "training_emphasis": "national_narrative",
                    },
                    "regional_history": {
                        "focus": "Local and regional historical development",
                        "subdomain_mapping": {
                            "west_virginia": {
                                "focus": "Appalachian culture, coal industry, state development",
                                "tools": [
                                    "local_timeline",
                                    "industry_tracker",
                                    "cultural_analyzer",
                                ],
                                "training_emphasis": "regional_identity",
                            }
                        },
                        "training_emphasis": "local_context",
                    },
                    "economics": {
                        "focus": "Economic systems, markets, financial literacy",
                        "tools": [
                            "market_analyzer",
                            "budget_calculator",
                            "system_comparator",
                        ],
                        "training_emphasis": "economic_reasoning",
                    },
                },
            },
            "science": {
                "description": "Scientific inquiry, methodology, and specialized sciences",
                "specialist_model": "phi3_science_tutor",
                "voice_preference": "jarvis",
                "primary_tools": [
                    "data_analyzer",
                    "simulation_runner",
                    "lab_guide",
                    "formula_renderer",
                ],
                "subdomain_mapping": {
                    "environmental_science": {
                        "focus": "Ecosystems, climate, sustainability, conservation",
                        "tools": [
                            "ecosystem_modeler",
                            "climate_tracker",
                            "impact_calculator",
                        ],
                        "training_emphasis": "systems_thinking",
                    },
                    "physics": {
                        "focus": "Forces, energy, waves, matter, quantum mechanics",
                        "tools": [
                            "physics_simulator",
                            "formula_calculator",
                            "concept_visualizer",
                        ],
                        "training_emphasis": "mathematical_modeling",
                    },
                    "astronomy": {
                        "focus": "Celestial objects, cosmology, space exploration",
                        "tools": [
                            "star_chart",
                            "distance_calculator",
                            "orbit_simulator",
                        ],
                        "training_emphasis": "scale_understanding",
                    },
                    "forensic_science": {
                        "focus": "Evidence analysis, investigation methods, lab techniques",
                        "tools": [
                            "evidence_analyzer",
                            "lab_procedure",
                            "case_study_guide",
                        ],
                        "training_emphasis": "analytical_methodology",
                    },
                    "oceanography": {
                        "focus": "Marine ecosystems, currents, ocean chemistry",
                        "tools": ["ocean_map", "current_tracker", "species_database"],
                        "training_emphasis": "marine_systems",
                    },
                    "botany": {
                        "focus": "Plant biology, classification, ecology, physiology",
                        "tools": [
                            "plant_identifier",
                            "growth_tracker",
                            "classification_guide",
                        ],
                        "training_emphasis": "biological_classification",
                    },
                    "earth_science": {
                        "focus": "Geology, meteorology, hydrology, earth systems",
                        "tools": [
                            "rock_identifier",
                            "weather_tracker",
                            "geological_timeline",
                        ],
                        "training_emphasis": "earth_systems",
                    },
                    "geology": {
                        "focus": "Rock formation, plate tectonics, geological time",
                        "tools": ["rock_cycle", "geological_map", "timeline_creator"],
                        "training_emphasis": "geological_processes",
                    },
                    "physical_science": {
                        "focus": "Chemistry and physics fundamentals, matter and energy",
                        "tools": [
                            "periodic_table",
                            "reaction_simulator",
                            "energy_calculator",
                        ],
                        "training_emphasis": "fundamental_concepts",
                    },
                    "zoology": {
                        "focus": "Animal biology, behavior, classification, evolution",
                        "tools": [
                            "animal_classifier",
                            "behavior_tracker",
                            "evolution_tree",
                        ],
                        "training_emphasis": "biological_diversity",
                    },
                    "anatomy": {
                        "focus": "Human body systems, physiology, medical terminology",
                        "tools": [
                            "body_system_viewer",
                            "medical_dictionary",
                            "function_analyzer",
                        ],
                        "training_emphasis": "systems_integration",
                    },
                    "computer_science": {
                        "focus": "Programming, algorithms, data structures, systems",
                        "tools": [
                            "code_executor",
                            "algorithm_visualizer",
                            "debugging_guide",
                        ],
                        "training_emphasis": "computational_thinking",
                    },
                    "food_science": {
                        "focus": "Nutrition, food chemistry, safety, preparation",
                        "tools": [
                            "nutrition_calculator",
                            "recipe_analyzer",
                            "safety_guide",
                        ],
                        "training_emphasis": "practical_application",
                    },
                },
            },
            "foreign_language": {
                "description": "World languages, culture, and communication",
                "specialist_model": "phi3_language_tutor",
                "voice_preference": "amy",
                "primary_tools": [
                    "translator",
                    "pronunciation_guide",
                    "grammar_checker",
                    "culture_guide",
                ],
                "subdomain_mapping": {
                    "spanish": {
                        "focus": "Spanish grammar, vocabulary, Hispanic culture",
                        "tools": [
                            "spanish_conjugator",
                            "vocabulary_builder",
                            "culture_explorer",
                        ],
                        "training_emphasis": "communicative_competence",
                        "voice_preference": "spanish_native",
                    },
                    "french": {
                        "focus": "French grammar, vocabulary, Francophone culture",
                        "tools": [
                            "french_conjugator",
                            "pronunciation_guide",
                            "culture_explorer",
                        ],
                        "training_emphasis": "cultural_immersion",
                        "voice_preference": "french_native",
                    },
                    "italian": {
                        "focus": "Italian grammar, vocabulary, Italian culture",
                        "tools": [
                            "italian_conjugator",
                            "pronunciation_guide",
                            "culture_explorer",
                        ],
                        "training_emphasis": "artistic_expression",
                        "voice_preference": "italian_native",
                    },
                },
            },
        }

    def create_folder_structure(self):
        """Create the complete academic domain folder structure."""
        for domain, config in self.domain_config.items():
            domain_path = self.base_path / domain
            domain_path.mkdir(parents=True, exist_ok=True)

            # Create subdomain folders
            if "subdomain_mapping" in config:
                for subdomain, subconfig in config["subdomain_mapping"].items():
                    subdomain_path = domain_path / subdomain
                    subdomain_path.mkdir(parents=True, exist_ok=True)

                    # Handle nested subdomains (like west_virginia under regional_history)
                    if "subdomain_mapping" in subconfig:
                        for nested_sub, nested_config in subconfig[
                            "subdomain_mapping"
                        ].items():
                            nested_path = subdomain_path / nested_sub
                            nested_path.mkdir(parents=True, exist_ok=True)

            print(f"✅ Created domain structure: {domain}")

    def generate_domain_readme_files(self):
        """Generate README files for each domain with configuration details."""
        for domain, config in self.domain_config.items():
            domain_path = self.base_path / domain
            readme_content = self._create_domain_readme(domain, config)

            readme_path = domain_path / "README.md"
            with open(readme_path, "w") as f:
                f.write(readme_content)

            print(f"📝 Created README: {domain}/README.md")

    def _create_domain_readme(self, domain: str, config: Dict[str, Any]) -> str:
        """Create README content for a domain."""
        content = f"""# {domain.title()} Domain Training Configuration

## Description
{config['description']}

## Specialist Configuration
- **Model**: {config['specialist_model']}
- **Voice Preference**: {config['voice_preference']}
- **Primary Tools**: {', '.join(config['primary_tools'])}

## Subdomains

"""

        if "subdomain_mapping" in config:
            for subdomain, subconfig in config["subdomain_mapping"].items():
                content += f"### {subdomain.replace('_', ' ').title()}\n"
                content += f"**Focus**: {subconfig['focus']}\n"
                content += f"**Tools**: {', '.join(subconfig['tools'])}\n"
                content += (
                    f"**Training Emphasis**: {subconfig['training_emphasis']}\n\n"
                )

                # Handle nested subdomains
                if "subdomain_mapping" in subconfig:
                    content += "#### Regional Specializations:\n"
                    for nested_sub, nested_config in subconfig[
                        "subdomain_mapping"
                    ].items():
                        content += f"- **{nested_sub.replace('_', ' ').title()}**: {nested_config['focus']}\n"
                    content += "\n"

        content += f"""## Training Data Structure

```
{domain}/
├── training_examples.jsonl     # Domain-specific training examples
├── tool_integration.jsonl      # Tool usage examples for this domain
├── socratic_questioning.jsonl  # Domain-specific Socratic examples
└── assessment_examples.jsonl   # Evaluation and testing examples
```

## Integration with Tool Control System

This domain integrates with the tiny tool controller through:
- Automatic tool selection based on domain context
- Specialist model routing to {config['specialist_model']}
- Voice preference mapping to {config['voice_preference']}
- Multi-modal output coordination

## Training Pipeline

1. **Data Collection**: Gather domain-specific examples
2. **Tool Integration**: Map tools to learning objectives
3. **Specialist Training**: Fine-tune {config['specialist_model']}
4. **Testing**: Validate with domain experts
5. **Deployment**: Integrate with production system
"""

        return content

    def create_tool_mapping_config(self):
        """Create comprehensive tool mapping configuration file."""
        tool_mapping = {
            "domain_tool_mapping": {},
            "specialist_routing": {},
            "voice_preferences": {},
            "tool_definitions": self._get_tool_definitions(),
        }

        for domain, config in self.domain_config.items():
            # Map domains to tools
            tool_mapping["domain_tool_mapping"][domain] = {
                "primary_tools": config["primary_tools"],
                "specialist": config["specialist_model"],
                "voice": config["voice_preference"],
            }

            # Add subdomain tool mappings
            if "subdomain_mapping" in config:
                for subdomain, subconfig in config["subdomain_mapping"].items():
                    full_domain = f"{domain}.{subdomain}"
                    tool_mapping["domain_tool_mapping"][full_domain] = {
                        "primary_tools": subconfig["tools"],
                        "specialist": config["specialist_model"],
                        "voice": subconfig.get(
                            "voice_preference", config["voice_preference"]
                        ),
                        "training_emphasis": subconfig["training_emphasis"],
                    }

            # Map specialists
            tool_mapping["specialist_routing"][config["specialist_model"]] = {
                "primary_domain": domain,
                "voice_preference": config["voice_preference"],
                "capabilities": config["primary_tools"],
            }

            # Map voice preferences
            tool_mapping["voice_preferences"][config["voice_preference"]] = {
                "domains": [domain],
                "use_case": self._get_voice_use_case(config["voice_preference"]),
            }

        # Save configuration
        config_path = self.base_path / "domain_tool_mapping.json"
        with open(config_path, "w") as f:
            json.dump(tool_mapping, f, indent=2)

        print(f"🔧 Created tool mapping: {config_path}")
        return tool_mapping

    def _get_tool_definitions(self) -> Dict[str, Any]:
        """Define all tools used across academic domains."""
        return {
            # Mathematical tools
            "calculator": {"type": "computational", "output": "numerical"},
            "graphing": {"type": "visual", "output": "chart"},
            "latex_renderer": {"type": "formatting", "output": "mathematical_notation"},
            "equation_solver": {
                "type": "computational",
                "output": "step_by_step_solution",
            },
            # Visual tools
            "diagram_create": {"type": "visual", "output": "diagram"},
            "image_analyzer": {"type": "analytical", "output": "visual_analysis"},
            "color_palette": {"type": "design", "output": "color_scheme"},
            # Text tools
            "text_analyzer": {"type": "analytical", "output": "text_analysis"},
            "writing_assistant": {
                "type": "generative",
                "output": "writing_suggestions",
            },
            "grammar_checker": {"type": "analytical", "output": "grammar_corrections"},
            # Research tools
            "timeline_creator": {
                "type": "organizational",
                "output": "chronological_display",
            },
            "map_generator": {"type": "visual", "output": "geographic_visualization"},
            "primary_source_analyzer": {
                "type": "analytical",
                "output": "source_analysis",
            },
            # Scientific tools
            "data_analyzer": {
                "type": "computational",
                "output": "statistical_analysis",
            },
            "simulation_runner": {
                "type": "interactive",
                "output": "simulation_results",
            },
            "lab_guide": {"type": "procedural", "output": "step_by_step_instructions"},
            # Language tools
            "translator": {"type": "linguistic", "output": "translation"},
            "pronunciation_guide": {"type": "audio", "output": "phonetic_guidance"},
            "culture_guide": {"type": "informational", "output": "cultural_context"},
        }

    def _get_voice_use_case(self, voice: str) -> str:
        """Get use case description for voice preference."""
        voice_cases = {
            "jarvis": "Analytical and authoritative for math, science, and factual content",
            "amy": "Conversational and warm for creative and language subjects",
            "alan": "Clear and explanatory for instructional content",
            "spanish_native": "Native Spanish pronunciation for language learning",
            "french_native": "Native French pronunciation for language learning",
            "italian_native": "Native Italian pronunciation for language learning",
        }
        return voice_cases.get(voice, "General educational content")

    def generate_training_templates(self):
        """Generate training data templates for each domain."""
        templates_dir = self.base_path / "training_templates"
        templates_dir.mkdir(exist_ok=True)

        template_content = self._create_training_template()

        for domain in self.domain_config.keys():
            domain_template = templates_dir / f"{domain}_training_template.jsonl"
            with open(domain_template, "w") as f:
                # Create sample entries for this domain
                for i in range(3):
                    sample = template_content.copy()
                    sample["domain"] = domain
                    sample["example_id"] = f"{domain}_sample_{i+1}"
                    f.write(json.dumps(sample) + "\n")

            print(f"📋 Created training template: {domain_template}")

    def _create_training_template(self) -> Dict[str, Any]:
        """Create training data template structure."""
        return {
            "example_id": "unique_identifier",
            "domain": "academic_domain",
            "subdomain": "specific_subject_area",
            "user_input": "student_question_or_request",
            "tool_classification": {
                "primary_category": "tool_category",
                "tools_needed": ["list", "of", "required", "tools"],
                "specialist_required": "phi3_specialist_model",
                "confidence": 0.95,
                "voice_preference": "appropriate_voice",
                "parameters": {"domain_specific_params": "value"},
            },
            "specialist_response": {
                "explanation": "detailed_educational_response",
                "tool_calls": [{"tool": "tool_name", "parameters": {"param": "value"}}],
                "follow_up_questions": ["question1", "question2"],
                "learning_objectives": ["objective1", "objective2"],
            },
            "metadata": {
                "difficulty_level": "beginner|intermediate|advanced",
                "learning_style": "visual|auditory|kinesthetic|reading",
                "assessment_type": "formative|summative|diagnostic",
                "curriculum_alignment": "state_standards_reference",
            },
        }


def main():
    """Set up the complete academic domain structure."""
    print("🎓 Setting Up Academic Domain Structure")
    print("=" * 50)

    organizer = AcademicDomainOrganizer()

    # Create folder structure
    print("\n📁 Creating folder structure...")
    organizer.create_folder_structure()

    # Generate README files
    print("\n📝 Generating domain documentation...")
    organizer.generate_domain_readme_files()

    # Create tool mapping configuration
    print("\n🔧 Creating tool mapping configuration...")
    tool_mapping = organizer.create_tool_mapping_config()

    # Generate training templates
    print("\n📋 Generating training templates...")
    organizer.generate_training_templates()

    print("\n🎉 Academic Domain Structure Complete!")
    print("=" * 50)
    print(f"✅ {len(organizer.domain_config)} major domains configured")

    total_subdomains = sum(
        len(config.get("subdomain_mapping", {}))
        for config in organizer.domain_config.values()
    )
    print(f"✅ {total_subdomains} subdomains organized")

    total_tools = len(tool_mapping["tool_definitions"])
    print(f"✅ {total_tools} specialized tools mapped")

    print("\n📚 Domains created:")
    for domain, config in organizer.domain_config.items():
        subdomain_count = len(config.get("subdomain_mapping", {}))
        print(f"  • {domain}: {subdomain_count} subdomains")

    print("\n🚀 Ready for domain-specific training data generation!")


if __name__ == "__main__":
    main()
