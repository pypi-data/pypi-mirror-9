"""this function can list all in some lists;
"""
def lol(listall,level):
    for i in listall:
      if isinstance(i,list):
         lol(i,level+1)	 
      else:  
         for tab_stop in range(level):
           print("\t",end='')
         print(i)

