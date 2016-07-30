class InterestingTrend():
	def __init__(self, title, description):
		self.title = title
		self.description = description
	def to_dict(self):
		return {
			'title': self.title,
			'description': self.description
		}