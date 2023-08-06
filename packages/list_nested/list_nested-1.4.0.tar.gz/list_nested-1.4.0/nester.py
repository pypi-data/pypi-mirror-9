def print_all(lst,indent=False,level=0):
    for line in lst:
        if isinstance(line,list):
            print_all(line,indent,level+1)
        else:
            if indent:
                for tab_stop in range(level):
                    print("\t",end=" ")
                    
            print (line)

