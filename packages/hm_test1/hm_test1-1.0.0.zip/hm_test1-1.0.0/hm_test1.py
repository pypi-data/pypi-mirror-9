def fun1(each_list):
	for x in each_list:
		if isinstance(x,list):
			fun1(x)
		else:
			print(x)