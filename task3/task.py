import json
import numpy as np

def load_json_string(json_str):
    return json.loads(json_str)

def transitive_closure(matrix):
    size = len(matrix)
    closure = matrix.copy()
    for k in range(size):
        for i in range(size):
            for j in range(size):
                closure[i, j] = closure[i, j] or (closure[i, k] and closure[k, j])
    return closure

def extract_clusters(closure_mat):
    n = len(closure_mat)
    visited_flags = [False] * n
    clusters = []

    for i in range(n):
        if not visited_flags[i]:
            cluster = []
            for j in range(n):
                if closure_mat[i, j] and closure_mat[j, i]:
                    cluster.append(j + 1)
                    visited_flags[j] = True
            clusters.append(sorted(cluster))
    
    return clusters

def compare_two_clusters(c1, c2, relation_matrix):
    a = c1[0] - 1
    b = c2[0] - 1
    if relation_matrix[a, b] == 1 and relation_matrix[b, a] == 0:
        return -1
    elif relation_matrix[a, b] == 0 and relation_matrix[b, a] == 1:
        return 1
    else:
        return 0

def main(json_rank1, json_rank2):
    rank1 = load_json_string(json_rank1)
    rank2 = load_json_string(json_rank2)

    all_items = set()
    for ranking in [rank1, rank2]:
        for group in ranking:
            if not isinstance(group, list):
                group = [group]
            all_items.update(group)
    
    if not all_items:
        return json.dumps({"kernel": [], "clustered_ranking": []})

    n_items = max(all_items)

    def create_matrix(ranking):
        positions = [0] * n_items
        current_rank = 0
        for group in ranking:
            if not isinstance(group, list):
                group = [group]
            for item in group:
                positions[item - 1] = current_rank
            current_rank += 1

        mat = np.zeros((n_items, n_items), dtype=int)
        for i in range(n_items):
            for j in range(n_items):
                if positions[i] >= positions[j]:
                    mat[i, j] = 1
        return mat

    M1 = create_matrix(rank1)
    M2 = create_matrix(rank2)

    M12 = M1 * M2
    M1_T = M1.T
    M2_T = M2.T
    M12_prime = M1_T * M2_T

    contradiction_kernel = []
    for i in range(n_items):
        for j in range(i + 1, n_items):
            if M12[i, j] == 0 and M12_prime[i, j] == 0:
                contradiction_kernel.append([i + 1, j + 1])

    P_matrix = np.logical_or(M1 * M2_T, M1_T * M2).astype(int)
    C_matrix = M1 * M2

    for pair in contradiction_kernel:
        i, j = pair[0] - 1, pair[1] - 1
        C_matrix[i, j] = 1
        C_matrix[j, i] = 1

    E_matrix = C_matrix * C_matrix.T
    E_closure = transitive_closure(E_matrix)
    clusters = extract_clusters(E_closure)

    cluster_rel_mat = np.zeros((len(clusters), len(clusters)), dtype=int)
    for i, ci in enumerate(clusters):
        for j, cj in enumerate(clusters):
            if i != j:
                if C_matrix[ci[0]-1, cj[0]-1] == 1:
                    cluster_rel_mat[i, j] = 1

    visited = [False] * len(clusters)
    sorted_order = []

    def dfs_topo(node):
        visited[node] = True
        for neighbor in range(len(clusters)):
            if cluster_rel_mat[node, neighbor] == 1 and not visited[neighbor]:
                dfs_topo(neighbor)
        sorted_order.append(node)

    for idx in range(len(clusters)):
        if not visited[idx]:
            dfs_topo(idx)

    sorted_order.reverse()

    final_ranking = []
    for idx in sorted_order:
        group = clusters[idx]
        if len(group) == 1:
            final_ranking.append(group[0])
        else:
            final_ranking.append(group)

    return json.dumps({
        "kernel": contradiction_kernel,
        "clustered_ranking": final_ranking
    })


if __name__ == "__main__":
    with open("range_a.json", "r", encoding="utf-8") as f:
        rank_a = f.read()
    with open("range_b.json", "r", encoding="utf-8") as f:
        rank_b = f.read()
    with open("range_c.json", "r", encoding="utf-8") as f:
        rank_c = f.read()

    print("Сравнение ранжировок:")

    print("\nrange_a.json vs range_b.json")
    res_ab = main(rank_a, rank_b)
    print(res_ab)

    print("\nrange_a.json vs range_c.json")
    res_ac = main(rank_a, rank_c)
    print(res_ac)

    print("\nrange_b.json vs range_c.json")
    res_bc = main(rank_b, rank_c)
    print(res_bc)
