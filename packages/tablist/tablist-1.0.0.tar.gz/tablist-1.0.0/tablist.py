

def print_lol(the_list,indent_flag=False,level=0):
    for each_item in the_list:
        if isinstance(each_item ,list): # if data = list, then repeat the function 
            print_lol(each_item,indent_flag,level+1)
        else:
            if(indent_flag):
                for spacing in range(level):#repeat as per level
                    print("\t",end="")
            #print tab
            print(each_item)# write data if item is not a list
