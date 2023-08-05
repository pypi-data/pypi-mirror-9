'''
Created on 5 Dec 2013

@author: Akul Mathur
'''

typ = (list, tuple)

def flattenlist(d):
    thelist = []
    for x in d:
        if not isinstance(x, typ):
            thelist += [x]
        else:
            thelist += flattenlist(x)
    return thelist


if __name__ == '__main__':
    pass