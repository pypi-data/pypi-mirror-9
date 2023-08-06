from random import shuffle

DEFAULT_SIZE = 100

def test(fn, size = DEFAULT_SIZE, debug = True):
	'''
	Test function to run each sort function  
	print pre-run result
	and post-run result
	'''
    if size<10:
        size = DEFAULT_SIZE;

    vals = [10+i for i in range(size)]
    shuffle(vals)
    if debug:
        print 'Before sort', vals[:5], '...', vals[-5:]
    vals = fn(vals)
    if debug:
        print 'After sort' , vals[:5], '...', vals[-5:]
