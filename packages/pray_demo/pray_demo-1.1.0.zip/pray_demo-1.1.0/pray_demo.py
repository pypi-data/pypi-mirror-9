__author__ = 'Administrator'
def print_list(move,level=0):
    for each_move in move:
        if isinstance(each_move,list):
            print_list(each_move,level+1)
        else:
            print(each_move)