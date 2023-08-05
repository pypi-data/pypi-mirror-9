class Diagram(object):
    INF = float('inf')

    def __init__(self):
        self._intervals = []
        self._finite_intervals = None
        self._infinite_intervals = None
        self._min_finite = self.INF
        self._max_finite = float(0)

    def __call__(self, shrink_to=None):
        def interval_sort_key(interval):
            b, d = interval
            return (d - b, b,)

        self._finite_intervals = sorted([ (b,d) for b, d in self._intervals if not d == self.INF ], key=interval_sort_key)
        self._infinite_intervals = sorted([ (b, d) for b, d in self._intervals if d == self.INF ], key=interval_sort_key)
        if shrink_to:
            self._finite_intervals = self._finite_intervals[-shrink_to:]
            self._infinite_intervals = self._infinite_intervals[-shrink_to:]

        if self._finite_intervals:
            self._min_finite = min(d for d,_ in self._finite_intervals)
            self._max_finite = max(d for _,d in self._finite_intervals)

    def __getitem__(self, idx):
        return self._intervals[idx]

    @classmethod
    def read_from(cls, fileobj, shrink_to=None):
        diagram = cls()
        for line in fileobj:
            b, d = map(float, line.split())
            diagram.add_interval((b, d,))
        diagram(shrink_to)
        return diagram

    def add_interval(self, interval):
        self._intervals.append(interval)

    def __len__(self):
        return len(self._intervals)

    def __getitem__(self, idx):
        return self._intervals[idx]

    @property
    def max(self):
        return self._max_finite

    @property
    def min(self):
        return self._min_finite

    @property
    def finite_intervals(self):
        return self._finite_intervals

    @property
    def infinite_intervals(self):
        return self._infinite_intervals
