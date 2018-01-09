import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-v','--verbosity', help='increase output verbosity',action='store_true')
parser.add_argument('square',help='display a square of a given number',type=int)
args = parser.parse_args()
answer = args.square**2
if args.verbosity:
	print "verbose output turned on:"
print answer
