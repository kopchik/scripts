#!/usr/bin/env python3
import argparse
import sys

def dprint(*args, **kwargs):
	return
	if not __debug__:
		return
	print(*args, **kwargs)

def read_int(path):
	with open(path) as fd:
		r = fd.readline()
	return int(r)

def write_int(path, value: int):
  with open(path, "r+") as fd:
    fd.write(str(value))

def get_value(value):
	if isinstance(value, int) or isinstance(value, float):
		return value
	if isinstance(value, str):
		if value.isdigit():
			return int(value)
		try:
			return float(value)
		except ValueError:
			pass
		return read_int(value)
	raise Exception("cannot read %s" % value)


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Change brightness, etc')
	parser.add_argument('--min', type=str, default=0, help="Integer value or path to file. Default 0")
	parser.add_argument('--max', type=str, default=100, help="Integer value or path to file. Default 100")
	parser.add_argument('--set', type=str, required=True, help="Where to put new value.")
	parser.add_argument('--actual', type=str, \
		help="Where to get current value. Default is to get current value from --set argument")
	parser.add_argument('val', type=str, nargs=1)
	args = parser.parse_args()
	
	if args.actual:
		actual = read_int(args.actual)
	else:
		actual = read_int(args.set)

	minimum = get_value(args.min)
	maximum = get_value(args.max)
	dprint("actual:", actual, "min:", minimum, "max:", maximum)

	in_percents = False
	val = args.val[0]
	assert val, "Value cannot be empty"
	mult = 1
	eq = False

	if val[-1:] == "%":
		in_percents = True
		val = val[:-1]

	if not val[0].isdigit():
		dprint("prefix:", val[0])
		if val[0] == '-':
			mult = -1
		elif val[0] == '+':
			pass
		elif val[0] == '=':
			eq = True
		else:
			raise Exception("Wrong prefix. Should be -/+/=")
		val = val[1:]

	try:
		val = float(val)
	except ValueError:
		raise Exception("Invalid value. Should be in form [-/+/=]NUM[%]")

	if eq:
		if in_percents:
			new_val = maximum * (val / 100)
		else:
			new_val = val
	else:
		if in_percents:
			new_val = actual * (1+val/100*mult)
		else:
			new_val = actual + val * mult
	dprint("new value:", new_val)

	# set value
	if new_val < minimum:
		new_val = minimum
	if new_val > maximum:
		new_val = maximum
	new_val = int(new_val)
	dprint("new value after normalizing:", new_val)
	write_int(args.set, new_val)
