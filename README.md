# Hierarchical Episodic Memory Skill for Autonomous Agents

[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-blue.svg)](https://modelcontextprotocol.io)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-brightgreen.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Zero External Dependencies](https://img.shields.io/badge/dependencies-zero-success.svg)](requirements.txt)

Hierarchical episodic memory engine tailored for multi-agent autonomous systems. Organizes conversational flow across three tiered tiers: **short-term working memory**, **mid-term session context**, and **long-term high-salience episodic reflections**, using pure Python standard library token frequency scoring.

## Core Capabilities
- **Tiered Memory Promotion**: Automatically promotes high-salience experiences from short-term to mid-term and permanent long-term memory.
- **Pure Stdlib Information Retrieval**: Fast BM25/TF-IDF token overlap scoring without requiring Pinecone, Weaviate, or heavy native C-extensions.
- **Salience Scoring**: Ranks recall items by importance weighting and keyword match density.

## MCP Server Integration
Run standard stdio MCP server:
```bash
python mcp_server.py
```

### Available MCP Tools
- `add_memory_event`: Store an observation with importance weighting (0.0 to 1.0).
- `retrieve_memories`: Semantic retrieval of past events matching queries.
- `inspect_memory_tiers`: Return counts and items across short, mid, and long term tiers.
