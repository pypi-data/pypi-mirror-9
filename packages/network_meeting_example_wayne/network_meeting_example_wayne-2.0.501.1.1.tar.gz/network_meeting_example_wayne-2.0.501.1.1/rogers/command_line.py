import sys
import getopt

class Command_line():
	def __init__(self):
		self.args = self.opts(sys.argv[1:])
		return

	def opts(self, options):
		shortops = 'i:o:h'
		longops = ['input=', 'output=', 'help']
		opts = getopt.getopt(options, shortops, longops)
		args = {'i': 'test.txt', 'o': 'output.txt', 'h': False}
		
		for (opt, arg) in opts[0]:
			if opt == '-i' or opt == '--input':
				args['i'] = arg
			elif opt == '-o' or opt == '--output':
				args['o'] = arg
			elif opt == '-h' or opt == '--help':
				args['h'] = True 

		return args
