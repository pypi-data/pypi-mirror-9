"""This is module which include one function preety_print() which
print nested listwith each item in new line."""
import sys
def preety_print(the_list,indent=False,level=0,fh=sys.stdout):
    """Display content of nested list, each item in new line.
    specify optional indentation and level."""
    for i in the_list:
        if isinstance(i,list):
            preety_print(i,indent,level+1,file=fh)
        else:
            if indent:
                print("\t"*level,end=' ',file=fh)
            print(i)

