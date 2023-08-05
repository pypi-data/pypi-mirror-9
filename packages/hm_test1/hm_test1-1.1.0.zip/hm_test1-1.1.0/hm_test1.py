def fun1(each_list,indent=false,level=0):
	for x in each_list:
		if isinstance(x,list):
			fun1(x,indent,level+1)
		else:
                        if indent:
                                for i in range(level):
                                        print("\t",end='')
                                        
			print(x)
