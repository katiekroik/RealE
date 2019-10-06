class Building:

	def __init__(self, price, units):
		self.price = price
		self.units = []
		self.units.append(units)


class Unit:
	def __init__(self, price, sqFt):
		self.price = price
		self.sqFt = sqFt