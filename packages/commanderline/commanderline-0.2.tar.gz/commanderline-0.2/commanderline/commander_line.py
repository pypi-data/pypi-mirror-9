#!/usr/bin/env python3

import sys
import inspect
import getopt
import ast

def represents_int(s):
	try:
		int(s)
		return True
	except ValueError:
		return False

def represents_float(s):
	try:
		float(s)
		return True
	except ValueError:
		return False

def represents_bool(s):
	if s == 'True' or s == 'False':
		return True
	else:
		return False

def parse_bool(s):
	if s == 'True':
		return True
	elif s == 'False':
		return False
	else:
		return bool(s)

def represents_none(s):
	if s == 'None':
		return True
	else:
		return False

def represents_complex_datatype(s):
	try:
		parsed=ast.literal_eval(s)
	except:
		return False

	return True

def parse_complex_datatype(s):
	'''Assumes s has been tested to not raise exception'''
	return ast.literal_eval(s)
 
def try_to_parse_v0_1(s):
	if represents_int(s):
		return int(s)
	elif represents_float(s):
		return float(s)
	elif represents_bool(s):
		return parse_bool(s)
	elif represents_none(s):
		return None
	else: 
		return s

def try_to_parse_v0_2(s):
	if represents_complex_datatype(s):
		return parse_complex_datatype(s)
	else: 
		return s

def try_to_parse(s):
	return try_to_parse_v0_2(s)

def fill_in_defaults(options, spec):
	num_defaults = 0
	if spec[3] is not None:
		num_defaults = len(spec[3])
		if num_defaults > 0:
			diff = len(spec[0]) - num_defaults
			for i in range(0, num_defaults):
				options[spec[0][diff+i]] = spec[3][i]

def print_func_args(f, comment=''):
	print(str(f.__name__)+comment)

	spec = inspect.getargspec(f)

	defaults = {}
	fill_in_defaults(defaults, spec)

	for o in spec[0]:
		print_default = ''
		if o in defaults:
			print_default = '='+repr(defaults[o])
		print('  --'+o+print_default)

def print_funcs(funcs):
	for i, f in enumerate(funcs):
		if i==0:
			comment = ' [default]'
		else:
			comment = ''

		# print(str(f.__name__)+comment)

		print_func_args(f, comment)

	# print('* denotes default function')

def parse_list_from_cmd_line(in_list):
    split_list = in_list.split(',')
    final_list = [int(e) for e in split_list]
    return final_list

def print_opt_arg_error():
    print('For help use --help')
    return(2)

def commander_line(funcs, print_done=True, squash_return_value=True, argv=None, print_argv_to_output=True, help_prints_args=True):
	'''# Commander Line (for Python 3)
	commander_line(funcs, print_done=True, squash_return_value=True, argv=None, print_argv_to_output=True, help_prints_args=True)

Commander Line makes any python function accessible from the command-line with just 2 lines of code.

It will take any function (from the current scope) as a parameter and expose the function's parameters to the command line as long arguments (i.e., --param_name).

Best-effort parsing of the parameters is performed. Currently supported data types are:

	1.  int
	2.  float
	3.  complex
	4.  bool
	5.  None
	6.  dict
	7.  list
	8.  set
	9.  tuple
	10. str

# Installation
	
	$ pip install commanderline

# Usage

Just import Commander Line as follows:

	import commanderline.commander_line as cl

...and include the following line at the end of your .py file (replace 'function_name' with your function):

	cl.commander_line(function_name) if __name__ == '__main__' else None

# Example

## test.py 

	#!/usr/bin/env python3
	
	import commanderline.commander_line as cl

	def add(v1, v2):
	  \'''Add two values v1 and v2 \'''
	  print(str(v1)+' + '+str(v2)+' = '+str(v1+v2))

	def subtract(v1, v2):
	  \'''Subtract v2 from v1 \'''
	  print(str(v1)+' - '+str(v2)+' = '+str(v1-v2))

	def union(s1, s2):
		\'''Union of s1 and s2 \'''
		print(str(s1)+' | '+str(s2)+' = '+str(s1|s2))

	cl.commander_line([add, subtract, union]) if __name__ == '__main__' else None	

## run / output

	$ ./test.py --v1 5 --v2 4
	Run parameters: ./test.py --v1 5 --v2 4
	5 + 4 = 9
	Done

	$ ./test.py -f subtract --v1 5 --v2 4
	Run parameters: ./test.py -f subtract --v1 5 --v2 4
	5 - 4 = 1
	Done

	./test.py -f union --s1="{1,2,3}" --s2="{2,3,4}"
	Run parameters: ./test.py -f union --s1={1,2,3} --s2={2,3,4}
	{1, 2, 3} | {2, 3, 4} = {1, 2, 3, 4}
	Done

	$ ./test.py -h
	Run parameters: ./test.py -h
	Add two values v1 and v2
	add arguments (and defaults if defined):
	  --v1
	  --v2

	$ ./test.py -f subtract -h
	Run parameters: ./test.py -f subtract -h
	Subtract v2 from v2
	subtract arguments (and defaults if defined):
	  --v1
	  --v2

	$ ./test.py -f union -h
	Run parameters: ./test.py -f union -h
	Union of s1 and s2
	union arguments (and defaults if defined):
	  --s1
	  --s2

	$ ./test.py -l
	Run parameters: ./test.py -l
	Exported functions:
	add [default]
	  --v1
	  --v2
	subtract
	  --v1
	  --v2
	union
	  --s1
	  --s2

# Details

Commander Line respects default values defined by your function and will use them when needed (i.e., when arguments are missing).

By default, it will print out the command line arguments, return 0, and print 'Done' when your function has finished. This behaviour can be controlled with the print_argv_to_output, squash_return_value, and print_done parameters (respectively).

Your function's __doc__ string will be printed when either of the -h and --help arguments are provided. A summary of its parameters and defaults will also be printed (existence of summary can be controlled with help_prints_args).

If you provide a list or tuple of functions instead of a single function, you can specify which one to call from the command line with the -f <func_name> argument. If none is specified, the first element in the tuple/list is taken as default.

List functions that are exported (and their command line arguments) with -l

P.S. Adding: 

	#!/usr/bin/env python3

as your shebang line will provide a nice and portable run environment for your new command-line tool
	'''
	
	if argv is None:
		argv = sys.argv

	if print_argv_to_output:
		print('Run parameters: '+(' '.join(argv)))

	if not isinstance(funcs, (list, tuple)):
		funcs = (funcs,)

	# Manually pre-parse command line options in search of function name (a chicken-and-egg problem: the function name defines the rest of the arguments, but getopt needs all arguments defined beforehand)
	# Get function name to call, before any other arg parsing is done

	func_ind = 0 # set default function
	for arg_ind, v in enumerate(argv):
		if v == '-f': # Found function definition!
			if arg_ind+1 < len(argv): # ...and a function name (hopefully) exists after it!
				func_name = argv[arg_ind+1]

				# Search for the provided function name in the function list
				found_arg_function_not_found = True
				for i, f in enumerate(funcs):
					if f.__name__ == func_name:
						func_ind = i
						found_arg_function_not_found = False
						break
				
				# If the provided function name is not found - error & exit
				if found_arg_function_not_found:
					print('Error: Specified function not found!')
					return print_opt_arg_error()	
			else:
				print('Error: Irregular parameter convention. Don\'t know what to do. Eject, eject!')
				return print_opt_arg_error()

			break		

	func = funcs[func_ind]

	spec = inspect.getargspec(func)

	# print(spec)

	# Add extra options that are OK, but bypassed
	extra_options = {'short':'f', 'short_getopt':'f:'}
	loop_options_extra = ('-'+extra_options['short'])

	# Set help options
	help_options = {'short':'h', 'short_getopt':'h', 'long':'help', 'long_getopt':'help'}
	loop_options_help = ('-'+help_options['short'], '--'+help_options['long'])

	# set list options
	list_options = {'short':'l', 'short_getopt':'l'}
	loop_options_list = ('-'+list_options['short'])

	# all getopt short options
	getopt_short_options = help_options['short_getopt']+extra_options['short_getopt']+list_options['short_getopt']

    # Prepare options for getopt()
	getopt_options_default = [help_options['long_getopt']]

	getopt_options_user = spec[0].copy()
	getopt_options_user = [o+'=' for o in getopt_options_user]

	getopt_options = getopt_options_default.copy()
	getopt_options.extend(getopt_options_user)

	# Prepare opts for lookup in loop
	loop_options = spec[0].copy()
	loop_options = {'--'+o for o in loop_options}

	# Prepare opts and values for function call
	unwrap_options = {}

	# Fill in defaults	
	fill_in_defaults(unwrap_options, spec)

	# ...the block below has been replaced by the function called above...

	# num_defaults = 0
	# if spec[3] is not None:
	# 	num_defaults = len(spec[3])
	# 	if num_defaults > 0:
	# 		diff = len(spec[0]) - num_defaults
	# 		for i in range(0, num_defaults):
	# 			unwrap_options[spec[0][diff+i]] = spec[3][i]

	# Get all other options
	try:
	    opts, args = getopt.getopt(argv[1:], getopt_short_options, getopt_options)
	except getopt.error as msg:
	    print(msg)
	    return print_opt_arg_error()

	# Process options
	for o, a in opts:
	    if o in loop_options_help:
	        print(func.__doc__)
	        if help_prints_args:
	        	print_func_args(func, ' arguments (and defaults if defined):')
	        return 0
	    elif o in loop_options:
	    	unwrap_options[o.lstrip('-')] = try_to_parse(a)
	    elif o in loop_options_extra:
	    	# Do nothing, these should have already been parsed
	    	pass
	    elif o in loop_options_list:
	    	print('Exported functions: ')
	    	print_funcs(funcs)
	    	return 0
	    else:
	        print('Error: Unkown option '+o)
	        return print_opt_arg_error()

	# verification
	for k in spec[0]:
	    if k not in unwrap_options:
	        print('Error: Missing flag: '+k)
	        return print_opt_arg_error()

	return_value = func(**unwrap_options)

	if print_done:
		print('Done')

	if squash_return_value:
		return 0
	else:
		return return_value

if __name__ == '__main__':
	commander_line((commander_line,), print_argv_to_output=False, help_prints_args=False)
