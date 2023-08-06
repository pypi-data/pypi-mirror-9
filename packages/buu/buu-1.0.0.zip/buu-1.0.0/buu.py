
def print_lol(lista , level):
	for item in lista:
			if isinstance(item, list):
				print_lol(item,level+1)
			else:
				for tab_stop in range(level):
					print("\t", end ="")
				print (item)

