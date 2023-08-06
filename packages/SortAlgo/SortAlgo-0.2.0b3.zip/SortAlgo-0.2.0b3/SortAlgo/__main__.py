

import sys
import random
import time
import getopt

from .BucketSort import bucket_sort
from .ShellSort import shell_sort
from .InsertSort import insert_sort

DEFAULT_SIZE = 100

def test(fn, size = DEFAULT_SIZE, debug = True):
    if size<10:
        size = DEFAULT_SIZE;

    vals = [10+i for i in range(size)]
    random.shuffle(vals)
    if debug:
        print 'Before sort', vals[:5], '...', vals[-5:]
    vals = fn(vals)
    if debug:
        print 'After sort' , vals[:5], '...', vals[-5:]

def main():
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

main()	