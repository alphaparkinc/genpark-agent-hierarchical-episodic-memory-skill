import sys
import json
import re
import time
from collections import Counter

class HierarchicalMemoryEngine:
    def __init__(self, short_term_cap=8, mid_term_cap=30):
        self.short_term = []
        self.mid_term = []
        self.long_term = []
        self.short_term_cap = short_term_cap
        self.mid_term_cap = mid_term_cap

    def add_event(self, content, importance=1.0):
        event = {
            "id": f"evt_{len(self.short_term) + len(self.mid_term) + len(self.long_term) + 1}",
            "content": content,
            "importance": float(importance),
            "timestamp": time.time()
        }
        self.short_term.append(event)
        if len(self.short_term) > self.short_term_cap:
            overflow = self.short_term.pop(0)
            self._promote_to_mid(overflow)
        return event

    def _promote_to_mid(self, event):
        self.mid_term.append(event)
        if len(self.mid_term) > self.mid_term_cap:
            overflow = self.mid_term.pop(0)
            if overflow.get("importance", 0) >= 0.7:
                self.long_term.append(overflow)

    def retrieve(self, query, top_k=5):
        all_events = self.short_term + self.mid_term + self.long_term
        if not all_events:
            return []
        tokens_q = set(re.findall(r"\w+", query.lower()))
        scored = []
        for e in all_events:
            tokens_e = Counter(re.findall(r"\w+", e["content"].lower()))
            overlap = sum(tokens_e[t] for t in tokens_q if t in tokens_e)
            score = overlap * e.get("importance", 1.0)
            scored.append((score, e))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored[:top_k] if item[0] > 0]

    def get_stats(self):
        return {
            "short_term_count": len(self.short_term),
            "mid_term_count": len(self.mid_term),
            "long_term_count": len(self.long_term)
        }

engine = HierarchicalMemoryEngine()

def handle_rpc(request):
    method = request.get("method")
    req_id = request.get("id")
    params = request.get("params", {})

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": "add_memory_event",
                        "description": "Store an episodic event with an importance weight.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "content": {"type": "string"},
                                "importance": {"type": "number", "default": 1.0}
                            },
                            "required": ["content"]
                        }
                    },
                    {
                        "name": "retrieve_memories",
                        "description": "Retrieve memories matching a semantic search query.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string"},
                                "top_k": {"type": "integer", "default": 5}
                            },
                            "required": ["query"]
                        }
                    },
                    {
                        "name": "inspect_memory_tiers",
                        "description": "Get count and summary of items in memory tiers.",
                        "inputSchema": {"type": "object", "properties": {}}
                    }
                ]
            }
        }

    if method == "tools/call":
        name = params.get("name")
        args = params.get("arguments", {})
        if name == "add_memory_event":
            evt = engine.add_event(args.get("content", ""), args.get("importance", 1.0))
            return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": json.dumps(evt)}]}}
        elif name == "retrieve_memories":
            res = engine.retrieve(args.get("query", ""), int(args.get("top_k", 5)))
            return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": json.dumps(res)}]}}
        elif name == "inspect_memory_tiers":
            stats = engine.get_stats()
            return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": json.dumps(stats)}]}}

    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Method not found"}}

if __name__ == "__main__":
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            resp = handle_rpc(req)
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
        except Exception as e:
            sys.stdout.write(json.dumps({"jsonrpc": "2.0", "error": {"code": -32000, "message": str(e)}}) + "\n")
            sys.stdout.flush()
