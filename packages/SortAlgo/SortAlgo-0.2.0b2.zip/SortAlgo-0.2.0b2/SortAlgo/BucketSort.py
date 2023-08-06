def bucket_sort(datalist, bin_sz=10):
	''' also called bin sort
	bubble sort in often used to enhance existing sorting algo, although itself can be used to sort all items
	algo: https://www-927.ibm.com/ibm/cas/hspc/student/algorithms/BucketSort.html
	def: http://en.wikipedia.org/wiki/Bucket_sort
	'''
	if not datalist:
		return []
		
	small = min(datalist)
	big = max(datalist)
	buckets = [ ]
	res = []
	#create # bin
	for i in range(bin_sz):
		buckets.append([])
	#append each item to all bins
	for i in datalist:
		buckets[(i-small)*bin_sz/(big-small+1)].append(i)
	
	for i in range(bin_sz):
		if len(buckets[i])>1:
			buckets[i] = bucket_sort(buckets[i])
	
	for i in range(bin_sz):
		res.extend(buckets[i])
	
	return res
	
