def printList(mylist, num=0):
	for a in mylist:
		if(isinstance(a, list)):
			printList(a, num+1)
		else:
			for b in range(num):
				print("\t",end='')
			print(a)
