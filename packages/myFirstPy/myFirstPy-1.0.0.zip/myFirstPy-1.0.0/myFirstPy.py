def printAll(my_list):

	for ele in my_list:
		if isinstance(ele,list):
			
			printAll(ele)
		else:
			print(ele)
