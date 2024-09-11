class CharacterProvider:
    def __init__(self, s: str) -> None:
        self.s = s
        self.string_len = len(s)
        self.index = 0
        self.line = 1
    
    def __next__(self) -> str:
        if self.EOF:
            raise StopIteration
        
        self.index += 1
        if self.s[self.index - 1] == "\n":
            self.line += 1
        return self.s[self.index - 1]

                
    def step_back(self, step = 1) -> None:
        self.index -= step
        self.line -= self.s.count("\n", self.index, self.index + step)
    
    @property
    def EOF(self) -> bool:
        return self.index >= self.string_len