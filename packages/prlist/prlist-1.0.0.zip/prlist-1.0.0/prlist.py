#define a function named my_print:

def my_print(my_list):
    for item in my_list:
        if isinstance(item,list):
            my_print(item)
        else:
            print(item)
        
