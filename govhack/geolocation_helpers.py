import StringIO
import sklearn.neighbors
from sklearn.externals import joblib
import numpy

from . import cache


def get_kdtree(coordinates, use_cache=True):
	"""
	Takes an iterable set of coordinate pairs, 
	and creates a kdtree from them. May use cache.
	"""

	numpy_coords = numpy.array(coordinates)

	kdtree_cached_str = cache.get("kdtree_cached")

	kdtree_cached_file = StringIO.StringIO()

	if kdtree_cached and use_cache:
		#Use cached version
		kdtree_cached_file.write(kdtree_cached_str)
		try:
			return joblib.load(kdtree_cached_file)
		except:
			#Reset the file and build a new model
			kdtree_cached_file = StringIO.StringIO()

	#Build new model
	kdtree = sklearn.neighbors.KDTree(numpy_coords)
	joblib.dump(kdtree, kdtree_cached_file)
	cache.set("kdtree_cached", kdtree_cached_file.getvalue())

	return kdtree


