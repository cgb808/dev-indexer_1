# ZenGlow AI Workspace - Project Index
*Generated: August 29, 2025*

## Top-Level Structure Overview

```
ZenGlowAIWorkspace/                 # Root workspace directory
├── 📁 Core Application Components
│   ├── app/                        # Main FastAPI application (40 Python modules)
│   ├── frontend/                   # Web UI components  
│   ├── infrastructure/             # Deployment configurations
│   └── leonardo_test.wav           # Voice integration test file
│
├── 📁 Fine-Tuning & AI Training
│   ├── fine_tuning/               # Complete training infrastructure
│   │   ├── datasets/              # Specialized training datasets
│   │   │   ├── processed/         # Ready training data
│   │   │   │   ├── drill_down_questioning/     # 648 drill-down examples
│   │   │   │   ├── socratic_method/            # 846 Socratic examples  
│   │   │   │   ├── interruption_handling/      # 71 interruption examples
│   │   │   │   └── pure_methodology/           # 500 methodology examples
│   │   │   └── scripts/           # Dataset generation scripts
│   │   ├── models/                # Trained specialist models
│   │   ├── training/              # Training workflows & scripts
│   │   ├── validation/            # Model validation & testing
│   │   └── tooling/               # LLM-as-Judge coordination tools
│   ├── data/                      # Raw datasets & samples
│   └── models/                    # Model files & downloads
│
├── 📁 Knowledge & Memory Management  
│   ├── artifact/knowledge-graph/  # Versioned knowledge snapshots
│   │   ├── run-20250829-234418/   # Latest snapshot (Aug 29, 2025)
│   │   ├── entities.json          # Knowledge graph entities
│   │   ├── relations.json         # Entity relationships
│   │   └── memory_graph.mmd       # Mermaid diagram
│   ├── memory_snapshot.json       # Current system state
│   └── sql/                       # Database schemas & migrations
│
├── 📁 Operations & DevOps
│   ├── scripts/                   # Automation utilities (7 directories, 70+ files)
│   │   ├── memory-save.mjs        # Knowledge graph snapshots
│   │   ├── memory-restore.mjs     # Snapshot restoration
│   │   └── index_codebase.py      # Project structure indexing
│   ├── docker-compose.yml         # Container orchestration
│   ├── Makefile                   # Build automation
│   ├── docs/devops/               # DevOps docs & backlog (DEVOPS.md, DEVOPS_TODO_HISTORY.md)
│
├── 📁 Documentation & Guides
│   ├── docs/                      # Technical documentation (architecture, memory, etc.)
│   │   ├── ARCHITECTURE_OVERVIEW.md        # System architecture
│   │   ├── MEMORY_RAG_INTEGRATION.md       # Memory + RAG integration (extended)
│   │   ├── integration/MCP_RAG_INTEGRATION.md # MCP integration guide (relocated)
│   │   ├── deployment/PRODUCTION_DEPLOYMENT.md # Deployment guide (relocated)
│   │   ├── security/RLS_POLICY_REFERENCE.md # RLS policy reference (relocated)
│   │   ├── workspace/REMOTE_WORKSPACE_LAYOUT.md # Workspace layout (relocated)
│   │   └── testing/AGENT_TEST_EXECUTION.md  # Test execution (relocated)
│   ├── README.md                  # Project overview
│   └── DOCS_INDEX.md              # Central documentation index
│
├── 📁 Development & Testing
│   ├── tests/                     # Test suites
│   ├── .vscode/                   # VS Code configuration
│   ├── .pytest_cache/             # Test cache
│   └── __pycache__/               # Python cache
│
└── 📁 Archive & Legacy
    ├── archive/                   # Deprecated/moved components
    ├── gemma_phi_ui/             # Legacy UI components
    └── whisper/                   # Audio processing tools
```

## Key Architectural Components

### 🎯 Specialized Models (Fine-Tuned)
- **Socratic Tutor**: 846 examples for question-based learning
- **Drill-Down Expert**: 648 examples for intent probing  
- **Interruption Handler**: 71 examples with [USER_INTERRUPTION] token
- **Base Foundation**: 500 pure methodology + 1,842 personality examples

### 🧠 RAG Integration Layer
- **pgvector Store**: Semantic similarity search
- **Memory Bridge**: MCP Memory → RAG integration
- **Context Retrieval**: Domain-specific knowledge for specialists

### 🏗️ Infrastructure Stack
- **Docker Services**: backend, ollama, redis, webui
- **Model Serving**: Ollama (Mistral 7B, Gemma 2B)
- **Caching**: Redis for performance
- **Voice Integration**: Leonardo TTS/Whisper

### 📊 Current Metrics
- **Python Modules**: 40 active modules
- **Training Examples**: 2,065 total specialized examples ready
- **Docker Services**: 4 services operational
- **Documentation**: 13+ technical documents
- **Memory Snapshots**: Versioned knowledge preservation

## Data Flow Architecture

```
User Input → Model Router → Specialist Selection → RAG Context Retrieval → Specialized Response
     ↓              ↓              ↓                    ↓                      ↓
[Voice/Text] → [Route Logic] → [Expert Model] → [Domain Knowledge] → [Contextual Expert Response]
```

## Recent Developments (August 2025)

**✅ Completed:**
- Fine-tuning infrastructure organization
- Specialized training datasets creation  
- LLM-as-Judge validation framework
- Interruption handling with technical integration
- Voice-enabled Leonardo assistant
- Docker Compose orchestration
- Memory management system updates

**🎯 Next Phase:**
- Model training automation
- Specialist deployment pipeline
- Model router implementation
- Performance monitoring
- Continuous learning feedback loops

---

*This index provides a comprehensive overview of the ZenGlow AI Workspace structure, reflecting the evolution from RAG optimization to specialized AI model training infrastructure.*
