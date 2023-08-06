import copy
def combination(data, printing=0):
    target = []
    Combina = []
    pn = printing
    def _combination(target, Combina, data, pn):
        for i in range(len(data)):
            new_target = copy.copy(target)  # data is type list what you want
            new_data = copy.copy(data)
            new_target.append(data[i])
            new_data = data[i+1:]
            Combina.append(new_target)
            if pn != 0:
                print(Combina)
            _combination(new_target, Combina, new_data, pn)
            
        return Combina

    outs = copy.copy(_combination(target, Combina, data, pn))
    poper(Combina)
    return outs

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

''' Example

>>> import combination_all as cm
>>> data = ['a', 1, '0']
>>> cm.combination(data)
[['a'], ['a', 1], ['a', 1, '0'], ['a', '0'], [1], [1, '0'], ['0']]
>>> cm.combination(data,1)
[['a']]
[['a'], ['a', 1]]
[['a'], ['a', 1], ['a', 1, '0']]
[['a'], ['a', 1], ['a', 1, '0'], ['a', '0']]
[['a'], ['a', 1], ['a', 1, '0'], ['a', '0'], [1]]
[['a'], ['a', 1], ['a', 1, '0'], ['a', '0'], [1], [1, '0']]
[['a'], ['a', 1], ['a', 1, '0'], ['a', '0'], [1], [1, '0'], ['0']]    
'''
