import copy
target = []
Combina = []
def inner_combination(target, data):
    for i in range(len(data)):
        new_target = copy.copy(target)  # data is type list what you want
        new_data = copy.copy(data)
        new_target.append(data[i])
        new_data = data[i+1:]
        Combina.append(new_target)
        inner_combination(new_target, new_data)
    return Combina

def poper(lists):
    try:
        if 'lists' in locals() or 'lists' in globals():
            for i in range(len(lists)):
                del lists[-1]
        else:
            print("there is no variable you typed, run combination by form of 'from combination import *'")
    except e:
        print(e)
    return

def combination(target, data):
    outs = copy.copy(inner_combination(target, data))
    poper(Combina)
    return outs
    


''' CAUTION

    You input this funcion for form of 'from combination import *' or you have error

    You must have function from 'combination(target, data)'

    Don't FORGET type target first.

    It's just null list that saves the list. You Don't have to worry about that.

    I give the example for you

>>> from combination import *
>>> data = [1, '1', 'a']        <- data can be number or string or any type
>>> combination(target, data)
[[1], [1, '1'], [1, '1', 'a'], [1, 'a'], ['1'], ['1', 'a'], ['a']]    <- Cool!!!
    
'''
