"""This is a module to print a list of lists"""
def printListOfLists(the_list):
  for each_item in the_list:
    if isinstance(each_item, list):
      printListOfLists(each_item)
    else:
      print(each_item)

