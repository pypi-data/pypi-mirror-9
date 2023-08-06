cimport approxidate

def approx(char *date):
	cdef timeval tv
	if approxidate(date, &tv) == -1:
		return -1.0
	return tv.tv_sec + (tv.tv_usec / 1000000.0)
