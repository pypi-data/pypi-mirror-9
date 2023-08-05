def test_list():
	cst = ['gta', ['locations', ['gi', ['subnets', ['10.10.1.0/24', ['.1 router', '.222 avaya']]], 'rc', 'bh']], 'ppl', ['locations', ['gi', 'sterling', 'jerome']]]
	print('cst = ', end='')
	print(cst)

def list2outline(the_list, wiki_style='doku', root_level=1):
	next_item=0
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
			elif wiki_style == 'lionhead':
				for indent_level in range(root_level):
					print("!", end='')
				print(' ', each_item)
			elif wiki_style == 'I':
				out_level = [['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII', 'XIII', 'XIV', 'XV', 'XVI', 'XVII', 'XVIII', 'XIX', 'XX', 'XXI', 'XXII', 'XXIII', 'XXIV', 'XXV', 'XXVI'], ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], ['i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii', 'ix', 'x', 'xi', 'xii', 'xiii', 'xiv', 'xv', 'xvi', 'xvii', 'xviii', 'xix', 'xx', 'xxi', 'xxii', 'xxiii', 'xxiv', 'xxv', 'xxvi'], [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26], ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'], ['aa', 'bb', 'cc', 'dd', 'ee', 'ff', 'gg', 'hh', 'ii', 'jj', 'kk', 'll', 'mm', 'nn', 'oo', 'pp', 'qq', 'rr', 'ss', 'tt', 'uu', 'vv', 'ww', 'xx', 'yy', 'zz'], ['aaa', 'bbb', 'ccc', 'ddd', 'eee', 'fff', 'ggg', 'hhh', 'iii', 'jjj', 'kkk', 'lll', 'mmm', 'nnn', 'ooo', 'ppp', 'qqq', 'rrr', 'sss', 'ttt', 'uuu', 'vvv', 'www', 'xxx', 'yyy', 'zzz']]
				for indent_level in range(root_level):
					print("  ", end='')
				print(out_level[root_level][next_item], '. ', each_item, sep='')
				next_item=next_item+1
			else:
				for indent_level in range(root_level):
					print('\t', end='')
				print(each_item)

