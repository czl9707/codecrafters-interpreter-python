from ..helper.bi_direction_iterator import BiDirectionIterator


class Comments:
    @staticmethod
    def consume_comments(iter: BiDirectionIterator) -> bool:
        sym = next(iter)
        if not iter.EOF: 
            sym += next(iter)
        
        if sym != "//":
            for _ in sym:
                iter.step_back()
            return False
        else:
            while not iter.EOF:
                if next(iter) == "\n":
                    iter.step_back()
                    break
                
            return True
        
class WhiteSpace:
    @staticmethod
    def consume_white_space(iter: BiDirectionIterator) -> bool:
        consumed = False
        while WhiteSpace.__consume_single(iter):
            consumed = True
            
        return consumed
        
    @staticmethod
    def __consume_single(iter: BiDirectionIterator) -> bool:
        if iter.EOF:
            return False
        
        s = next(iter)
        if s == " " or s == "\t":
            return True

        iter.step_back()
        return False