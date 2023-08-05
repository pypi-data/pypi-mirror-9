def msniper(inputlist,level):
  for each_item in inputlist:
    if isinstance(each_item,list):
      msniper(each_item,level+1);
    else:
      for tab_num in range(level):
          print("\t",end='')
      print(each_item);
