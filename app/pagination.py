

class Pagination:
    def __init__(self,**kwargs):
        self.pages = kwargs.get("pages",None)
        self.page = kwargs.get("page",None)
        self.has_next = kwargs.get("has_next",False)
        self.has_prev = kwargs.get("has_prev",False)
    
    def iter_pages(self,left_edge=2,left_current=2,right_current=5,right_edge=2):
        pages = []
        
        # effective left edge
        if self.page - left_edge < 0:
            eff_le = [page for page in range(1,self.page)]
        elif self.page == left_edge:
            eff_le = [page for page in range(1,left_edge)]
        else:
            eff_le = [page for page in range(1,left_edge+1)]

        pages += eff_le
        pages.append(None)
        
        # effective left current
        if self.page - left_current <= 0:
            eff_lc = []
        elif self.page - left_current < left_edge:
            eff_lc = []
        elif self.page - left_current == left_edge:
            eff_lc = [page for page in range(left_edge+1,self.page)]
        else:
            eff_lc = [page for page in range(self.page-left_current,self.page)]

        # effective right current
        if self.page + right_current > self.pages - right_edge:
            eff_rc = [self.page]
        else:
            eff_rc = [page for page in range(self.page,self.page+right_current+1)]

        pages += eff_lc + eff_rc
        pages.append(None)

        # effective right edge
        if self.pages - self.page < right_edge:
            eff_re = [page for page in range(self.page+1,self.pages+1)]
        else:
            eff_re = [page for page in range(self.pages-right_edge+1,self.pages+1)]
        
        pages += eff_re
        
        return pages
