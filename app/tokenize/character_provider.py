class CharacterProvider:
    def __init__(self, s: str) -> None:
        self.s = s
        self.string_len = len(s)
        self.index = 0
        self.line = 1
    
    def forward(self, step: int = 1) -> str:
        if self.index + step > self.string_len:
            raise StopIteration
        
        self.line += self.s.count("\n", self.index, self.index + step)
        self.index += step
        return self.s[self.index - step: self.index]

                
    def backward(self, step:int = 1) -> None:
        self.index -= step
        self.line -= self.s.count("\n", self.index, self.index + step)
    
    def top(self, step: int = 1) -> str:
        return self.s[self.index: self.index + step]
    
    def forward_until(self, s:str) -> str:
        end = self.s.find(s, self.index, -1)
        if end == -1:
            return self.forward(self.string_len - self.index)
        else:
            return self.forward(end - self.index + 1)
    
    @property
    def EOF(self) -> bool:
        return self.index >= self.string_len