from ..helper.bi_direction_iterator import BiDirectionIterator


class Comments:
    @staticmethod
    def has_comments(iter: BiDirectionIterator) -> bool:
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
                    break
                
            return True
        
            