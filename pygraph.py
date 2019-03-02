from collections import deque


class AdjList:
    def __init__(self, vertices=None):
        assert isinstance(vertices, list), "vertices are not complaint with the list type"
        self._vertices = vertices if vertices else []
        self._edges = dict()
        self._list = [deque()] * len(vertices) if vertices else []

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

    def bfs(self, v, *, pre=None, post=None):
        assert v < len(self._vertices), "{0} invalid index".format(v)

        pre = pre if pre else lambda u: u
        post = post if post else lambda u: u
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

            post(u)

    def dfs(self, *, pre=None, post=None, order=None):
        pre = pre if pre else lambda u: u
        post = post if post else lambda u: u
        order = order if order else lambda vx: [i for i in range(len(vx))]
        visited = [False] * len(self._vertices)

        def visit(u):
            visited[u] = True
            pre(u)

            for w in self._list[u]:
                if not visited[w]:
                    visited[w] = True
                    visit(w)

            post(u)

        for v in order(self._vertices):
            if not visited[v]:
                visit(v)

    def transpose(self):
        transposed = AdjList(self._vertices)

        for u, lst in enumerate(self._list):
            for v in lst:
                transposed.add_edge(v, u, self.edge((u, v)))

        return transposed

    def _kosaraju(self):

        if len(self._vertices) == 0:
            return

        def post_counter():
            c = 0
            post = [0] * len(self._vertices)

            def visit(v):
                nonlocal c
                post[c] = v
                c += 1

            return post, visit

        post, func = post_counter()
        self.dfs(post=func)

        G = self.transpose()

        components = []
        component = []

        def pre(v):
            nonlocal components, component
            component.append(v)

        def post_order(vx):
            nonlocal components, component
            for v in reversed(post):
                if len(component) != 0:
                    components.append(component)
                    component = []
                yield v

        G.dfs(pre=pre, order=post_order)
        return components

    def connected_components(self, method=None):
        methods = {'kosaraju': self._kosaraju, 'torjana': None}
        method = method if method else list(methods.keys())[0]
        func = methods.get(method, None)
        assert func, "Unknown method {0}".format(method)
        return func()

    def topological_sort(self):
        def post_counter():
            c = 0
            post = [0] * len(self._vertices)

            def visit(v):
                nonlocal c
                post[c] = v
                c += 1

            return post, visit

        post, func = post_counter()
        self.dfs(post=func)
        return list(reversed(post))