
movie = ['sge','58','tyj',['456','yyy','ooo',['123sdf','457fgh','789hjk']]]
def printall(a,indent=False,level=0):
    for i in a:
        if isinstance(i,list):
            printall(i,indent,level+1);
        else:
            if indent:
                for num in range(level):
                    print('\t',end='')
            print(i);
            
                
                


        
