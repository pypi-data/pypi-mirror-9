
def human(size):
	radix = 1024.
	units = ["B", "KB", "MB", "GB", "TB"]
	n = len(units)
	for u in range(n):
		if size < radix : break
		size /= radix

	return "%f %s" % (size, units[u])
