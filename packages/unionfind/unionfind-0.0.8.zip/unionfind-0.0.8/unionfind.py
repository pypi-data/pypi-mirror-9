class unionfind:
	def __init__(self, n):
		self.parent = list(range(n))
	def find(self, i):
		if self.parent[i] != i: self.parent[i] = self.find(self.parent[i])
		return self.parent[i]
	def unite(self, i, j):
		i = self.find(i)
		j = self.find(j)
		if i != j: self.parent[i] = j
	def issame(self, i, j):
		return self.find(i) == self.find(j)
	def groups(self):
		r = range(len(self.parent))
		return [[j for j in r if self.issame(j, i)] for i in r if i == self.parent[i]]
