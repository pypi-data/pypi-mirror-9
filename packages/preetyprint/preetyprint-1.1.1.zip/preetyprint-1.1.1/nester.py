"""This is module which include one function preety_print() which
print nested list"""
def preety_print(the_list,indent=0):
    """Display nested list in a printable fashion"""
    for i in the_list:
        if isinstance(i,list):
            preety_print(i,indent+1)
        else:
            print("\t"*indent,i)

