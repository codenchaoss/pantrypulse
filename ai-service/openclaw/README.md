# KitchenSync OpenClaw Orchestration Module (Phase 1)

This module establishes the **OpenClaw Foundation** (Phase 1) for KitchenSync's Back-of-House (BOH) automation. It acts as the workflow supervisor that coordinates our independent Python FastAPI microservices into unified automated runs.

## 📂 Project Structure

```
openclaw/
├── config/
│   └── openclaw.json       # Central model environments and default configs
├── agents/
│   └── kitchensync-manager/
│       ├── AGENTS.md        # System execution guidelines
│       ├── SOUL.md          # Persona and tone boundaries (professional, polite, no emojis)
│       ├── IDENTITY.md      # Avatar reference & profile rules
│       ├── TOOLS.md         # Tool calls conventions
│       └── USER.md          # User addressing terms
├── skills/
│   ├── inventory_optimization/
│   │   └── SKILL.md         # Exposes POST /optimization
│   ├── recipe/
│   │   └── SKILL.md         # Exposes POST /recipe
│   ├── menu/
│   │   └── SKILL.md         # Exposes POST /menu
│   ├── pricing/
│   │   └── SKILL.md         # Exposes POST /pricing
│   ├── description/
│   │   └── SKILL.md         # Exposes POST /description
│   └── supplier/
│       └── SKILL.md         # Exposes POST /supplier
├── workflows/
│   └── restaurant_optimization.json # Stage orchestration blueprint
├── services/
│   └── gateway.py           # HTTP Client triggers for Python API endpoints
├── models/
│   └── schemas.py           # Model definitions
├── tests/
│   └── test_foundation.py   # Workspace structure validator
└── README.md                # This documentation
```

## 🤖 KitchenSync Manager Agent
The **KitchenSync Manager** is the agent responsible for kitchen routine orchestration.
- **Vibe**: Organized, logical, efficient, and cost-focused.
- **Tone**: Business professional, polite, clean. Emojis are strictly disabled (`SOUL.md`).
- **Target Operations**: Minimizing waste index percentages, selecting planned specials, generating prices, and drafting supplier orders.

## 🚀 Future Integrations Roadmap
1. **Phase 2 (Skills Integration)**: Map placeholder skills to FastAPI endpoints inside `gateway.py` and implement tool decorators.
2. **Phase 3 (Workflow Orchestration)**: Implement workflow parser execution loop running from inventory updates through daily menu spec listings.
3. **Phase 4 (UI Automation)**: Connect simulated state channels updating Dashboards, Reports, and planners.
4. **Phase 5 (Print Queue)**: Add mock/simulated printer API queues.
5. **Phase 6 (End-to-End Workflow)**: Conduct complete workflow integration from inventory depletion signals to print jobs.
