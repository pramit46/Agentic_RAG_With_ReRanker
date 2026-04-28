# 🔀 Fusion Ranking Explained

## What is Fusion Ranking?

**Fusion Ranking** (also called **Reciprocal Rank Fusion** or RRF) is a technique for combining search results from multiple retrieval systems into a single, unified ranking.

### The Problem It Solves

When you have multiple search methods (like Vector Search, BM25, and Graph Search), each produces its own ranked list with different scoring mechanisms:

```
Vector Search Results:          BM25 Results:               Graph Results:
1. Doc A (score: 0.95)          1. Doc B (score: 2.8)      1. Doc C (score: 0.4)
2. Doc B (score: 0.82)          2. Doc A (score: 1.2)      2. Doc A (score: 0.3)
3. Doc D (score: 0.71)          3. Doc E (score: 0.9)      3. Doc B (score: 0.2)
```

**Challenge:** These scores aren't directly comparable!
- Vector similarity: 0-1 range
- BM25: Unbounded positive values
- Graph: Custom scoring

You can't just merge by score because they use different scales.

## How Reciprocal Rank Fusion (RRF) Works

### The Formula

```
RRF_score(doc) = Σ (1 / (k + rank_i))
```

Where:
- `k` = constant (usually 60)
- `rank_i` = position of document in result list i
- `Σ` = sum across all result lists

### Step-by-Step Example

**Input: 3 retrieval methods**

```
Vector Search:     BM25:             Graph:
1. Doc A           1. Doc B          1. Doc C
2. Doc B           2. Doc A          2. Doc A
3. Doc D           3. Doc E          3. Doc B
```

**Calculate RRF scores:**

For **Doc A**:
- Vector rank: 1 → 1/(60+1) = 0.0164
- BM25 rank: 2 → 1/(60+2) = 0.0161
- Graph rank: 2 → 1/(60+2) = 0.0161
- **Total: 0.0486**

For **Doc B**:
- Vector rank: 2 → 1/(60+2) = 0.0161
- BM25 rank: 1 → 1/(60+1) = 0.0164
- Graph rank: 3 → 1/(60+3) = 0.0159
- **Total: 0.0484**

For **Doc C**:
- Vector rank: not found → 0
- BM25 rank: not found → 0
- Graph rank: 1 → 1/(60+1) = 0.0164
- **Total: 0.0164**

For **Doc D**:
- Vector rank: 3 → 1/(60+3) = 0.0159
- BM25 rank: not found → 0
- Graph rank: not found → 0
- **Total: 0.0159**

**Final Ranking:**
1. Doc A (0.0486) ← Appeared high in all 3
2. Doc B (0.0484) ← Also appeared in all 3
3. Doc C (0.0164) ← Only in graph search
4. Doc D (0.0159) ← Only in vector search

## Why RRF is Powerful

### 1. **Scale-Invariant**
✅ Works with any scoring system
✅ No need to normalize scores
✅ Rank position matters, not absolute scores

### 2. **Consensus Building**
✅ Documents appearing in multiple sources get higher scores
✅ Rewards consistency across retrieval methods
✅ Reduces impact of outliers

### 3. **Simple & Effective**
✅ No machine learning required
✅ No training data needed
✅ Proven to work well in practice

### 4. **Robust**
✅ Handles missing documents gracefully (score = 0)
✅ Not affected by score inflation in any single method
✅ Works with any number of retrieval sources

## In Your Agentic RAG System

### Implementation

Located in [`agent.py`](agent.py) in the `_fusion_ranking()` method:

```python
def _fusion_ranking(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # Group documents by source
    source_rankings = {}
    for doc in documents:
        source = doc.get("source", "unknown")
        if source not in source_rankings:
            source_rankings[source] = []
        source_rankings[source].append(doc)
    
    # Sort each source's results by score
    for source in source_rankings:
        source_rankings[source] = sorted(
            source_rankings[source],
            key=lambda x: x.get("score", 0),
            reverse=True
        )
    
    # Calculate RRF scores
    k = 60  # RRF constant
    rrf_scores = {}
    
    for doc in documents:
        doc_text = doc.get("text", "")
        if doc_text not in rrf_scores:
            rrf_scores[doc_text] = {"score": 0, "doc": doc}
        
        # Find rank in source
        source = doc.get("source", "unknown")
        if source in source_rankings:
            rank = source_rankings[source].index(doc) + 1
            rrf_scores[doc_text]["score"] += 1 / (k + rank)
    
    # Return sorted by RRF score
    return sorted(
        [data["doc"] for data in rrf_scores.values()],
        key=lambda x: rrf_scores[x.get("text", "")]["score"],
        reverse=True
    )
```

### Your Retrieval Pipeline

```
┌─────────────────────────────────────────────────────────┐
│ QUERY: "What is RAG?"                                   │
└─────────────────────────────────────────────────────────┘
                         ↓
        ┌────────────────┼────────────────┐
        ↓                ↓                ↓
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Vector DB    │  │ BM25         │  │ Graph DB     │
│ (Semantic)   │  │ (Keywords)   │  │ (Relations)  │
│              │  │              │  │              │
│ 5 results    │  │ 4 results    │  │ 3 results    │
└──────────────┘  └──────────────┘  └──────────────┘
        │                │                │
        └────────────────┼────────────────┘
                         ↓
           ┌─────────────────────────┐
           │  FUSION RANKING (RRF)   │
           │  Combines 12 results    │
           │  → 8 unique documents   │
           └─────────────────────────┘
                         ↓
           ┌─────────────────────────┐
           │  HITL RE-RANKING        │
           │  Applies learned prefs  │
           └─────────────────────────┘
                         ↓
           ┌─────────────────────────┐
           │  FINAL TOP 10 RESULTS   │
           └─────────────────────────┘
```

## Benefits in Your System

### 1. **Multi-Method Synergy**
- Vector Search: Captures semantic meaning
- BM25: Finds exact keyword matches
- Graph Search: Discovers related concepts
- **Fusion**: Gets the best of all three!

### 2. **Quality Documents Rise to Top**
- If a document is relevant semantically AND has keywords AND is connected in the graph
- → It will rank very high after fusion

### 3. **Reduces False Positives**
- A document that only scores high in ONE method (might be noise)
- → Will rank lower after fusion
- Documents scoring well in MULTIPLE methods (likely relevant)
- → Will rank higher

### 4. **Complements HITL Re-ranking**
- Fusion provides initial good ranking
- HITL re-ranking then boosts based on user preferences
- Together: Very powerful!

## Alternatives to RRF

### Other Fusion Methods:

1. **Score Normalization + Weighted Sum**
   - Normalize all scores to 0-1
   - Combine: `final = w1*vector + w2*bm25 + w3*graph`
   - ❌ Requires tuning weights
   - ❌ Sensitive to score distributions

2. **CombSUM**
   - Simply add normalized scores
   - ❌ Requires careful normalization
   - ❌ Affected by score inflation

3. **Borda Count**
   - Similar to RRF but uses `(N - rank)` instead of `1/(k+rank)`
   - ✅ Works well
   - ❌ Slightly less robust to outliers

4. **Learning to Rank (LTR)**
   - Train ML model to combine scores
   - ✅ Can be very effective
   - ❌ Needs training data
   - ❌ More complex

### Why We Use RRF

✅ **No hyperparameters to tune** (except k, which works well at 60)
✅ **No training data needed**
✅ **Simple to understand and implement**
✅ **Proven effective in research and production**
✅ **Handles any number of sources**

## Real-World Impact

### Without Fusion (using only Vector Search):
```
Query: "What is RAG?"
Results: Semantically similar docs, but might miss exact keyword matches
```

### With Fusion (Vector + BM25 + Graph):
```
Query: "What is RAG?"
Results: 
  ✓ Semantically similar (from Vector)
  ✓ Contains "RAG" keyword (from BM25)
  ✓ Connected to related concepts (from Graph)
  → Much better coverage!
```

## References

- **Original RRF Paper**: Cormack, G. V., Clarke, C. L., & Buettcher, S. (2009). "Reciprocal rank fusion outperforms condorcet and individual rank learning methods"
- **Used By**: Elasticsearch, Vespa, many hybrid search systems
- **Research**: Consistently outperforms single-method retrieval by 10-40%

## See It In Action

Run the demo:
```bash
./venv/bin/python demo_retrieval.py
```

You'll see:
1. Individual results from each source
2. Combined results after fusion
3. How documents from multiple sources rank higher

---

**Bottom Line:** Fusion Ranking makes your multi-source retrieval system work as a unified, intelligent whole rather than separate parts. It's why your system can find the BEST documents, not just "good" documents from each individual method.
