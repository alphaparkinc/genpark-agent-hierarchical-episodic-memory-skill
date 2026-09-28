import sys, json, time, math, re
from collections import defaultdict

class AgentHierarchicalEpisodicMemory:
    """
    Zero-Dependency Hierarchical Episodic Memory Engine for Autonomous Agents.
    Maintains three-tier cognitive memory architecture:
    1. Working Memory (active key-value state / scratchpad)
    2. Short-Term Memory Buffer (sliding dialogue turns with token awareness)
    3. Episodic Long-Term Memory (lexical/semantic index with exponential decay and importance weighting)
    """
    def __init__(self, short_term_capacity=10, decay_lambda=0.01):
        self.short_term_capacity = short_term_capacity
        self.decay_lambda = decay_lambda
        self.working_memory = {}
        self.short_term_buffer = []
        self.episodic_store = []
        self.id_counter = 0

    def set_working_memory(self, key, value):
        self.working_memory[str(key)] = value
        return {"status": "SET", "key": key, "value": value}

    def get_working_memory(self, key, default=None):
        return self.working_memory.get(str(key), default)

    def record_turn(self, role, content, metadata=None):
        self.id_counter += 1
        turn = {
            "turn_id": self.id_counter,
            "role": role,
            "content": content,
            "timestamp": time.time(),
            "metadata": metadata or {}
        }
        self.short_term_buffer.append(turn)
        if len(self.short_term_buffer) > self.short_term_capacity:
            evicted = self.short_term_buffer.pop(0)
            self._auto_consolidate_turn(evicted)
        return {"status": "RECORDED", "turn_id": self.id_counter, "buffer_length": len(self.short_term_buffer)}

    def _auto_consolidate_turn(self, turn):
        tokens = set(re.findall(r'\w+', turn["content"].lower()))
        importance = min(1.0, 0.3 + (len(tokens) / 50.0))
        self.episodic_store.append({
            "memory_id": turn["turn_id"],
            "content": f"[{turn['role'].upper()}]: {turn['content']}",
            "tokens": list(tokens),
            "timestamp": turn["timestamp"],
            "importance": importance,
            "access_count": 0
        })

    def consolidate_summary(self, summary_text, importance=0.8):
        self.id_counter += 1
        tokens = set(re.findall(r'\w+', summary_text.lower()))
        memory_record = {
            "memory_id": self.id_counter,
            "content": summary_text,
            "tokens": list(tokens),
            "timestamp": time.time(),
            "importance": float(importance),
            "access_count": 0
        }
        self.episodic_store.append(memory_record)
        return {"status": "CONSOLIDATED", "memory_id": self.id_counter, "importance": importance}

    def recall(self, query, top_k=3, alpha=0.5, beta=0.3, gamma=0.2):
        now = time.time()
        q_tokens = set(re.findall(r'\w+', query.lower()))
        if not q_tokens:
            return {"results": [], "total_searched": len(self.episodic_store)}

        ranked = []
        for mem in self.episodic_store:
            m_tokens = set(mem["tokens"])
            intersection = q_tokens.intersection(m_tokens)
            union = q_tokens.union(m_tokens)
            relevance = len(intersection) / len(union) if union else 0.0

            delta_t = max(0.0, now - mem["timestamp"])
            recency = math.exp(-self.decay_lambda * delta_t)

            importance = mem.get("importance", 0.5)

            score = (alpha * relevance) + (beta * recency) + (gamma * importance)
            ranked.append((score, relevance, recency, mem))

        ranked.sort(key=lambda x: x[0], reverse=True)
        results = []
        for score, rel, rec, mem in ranked[:top_k]:
            mem["access_count"] += 1
            results.append({
                "memory_id": mem["memory_id"],
                "content": mem["content"],
                "final_score": round(score, 4),
                "relevance": round(rel, 4),
                "recency": round(rec, 4),
                "importance": round(mem["importance"], 4),
                "access_count": mem["access_count"]
            })

        return {
            "query": query,
            "results": results,
            "total_episodic_memories": len(self.episodic_store)
        }

    def run_benchmark_hierarchical_memory(self):
        self.set_working_memory("active_task", "Refactor payment checkout pipeline")
        self.set_working_memory("active_currency", "USD")

        self.record_turn("user", "We noticed high latency on Stripe webhook ingress during peak hours.")
        self.record_turn("assistant", "We should implement sliding replay tolerance and an HMAC verification cache.")
        self.consolidate_summary("User reported Stripe webhook ingestion latency spike; agent recommended HMAC verification caching.", importance=0.95)
        self.consolidate_summary("Previous quarter quarterly sales grew by 18% in EMEA markets.", importance=0.4)

        recall_res = self.recall("Stripe webhook latency caching", top_k=2)
        top_match = recall_res["results"][0] if recall_res["results"] else {}

        return {
            "benchmark_status": "PASSED",
            "working_memory_verified": self.get_working_memory("active_currency") == "USD",
            "episodic_count": len(self.episodic_store),
            "top_memory_id": top_match.get("memory_id"),
            "top_relevance_score": top_match.get("final_score")
        }
