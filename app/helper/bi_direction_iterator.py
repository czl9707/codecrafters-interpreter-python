from typing import Iterator


class BiDirectionIterator:
    def __init__(self, s: str) -> None:
        self.s = s
        self.string_len = len(s)
        self.index = 0
    
    def __next__(self) -> str:
        if self.EOF:
            raise StopIteration
        
        self.index += 1
        return self.s[self.index - 1]
        
    def __iter__(self) -> Iterator[str]:
        while not self.EOF:
            yield next(self)
                
    def step_back(self) -> None:
        self.index -= 1
    
    @property
    def EOF(self) -> bool:
        return self.index >= self.string_len