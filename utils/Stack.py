from collections import deque

class Stack:
    def __init__(self):
        self._data = deque()
    
    def push(self, item):
        self._data.append(item)
    
    def pop(self):
        if self.is_empty():
            raise IndexError("Pop from empty stack")
        return self._data.pop()
    
    def peek(self):
        if self.is_empty():
            raise IndexError("Peek from empty stack")
        return self._data[-1]
    
    def is_empty(self)
        return len(self._data) == 0
    
    def __len__(self):
        return len(self._data) 
    
    def __repr__(self):
        return f"Stack({list(self._data)})"