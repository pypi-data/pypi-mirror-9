def quick_sort(datalist):
	'''
	Straight forward method, devide and conquer
	http://www.stoimen.com/blog/2012/03/13/computer-algorithms-quicksort/

	input list should be the same type: int, float, double, long etc

	time complexity: O(n*log(n))
	spapce requires: extra space required
	'''
	if not datalist:
		return []
	
	pivot = datalist[0]
	left = []
	right = []
	for i in range(1, len(datalist)):
		if datalist[i] > pivot:
			right.append(datalist[i])
		elif datalist[i] < pivot:
			left.append(datalist[i])
	return quick_sort(left) + [pivot] + quick_sort(right)		
	
	
	