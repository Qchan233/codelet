from collections import defaultdict

graph = {
    0: [1, 6, 7, 8],
    1: [2, 5],
    2: [3, 4],
    3: [1],
    4: [5],
    5: [1],
    6: [7],
    7: [4],
    8: [7],
}

graph2 = {
    6: [5, 4],
    5: [1],
    4: [2, 3],
    1: [2],
    2: [1, 3],
    3: [2],
}

def rpo_dfs(graph, start):
    visited = set()
    postorder = []

    def dfs(u):
        visited.add(u)
        for v in graph.get(u, []):
            if v not in visited:
                dfs(v)
        postorder.append(u)

    dfs(start)
    return list(reversed(postorder))

def naive_dom(graph, start):
    dom = {node: {node} if node == start else set(graph.keys()) for node in graph}
    changed = True
    rpo = rpo_dfs(graph, start)

    preds = defaultdict(list)
    for u in graph:
        for v in graph[u]:
            preds[v].append(u)

    print(preds)

    while changed:
        changed = False
        for n in rpo:
            if n == start:
                continue
            new_dom = set(graph.keys())
            for p in preds[n]:
                new_dom &= dom[p]
            new_dom.add(n)
            if new_dom != dom[n]:
                dom[n] = new_dom
                changed = True
    
    return dom

def compute_idom_kooper(graph, start):
    """
    Keith–Cooper Simple Fast Dominators
    graph: dict[node] -> list[node]  (successors)
    start: entry node
    """

    # ---------- build predecessors ----------
    preds = defaultdict(list)
    for u, vs in graph.items():
        for v in vs:
            preds[v].append(u)

    # ---------- DFS to get postorder ----------
    visited = set()
    postorder = []

    postorder_num = {}
    def dfs(u):
        visited.add(u)
        for v in graph.get(u, []):
            if v not in visited:
                dfs(v)
        postorder_num[u] = len(postorder)
        postorder.append(u)

    dfs(start)

    # reverse postorder (skip start later)
    rpo = list(reversed(postorder))

    # ---------- helpers ----------
    idom = {start: start}

    def intersect(u, v):
        while u != v:
            while postorder_num[u] < postorder_num[v]:
                u = idom[u]
            while postorder_num[v] < postorder_num[u]:
                v = idom[v]
        return u

    # ---------- main loop ----------
    changed = True
    while changed:
        changed = False
        for n in rpo:
            if n == start:
                continue

            # only consider predecessors whose idom is known
            preds_with_idom = [p for p in preds[n] if p in idom]
            if not preds_with_idom:
                continue

            new_idom = preds_with_idom[0]
            for p in preds_with_idom[1:]:
                new_idom = intersect(p, new_idom)

            if n not in idom or idom[n] != new_idom:
                idom[n] = new_idom
                changed = True

    idom[start] = None
    return idom

idom = compute_idom_kooper(graph, 0)

for n in sorted(idom):
    print(f"dom({n}) = {idom[n]}")