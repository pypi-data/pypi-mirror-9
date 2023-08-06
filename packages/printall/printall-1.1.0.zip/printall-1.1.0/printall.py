
movie = ['sge','58','tyj',['456','yyy','ooo',['123sdf','457fgh','789hjk']]]
def printall(a,level):
    for i in a:
        if isinstance(i,list):
            printall(i,level);
        else:
            for num in range(level):
                print('\t',end='')
            print(i);
            
            


        
