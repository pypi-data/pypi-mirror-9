
import sys
import random
import time
import getopt

from SortAlgo.BucketSort import bucket_sort
from SortAlgo.ShellSort import shell_sort
from SortAlgo.InsertSort import insert_sort

from TestFunc.py import test


if __name__ == '__main__':
	if len(sys.argv) == 1:
		print """%s sorting_method
		insert_sort
		"""% sys.argv[0]
	else:
		pass

	for i in [globals()[i] for i in globals().keys() if 'sort' in i]:
		begin=time.time()
		print 'testing ', i
		test( i, size=5000)
		print "this sorting takes totally: ", time.time() - begin

	