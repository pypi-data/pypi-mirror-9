def myFun(param, level=0):
	if isinstance(param, list):
		for item in param:
			if isinstance(param,list):
				myFun(item, level+1)
			else:
                                for item_level in range(level):
                                        print("\t",end='')
                                print(item)
	else:
		print(param)

