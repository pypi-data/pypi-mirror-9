#!/usr/bin/env python
import sys, argparse, logging, os, subprocess

# Box syncing
BP_DIR = os.path.expanduser("~") + '/.boilerplate/'

try:
	input = raw_input
except NameError:
	pass

def call_command(command):
	logging.debug("Executing " + command)
	comm = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
	return comm.communicate()

def init():
	logging.basicConfig(level = logging.DEBUG,
		format = "%(asctime)s %(levelname)-8s %(message)s",
		datefmt = "%m-%d %H:%M",
		filename = BP_DIR + "boilerplate.log",
		filemode = "w")
	console = logging.StreamHandler()

	# INFO or higher goes to console
	console.setLevel(logging.INFO)
	formatter = logging.Formatter("%(levelname)-8s %(message)s")
	console.setFormatter(formatter)

	logging.getLogger("").addHandler(console)

	logging.debug("Using Python version " + sys.version)

def handleNew(name, boilerplate):
	bp_path = BP_DIR + name

	if os.path.isdir(bp_path):
		# Boilerplate with that name already exists
		logging.debug(bp_path + " already exists. Asking to overwrite...")

		res = ""
		while res != "y" and res != "n":
			res = input("Boilerplate '" + name + "' already exists. "
			            "Do you want to replace its contents? (y/n) ")
			res = res.lower()

		if res == "n":
			logging.debug("Overwrite denied. Aborting")
			return
		else:
			logging.debug("Overwrite approved. Deleting " + bp_path)
			call_command("rm -rf " + bp_path)

	assert not os.path.isdir(bp_path)
	call_command("mkdir -p " + bp_path)

	boilerplate = os.path.abspath(boilerplate)
	logging.debug("Creating new boilerplate '" + name + "' from " + boilerplate)

	if os.path.isdir(boilerplate):
		boilerplate += "/*"

	command = "cp -r " + boilerplate + " " + bp_path
	call_command(command)

	assert os.path.isdir(bp_path)
	logging.debug("Boilerplate created!")

def handleUse(name):
	bp_path = BP_DIR + name

	if os.path.isdir(bp_path):
		logging.debug("Using boilerplate '" + name + "'")
		command = "cp -r " + bp_path + "/*" + " ."
		call_command(command)
	else:
		logging.error("No boilerplate with the name '" + name + "'  was found!")

def handleList():
	(stdout, stderr) = call_command("ls -d " + BP_DIR + "*/")

	names = stdout.split()
	nameCount = len(names)
	idx = 0
	
	for line in names:
		idx += 1

		line = line.decode("utf-8")
		if line.startswith(BP_DIR):
			line = line[len(BP_DIR):-1]

		print(line)

def handleDelete(name):
	bp_path = BP_DIR + name

	if os.path.isdir(bp_path):
		logging.debug("Deleting boilerplate '" + name + "'")
		command = "rm -r " + bp_path
		call_command(command)
	else:
		logging.error("No boilerplate with the name '" + name + "'  was found!")

	assert not os.path.isdir(bp_path)

def parseargs():
	parser = argparse.ArgumentParser()

	subparsers = parser.add_subparsers()

	new_parser = subparsers.add_parser(
		"new", help="Create a new boilerplate or overwrite an existing one")
	new_parser.add_argument(
		"name", type=str, help="The name under which to save this boilerplate")
	new_parser.add_argument(
		"files", type=str, help="The file or directory to save as the boilerplate")
	new_parser.set_defaults(mode="new")

	use_parser = subparsers.add_parser(
		"use", help="Insert existing boilerplate in the current directory")
	use_parser.add_argument(
		"name", type=str, help="The name of the boilerplate to use")
	use_parser.set_defaults(mode="use")

	list_parser = subparsers.add_parser(
		"list", help="List the available boilerplates")
	list_parser.set_defaults(mode="list")

	delete_parser = subparsers.add_parser(
		"delete", help="Delete a boilerplate")
	delete_parser.add_argument(
		"name", type=str, help="The name of the boilerplate to delete")
	delete_parser.set_defaults(mode="delete")

	return parser.parse_args()

def main():
	args = parseargs()
	init()

	if args.mode is None:
		logging.error("Mode must be provided. Use --help for more information.")
		return

	if args.mode is "new":
		handleNew(args.name, args.files)
	elif args.mode is "use":
		handleUse(args.name)
	elif args.mode is "list":
		handleList()
	elif args.mode is "delete":
		handleDelete(args.name)
	else:
		logging.error("Invalid mode")

