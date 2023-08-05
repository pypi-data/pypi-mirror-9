"""This is a module to print a list of lists. 
It accepts two arguments: the list itself, and 
the indentation level you would like"""
def printListOfLists(the_list, indentationLevel=-1):
  for each_item in the_list:
    if isinstance(each_item, list):
      printListOfLists(each_item, indentationLevel+1)
    else:
      for tab_stop in range(indentationLevel):
        print("\t", end='')
      print(each_item)

