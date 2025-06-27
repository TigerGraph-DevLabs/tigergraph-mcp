from .queries import WCC_QUERY, PAGERANK_QUERY

SUGGEST_ALGORITHMS_PROMPT = """
## Objective

Suggest suitable graph algorithms for the user to run, based on the current TigerGraph schema. Provide a brief explanation of each algorithm’s purpose and when it is applicable.

## Instructions

1. **Inspect the graph schema**:
   - Identify all edge types along with their direction (directed or undirected) and source/target vertex types.

2. **Suggest WCC (Weakly Connected Components)** if:
   - The schema contains at least one undirected edge type.
   - Do not suggest WCC if all edges are directed.

3. **Suggest PageRank** if:
   - There is at least one directed edge type where the source and target node types are the same.
   - Do not suggest PageRank if such edges are not found.

4. Do **not** mention any algorithm that is not applicable. Only include suggested algorithms.

5. For each suggested algorithm, include:
   - The algorithm name
   - A short, user-friendly explanation of what it does
   - The kind of insight or output the user might expect

6. If no algorithms are applicable, reply with a short explanation that nothing is recommended based on current schema.

7. End the message by asking the user to confirm if the suggested algorithms look good, or if they want to revise.

## Output Format

Respond in natural language. Examples:

**If both algorithms are suggested:**
```

Based on your graph structure, I suggest the following algorithms:

✅ **WCC (Weakly Connected Components)**
Helps identify clusters of interconnected nodes based on undirected edges. Useful for finding isolated communities or disconnected parts of your graph.

✅ **PageRank**
Ranks nodes by importance using link structure. Commonly used to find influential or highly connected nodes in a network.

Please confirm if this looks good by replying with "confirmed", "approved", "go ahead", or "ok". Or let me know if you'd like to revise anything.

```

**If only one algorithm is suggested (e.g., WCC):**
```

Based on your graph structure, I suggest the following algorithm:

✅ **WCC (Weakly Connected Components)**
Helps identify clusters of interconnected nodes based on undirected edges. Useful for finding isolated communities or disconnected parts of your graph.

Please confirm if this looks good by replying with "confirmed", "approved", "go ahead", or "ok". Or let me know if you'd like to revise anything.

```

**If no algorithms are applicable:**
```

There are currently no suitable algorithms to run based on the structure of your graph.

Please confirm if this looks good by replying with "confirmed", "approved", "go ahead", or "ok". Or let me know if you'd like to revise anything.

```
"""
EDIT_ALGORITHM_SELECTION_PROMPT = """
## Objective

Revise the algorithm selections (WCC and PageRank) based on the user's feedback and confirm the updated choices.

## Instructions

- First, interpret the user's latest input to adjust the algorithm selection.
  - If the feedback clearly includes or excludes WCC and/or PageRank, update the selection accordingly.
  - If the feedback is ambiguous, incomplete, or includes unsupported algorithms, politely explain that only WCC and PageRank are currently supported.
- Show the updated selection to the user.
- Ask for final confirmation using accepted phrases: "confirmed", "approved", "go ahead", or "ok".

## Output Format

Summarize the final selection for confirmation:

```

Here’s your current selection:

✅ WCC: Yes / No
✅ PageRank: Yes / No

Please confirm to proceed by replying with "confirmed", "approved", "go ahead", or "ok". Or let me know if you'd like to revise anything.

```
"""

RUN_ALGORITHMS_PROMPT = f"""
## Objective

Create, install, and run the selected graph algorithms (WCC and/or PageRank) on the current schema.

## Instructions

1. If no algorithms are selected, do not run any queries.  
   Simply return:  
   "No algorithms were selected. Onboarding is now complete."

2. For each selected algorithm, perform the following steps using tool calls:
   - Use `CREATE_QUERY` with the corresponding GSQL code below.
   - Use `INSTALL_QUERY` to install the query.
   - Use `RUN_QUERY` with the appropriate parameters.

---

### WCC (tg_wcc)

- Only run if the user has confirmed.
- Parameters:
  - `e_type_set`: all undirected edge types
  - `v_type_set`: all node types connected by undirected edges
  - `print_limit`: -1
  - All other parameters should use default values.
- Expected output: number of connected components.

**GSQL Code:**
```

{WCC_QUERY}

```

---

### PageRank (tg_pagerank)

- Only run if the user has confirmed.
- Only run if there exists a valid (`v_type`, `e_type`) pair such that:
  - `e_type` is a directed edge.
  - Both the source and target types of `e_type` are the same and equal to `v_type`.
- Parameters:
  - `v_type`: node type connected by `e_type`
  - `e_type`: directed edge type whose source and target types are both `v_type`
  - All other parameters should use default values.
- Expected output: comprehensive ranking details from `pagerank_top_nodes`.

**GSQL Code:**
```

{PAGERANK_QUERY}

```

## Output Format

```

✅ WCC completed. Top connected components:

✅ PageRank completed. Top-ranked nodes:

✅ All selected algorithms have completed. Onboarding is now complete.

```
"""
