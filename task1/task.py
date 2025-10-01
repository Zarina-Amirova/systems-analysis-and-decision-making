import numpy as np

with open("task0/task2.csv", "r", encoding="utf-8") as f:
    graph_input = f.read().split("\n")
#print(graph_input)
import numpy as np

def main(graph_list: list[str]) -> None:
   
    edges = []
    vertices = set()
    for line in graph_list:
        line = line.strip()
        if line:
            a, b = line.split(',')
            v1, v2 = int(a), int(b)
            edges.append((v1, v2))
            vertices.add(v1)
            vertices.add(v2)
    
    vertices = sorted(vertices)
    n = len(vertices)
    idx = {v: i for i, v in enumerate(vertices)}

    #Прямое управление
    M1 = np.zeros((n, n), dtype=int)
    for v1, v2 in edges:
        i, j = idx[v1], idx[v2]
        M1[i, j] = 1

    #Прямое подчинение 
    M2 = M1.T

    #Опосредованное управление 
    T = M1.copy()
    for k in range(n):
        for i in range(n):
            if T[i, k]:
                T[i] = np.logical_or(T[i], T[k]).astype(int)
    
    M3 = T - M1
    np.fill_diagonal(M3, 0)
    M3 = np.clip(M3, 0, 1)

    #Опосредованное подчинение 
    M4 = M3.T

    #Соподчинение
    M5 = np.zeros((n, n), dtype=int)
    for i in range(n):
        for j in range(n):
            if i != j and np.any(M1[:, i] & M1[:, j]):
                M5[i, j] = 1

    
    def print_matrix(mat: np.ndarray, title: str) -> None:
        print(f"\n{title}")
        print("   ", " ".join(f"{v:>2}" for v in vertices))
        for i, row in enumerate(mat):
            print(f"{vertices[i]:>2}:", " ".join(f"{x:>2}" for x in row))

    
    print("Вершины:", vertices)
    print_matrix(M1, "1) Прямое управление")
    print_matrix(M2, "2) Прямое подчинение")
    print_matrix(M3, "3) Опосредованное управление")
    print_matrix(M4, "4) Опосредованное подчинение")
    print_matrix(M5, "5) Соподчинение")

main(graph_input)
