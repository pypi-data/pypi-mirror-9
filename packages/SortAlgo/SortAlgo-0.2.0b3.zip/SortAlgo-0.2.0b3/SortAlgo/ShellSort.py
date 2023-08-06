'''
shell sort: enhanced version of insert. it does quite well for certain circumstances in this example we use doug shell sort

http://www.stoimen.com/blog/2012/02/27/computer-algorithms-shell-sort/


input list should be the same type: int, float, double, long etc
'''	

def shell_sort(datalist):
	gap = len(datalist)/2
	while gap>0:
		for i in range(gap,len(datalist)):
			j= i-gap
			while j>=0 and datalist[j] > datalist[j+gap]:
				datalist[j], datalist[j+gap] = datalist[j+gap], datalist[j]
				j -= gap
		gap /= 2
	return datalist
