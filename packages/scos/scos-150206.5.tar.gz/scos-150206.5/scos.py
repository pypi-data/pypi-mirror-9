def testlist():
	x = ['gta', ['locations', ['gi', ['subnets', ['10.10.1.0/24', ['.1 router', '.222 avaya']]], 'rc', 'bh']], 'ppl', ['locations', ['gi', 'sterling', 'jerome']]]
	print(x)

def list2outline(the_list, root_level=1):
	for each_item in the_list:
		if isinstance(each_item, list):
			list2outline(each_item, root_level+1)
		else:
			for indent_level in range(root_level):
				print("  ", end='')
			print('*', each_item)
