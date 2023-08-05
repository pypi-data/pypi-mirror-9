def msniper(inputlist,tabneed=0,level=0):
  for each_item in inputlist:
    if isinstance(each_item,list):
      msniper(each_item,tabneed,level+1);
    else:
      if tabneed:
          for tab_num in range(level):
              print("\t",end='');
      print(each_item);
