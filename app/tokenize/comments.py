from ..helper.bi_direction_iterator import BiDirectionIterator


class Comments:
    @staticmethod
    def has_comments(iter: BiDirectionIterator) -> bool:
        sym = next(iter)
        sym += next(iter)
        if sym != "//":
            iter.step_back()
            iter.step_back()
            return False
        
        for ch in iter:
            if ch == "\n":
                break
        
        return True
            