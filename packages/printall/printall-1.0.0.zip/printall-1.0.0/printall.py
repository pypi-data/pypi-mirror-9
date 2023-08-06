def printall(a):
    for i in a:
        if isinstance(i,list):
            printall(a);
        else:
            print(i);

        
