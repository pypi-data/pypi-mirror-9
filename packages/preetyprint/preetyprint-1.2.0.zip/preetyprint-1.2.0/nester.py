"""This is module which include one function preety_print() which
print nested listwith each item in new line."""
def preety_print(the_list,indent=False,level=0):
    """Display content of nested list, each item in new line.
specify optional indentation and level."""
    for i in the_list:
        if isinstance(i,list):
            preety_print(i,indent,level+1)
        else:
            if indent:
                print("\t"*level,end=' ')
            print(i)

