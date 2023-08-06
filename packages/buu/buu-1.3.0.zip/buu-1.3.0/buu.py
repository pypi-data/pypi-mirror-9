
def print_lol(lista , indent = False, level = 0):
	for item in lista:
			if isinstance(item, list):
				print_lol(item, indent, level+1)
			else:
				if indent:
					for tab_stop in range(level):
						print("\t", end ="")
				print (item)

