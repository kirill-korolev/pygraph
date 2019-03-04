from collections import deque
from functools import wraps


def counter(func):
    counter.c = 0

    @wraps(func)
    def inner(*args, **kwargs):
        result = func(*args, **kwargs)
        counter.c += 1
        return result
    return inner


class AdjList:
    def __init__(self, vertices=None):
        assert isinstance(vertices, list), "vertices are not complaint with the list type"
        self._vertices = vertices if vertices else []
        self._edges = dict()
        self._list = [deque() for _ in vertices] if vertices else []

    def add_vertex(self, v):
        self._vertices.append(v)
        self._list.append(deque())
        return len(self._vertices) - 1

    def add_edge(self, u, v, edge=None):
        V = len(self._vertices)
        assert u < V and v < V, "({0}, {1}) invalid pair of indices".format(u, v)
        self._list[u].append(v)
        self._edges[u, v] = edge if edge else 1
        return u, len(self._list[u]) - 1

    def vertex(self, v):
        assert v < len(self._vertices), "{0} invalid index".format(v)
        return self._vertices[v]

    def edge(self, e):
        assert isinstance(e, tuple), "edge index must be tuple"
        edge = self._edges.get(e, None)
        assert edge, "{0} invalid index".format(e)
        return edge

    def vertices(self):
        return self._vertices

    def edges(self):
        return self._list

    def bfs(self, v, *, pre=None, post=None, edge=None):
        assert v < len(self._vertices), "{0} invalid index".format(v)

        pre = pre if pre else lambda u: u
        post = post if post else lambda u: u
        edge = edge if edge else lambda e: e
        visited = [False] * len(self._vertices)
        q = deque([v])

        visited[v] = True

        while len(q) > 0:
            u = q.popleft()
            pre(u)

            for w in self._list[u]:
                if not visited[w]:
                    q.append(w)
                    visited[w] = True
                    edge((u, w))

            post(u)

    def dfs(self, *, pre=None, post=None, order=None, edge=None):
        pre = pre if pre else lambda u: u
        post = post if post else lambda u: u
        order = order if order else lambda vx: [i for i in range(len(vx))]
        edge = edge if edge else lambda e: e
        visited = [False] * len(self._vertices)

        def visit(u):
            visited[u] = True
            pre(u)

            for w in self._list[u]:
                if not visited[w]:
                    visited[w] = True
                    edge((u, w))
                    visit(w)

            post(u)

        for v in order(self._vertices):
            if not visited[v]:
                visit(v)

    def reversed_edges(self):

        pre = [0] * len(self._vertices)
        post = [0] * len(self._vertices)
        edges = set()

        @counter
        def pre_visit(v):
            pre[v] = counter.c

        @counter
        def post_visit(v):
            post[v] = counter.c

        def edge(e):
            edges.add(e)

        self.dfs(pre=pre_visit, post=post_visit, edge=edge)
        not_visited = set(self._edges.keys()) - edges
        rev_edges = []

        for (u, v) in not_visited:
            if pre[v] < pre[u] < post[u] < post[v]:
                rev_edges.append((u, v))

        return rev_edges

    def has_cycle(self):
        return len(self.reversed_edges()) > 0

    def transpose(self):
        transposed = AdjList(self._vertices)

        for u, lst in enumerate(self._list):
            for v in lst:
                transposed.add_edge(v, u, self.edge((u, v)))

        return transposed

    def _kosaraju(self):

        if len(self._vertices) == 0:
            return []

        post = [0] * len(self._vertices)

        @counter
        def post_visit(v):
            post[counter.c] = v

        self.dfs(post=post_visit)
        G = self.transpose()

        components = []
        component = set()

        def pre(v):
            nonlocal components, component
            component.add(v)

        def order(vx):
            nonlocal components, component
            for v in reversed(post):
                if len(component) != 0:
                    components.append(component)
                    component = set()
                yield v

        G.dfs(pre=pre, order=order)
        return components

    def _tarjan(self):
        if len(self._vertices) == 0:
            return []

        pre = [-1] * len(self._vertices)
        low = [-1] * len(self._vertices)
        on_stack = [False] * len(self._vertices)
        stack = []
        components = []
        c = 0

        def visit(u):
            nonlocal c
            pre[u] = c
            low[u] = c
            stack.append(u)
            on_stack[u] = True
            c += 1

            for w in self._list[u]:
                if pre[w] == -1:
                    visit(w)
                    low[u] = min(low[u], low[w])
                else:
                    if on_stack[w]:
                        low[u] = min(low[u], pre[w])

            if low[u] == pre[u]:
                component = set()

                while True:
                    w = stack.pop()
                    on_stack[w] = False
                    component.add(w)

                    if w == u:
                        break

                components.append(component)

        for v in range(len(self._vertices)):
            if pre[v] == -1:
                visit(v)

        return components

    def connected_components(self, method=None):
        methods = {"kosaraju": self._kosaraju, "tarjan": self._tarjan}
        method = method if method else list(methods.keys())[1]
        func = methods.get(method, None)
        assert func, "Unknown method {0}".format(method)
        return func()

    def topological_sort(self):

        post = [0] * len(self._vertices)

        @counter
        def post_visit(v):
            post[counter.c] = v

        self.dfs(post=post_visit)
        return list(reversed(post))