import math
page_translated = 0
page_total = 0
listeners = []

def set_total_page(value):
    global page_total,page_translated 
    page_total = value
    page_translated = 0

def update_status():
    global page_translated
    page_translated += 1
    increment = math.ceil(page_translated / page_total * 100) - math.ceil((page_translated-1) / page_total * 100) 
    for listener in listeners:
        listener(increment)
    
def add_listener(listener):
    listeners.append(listener)

def clear_listeners() -> bool:
    global listeners
    task_before = False
    if (len(listeners)!=0):
        task_before = True
    listeners = []
    return task_before
