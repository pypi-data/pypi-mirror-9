"""This is module which include one function preety_print() which
print nested list"""
def preety_print(a,space=0):
    """Display nested list in a printable fashion"""
    for i in a:
        if isinstance(i,list):
            preety_print(i,space+4)
        else:
            print(" "*space,i)

