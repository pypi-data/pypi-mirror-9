"""print a python list"""
def printList(myList):
	for a in myList:
		if(isinstance(a,list)):
			printList(a)
		else:
			print(a)