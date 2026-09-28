from client import AgentHierarchicalEpisodicMemory
import json

def main():
    mem = AgentHierarchicalEpisodicMemory()
    res = mem.run_benchmark_hierarchical_memory()
    print("Hierarchical Episodic Memory Benchmark Result:")
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    main()
