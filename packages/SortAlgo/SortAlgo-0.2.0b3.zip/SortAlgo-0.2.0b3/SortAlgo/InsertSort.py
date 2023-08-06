def insert_sort(datalist):
	'''
	insert sort
# small -> big
	http://www.stoimen.com/blog/2012/02/13/computer-algorithms-insertion-sort/

	input list should be the same type: int, float, double, long etc

	time complexity
	O(n2)
	'''
	for i in range(1,len(datalist)): #assume the first item doesn't need any sorting
		tmp = datalist[i]
		j=i
		while j>0 and datalist[j-1] > tmp:
			datalist[j] = datalist[j-1] 
			j-=1
		datalist[j] = tmp
	
	return datalist
