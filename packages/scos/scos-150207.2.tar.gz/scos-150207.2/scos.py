def list2outline(the_list, wiki_style='doku', root_level=1):
	for each_item in the_list:
		if isinstance(each_item, list):
			list2outline(each_item, wiki_style, root_level+1)
		else:
			if wiki_style == 'doku':
				for indent_level in range(root_level):
					print("  ", end='')
				print('*', each_item)
			elif wiki_style == 'lion':
				for indent_level in range(root_level):
					print("*", end='')
				print(' ', each_item)
			else:
				for indent_level in range(root_level):
					print('\t', end='')
				print(each_item)
