import sys
"""indent指示是否缩进，level指示缩进的层次，out指示输出的设备，默认为屏幕 """
def print_list(the_list,indent=False,level=0,out=sys.stdout):
    for each_item in the_list:
        if isinstance(each_item,list):
            print_list(each_item,indent,level+1,out)
        else:
            for num in range(level):
                print("\t",end='',file=out)
            print(each_item,file=out)
