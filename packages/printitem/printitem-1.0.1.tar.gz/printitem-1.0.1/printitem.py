"""This is a modules that includes some useful funtions"""

def printitem (listin, level):
    """printitem(listin) print the item if it is not a list"""
    if isinstance(listin, list):

        for each_item in listin:
            printitem(each_item, level + 1)
    else:
		for n in range(level):
			print('\t', end='')
        print(listin)
