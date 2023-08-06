def selection_sort(datalist):
	'''
	selection sorting
	http://www.sorting-algorithms.com/selection-sort
	sorting from min to max

	space: O(1)
	time: O(n^2)
	'''
	if not datalist:
		return []
	
	for i in range(0, len(datalist)):
		for j in range(i+1, len(datalist)):
			if datalist[i] > datalist[j]:
				datalist[i], datalist[j] = datalist[j], datalist[i] #python style swap
				
	return datalist		