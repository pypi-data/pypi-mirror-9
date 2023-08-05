import numpy as np

class Cluster(object):
    """
    Class to find distinct clusters.

    Class Metods:

	n_distnict(self, y): the number of distinct clusters
	cluster_sizes(self, y): the sizes of each cluster in a numpy ndarray
	get_members(self, y, cinx): the indeces of members of a particular cluster cinx

    """

    def __init__(self, X=None, y=None):
        self.X = X
        self.y = y
        self.n = y.shape[0]

    def set_data(self, X, y):
        self.X = X
        self.y = y
        self.n = y.shape[0]

    def n_distinct(self):
	"""
	Returns  the number of distinct clusters.
	"""
        return(np.unique(self.y).shape[0])

    def cluster_sizes(self):
	"""
	Returns the sizes of each cluster in a numpy ndarray.
	"""
	tup = np.unique(self.y, return_counts = T)
	return(np.asarray(tup).T)

    def _get_members(self, cinx):
	"""
	Returns a numpy array for the indecies of all 
	members for a specific cluster indexed by cinx.
	
	"""
	allindx = np.arange(0, self.n)
	return (allindx[self.y == cinx])
        

    def _get_non_members(self, cinx):
	"""
	Returns a numpy array for the indecies of all
	data points that DO NOT belong to cluster cinx.

	"""
	allindx = np.arange(0, self.n)
	return (allindx[self.y != cinx])

    def distance(self, i, j, method='euclidean'):
        x1 = self.X[i]
        x2 = self.X[j]
        if method == 'euclidean':
            diff = x1 - x2
            sq_diff = diff * diff
            return(np.sqrt(np.sum(sq_diff)))
        elif method == 'editdist':
            return(editdist.distance(x1, x2))

    def _num_singletons(self, indicator=-1):
	"""Finding the number of singletons
	   specified by indicator [default=-1]
	"""
        return (np.sum(self.y == indicator))

    def summary(self, sing_indicator=-1):
        """ Gives a summary statistics on clusters.
	"""
	print ("Number of singletons: %d"%(self._num_singletons(sing_indicator)))
	print ("Number of clusters: %d"%(self.n_distinct()))

	return (None)
