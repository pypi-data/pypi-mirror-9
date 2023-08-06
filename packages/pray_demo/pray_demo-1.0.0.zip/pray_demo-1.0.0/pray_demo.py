__author__ = 'Administrator'
def print_list(move):
    for each_move in move:
        if isinstance(each_move,list):
            print_list(each_move)
        else:
            print(each_move)