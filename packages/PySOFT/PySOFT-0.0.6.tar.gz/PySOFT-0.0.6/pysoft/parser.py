import collections
import gzip


class Column(object):
	def __init__(self, name, desc):
		self.name = name
		self.description = desc

	def __repr__(self):
		return self.name

class Row(object):
	""" Allow data access via column name and column index
	"""

	def __init__(self, col_names, row):
		self.dict = collections.OrderedDict([(col, row[i]) for i, col in enumerate(col_names)])
		self.keys = list(self.dict.keys())

	def __getitem__(self, key):
		if isinstance(key, int):
			return self.dict[self.keys[key]]
		elif isinstance(key, str):
			return self.dict[key]
		else:
			raise TypeError('Only int and string allowed for indexing')

	def __setitem__(self, key, item):
		if isinstance(key, int):
			self.dict[self.keys[key]] = item
		elif isinstance(key, str):
			self.dict[key] = item
		else:
			raise TypeError('Only int and string allowed for indexing')

	def __iter__(self):
		return iter(self.dict.values())

	def __len__(self):
		return len(self.dict)

class SOFTFile(object):
	def __init__(self, fname, skip_data=False):
		self.header = {}
		self.columns = []
		self.data = []

		if fname.endswith('.gz'):
			with gzip.open(fname, 'rb') as fd:
				self.content = str(fd.read(), encoding='utf8')
		else:
			with open(fname, 'r') as fd:
				self.content = fd.read()

		self.parse(skip_data)

	def parse(self, skip_data):
		section = None
		dataset = None
		get_kv = lambda f: (f[0].strip()[1:], f[1].strip())

		for line in self.content.split('\n'):
			fields = line.split('=')

			if line.startswith('^'):
				section = fields[0].strip().lower()[1:]

				if section == 'dataset':
					dataset = fields[1].strip()

					if not 'dataset' in self.header:
						self.header['dataset'] = {}
						self.header['dataset']['name'] = dataset
						self.header['dataset']['subsets'] = []
				elif section == 'subset':
					self.header['dataset']['subsets'].append({})
				else:
					self.header[section] = {}
			elif line.startswith('!'):
				if '=' in line:
					key, value = get_kv(fields)

					if section == 'subset':
						access = self.header['dataset']['subsets'][-1]
					else:
						access = self.header[section]

					access[key.lower()] = value
			elif line.startswith('#'):
				name, desc = get_kv(fields)

				self.columns.append(Column(name, desc))
			else:
				if skip_data: break

				cols = [c.name for c in self.columns]
				row = line.split('\t')
				if len(row) != len(cols): continue
				if row[0] == self.columns[0].name: continue # table header

				self.data.append(Row(cols, row))
