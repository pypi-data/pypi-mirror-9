def msniper(inputlist):
	for each_item in inputlist:
		if isinstance(each_item,list):
			msniper(each_item);#this is a critcal point to work
		else:
		    print(each_item);
