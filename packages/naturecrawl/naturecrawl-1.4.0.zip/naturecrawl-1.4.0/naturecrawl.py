def print_lol(the_list, indent=False, level=0, fh=sys.stdout):
        """ 打印列表
作者： 王志军
时间： 2015-02-13 """
        for the_item in the_list:
                if isinstance(the_item,list):
                        print_lol(the_item,indent,level+1,fh)
                else:
                        if indent:
                                for tabs in range(level):
                                        print("\t",end='',file=fh)
                        print(the_item,file=fh)

