"""module prints all elements within nested lists"""

"""if an element is a list, it is returned to the function to 'unpack' one level
deeper"""

import sys

def printitems(data, indent=True, level=0, dest=sys.stdout):
    for item in data:
        if isinstance(item, list):
            printitems(item, indent, level + 1, dest)
        else:
            if indent:
                for tabstop in range(level):
                    print("\t", end='', file=dest)
            print(item, file=dest)
            



        


        

