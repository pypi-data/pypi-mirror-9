"""this function can list all in some lists;
"""
def lol(listall):
    for i in listall:
      if isinstance(i,list):
          lol(i)	 
      else:  
         print(i)

