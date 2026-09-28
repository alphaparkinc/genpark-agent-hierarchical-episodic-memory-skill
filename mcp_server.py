import sys, json
from client import AgentHierarchicalEpisodicMemory

def main():
    engine = AgentHierarchicalEpisodicMemory()
    for line in sys.stdin:
        line = line.strip()
        if not line: continue
        try:
            req = json.loads(line)
            method = req.get("method")
            rid = req.get("id")
            params = req.get("params", {})

            if method == "tools/list":
                res = {
                    "tools": [
                        {"name": "set_working_memory", "description": "Set working memory.", "inputSchema": {"type": "object", "properties": {"key": {"type": "string"}, "value": {"type": "string"}}, "required": ["key", "value"]}},
                        {"name": "record_turn", "description": "Record turn.", "inputSchema": {"type": "object", "properties": {"role": {"type": "string"}, "content": {"type": "string"}}, "required": ["role", "content"]}},
                        {"name": "recall", "description": "Recall memories.", "inputSchema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}},
                        {"name": "run_benchmark_hierarchical_memory", "description": "Run self-test.", "inputSchema": {"type": "object"}}
                    ]
                }
            elif method == "tools/call":
                tname = params.get("name")
                args = params.get("arguments", {})
                if tname == "set_working_memory":
                    out = engine.set_working_memory(args.get("key"), args.get("value"))
                elif tname == "record_turn":
                    out = engine.record_turn(args.get("role", "user"), args.get("content", ""))
                elif tname == "recall":
                    out = engine.recall(args.get("query", ""))
                elif tname == "run_benchmark_hierarchical_memory":
                    out = engine.run_benchmark_hierarchical_memory()
                else:
                    out = {"error": f"Unknown tool {tname}"}
                res = {"content": [{"type": "text", "text": json.dumps(out)}]}
            else:
                res = {"error": "Unsupported method"}
            print(json.dumps({"jsonrpc": "2.0", "id": rid, "result": res}), flush=True)
        except Exception as e:
            print(json.dumps({"jsonrpc": "2.0", "error": {"code": -32603, "message": str(e)}}), flush=True)

if __name__ == "__main__":
    main()
