def merge_sort(datalist):
	'''
	explanation: http://www.stoimen.com/blog/2012/03/05/computer-algorithms-merge-sort/
	animation: http://www.sorting-algorithms.com/merge-sort
	'''
	def merge(left, right): 
		'''
		merge left and right list
		'''
		ret = []
		i = j = 0
		while(i<len(left) and j<len(right)):
			if left[i] < right[j]:
				ret.append(left[i])
				i += 1
			else:
				ret.append(right[j])
				j += 1
		ret.extend(left[i:])
		ret.extend(right[j:])
		return ret
		
	if len(datalist)<=1:
		return datalist
		
	left = datalist[0: len(datalist)/2]
	right = datalist[len(datalist)/2: len(datalist)]
	left = merge_sort(left)
	right = merge_sort(right)
	
	return merge(left, right)
