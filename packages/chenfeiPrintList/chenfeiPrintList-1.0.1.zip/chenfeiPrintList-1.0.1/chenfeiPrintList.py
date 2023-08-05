def printList(mylist, num=0):
	for a in mylist:
		if(isinstance(a, list)):
			for b in range(num):
				print("\t", end=" ")
			printList(a, num)
		else:
			print(a,end=" ")