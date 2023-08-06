'''
Most popular and inefficient sort algorithm
http://www.stoimen.com/blog/2012/02/20/computer-algorithms-bubble-sort/

input list should be the same type: int, float, double, long etc

time complexity: O(n2) 
'''	
	
def bubble_sort(datalist):
	''' bubble_sort
	def: http://en.wikipedia.org/wiki/Bubble_sort
	algo: http://www.algolist.net/Algorithms/Sorting/Bubble_sort
	http://interactivepython.org/runestone/static/pythonds/SortSearch/sorting.html
	'''
	for i in range(len(datalist)):
		j = len(datalist) - 1
		while j>i:
			if datalist[j] < datalist[j-1]:
				datalist[j-1] , datalist[j] = datalist[j] , datalist[j-1]
			j-= 1
	return datalist
