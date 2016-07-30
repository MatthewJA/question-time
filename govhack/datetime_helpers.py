import arrow


def get_hansard_range(datestring):
	#Get datetime aware date object in arrow
	dt = arrow.get(datestring)
	return [x.format('YYYY-MM-DDTHH:mm:ss') for x in dt.span('day')]



