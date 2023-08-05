def print_lol(the_list, level=0):
        """ 打印列表
作者： 王志军
时间： 2015-02-13 """
        for the_item in the_list:
                if isinstance(the_item,list):
                        print_lol(the_item,level+1)
                else:
                        for tabs in range(level):
                                print("\t",end='')
                        print(the_item)

