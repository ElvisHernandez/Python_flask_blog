

class Pagination:
    def __init__(self,**kwargs):
        self.pages = kwargs.get("pages",None)
        self.page = kwargs.get("page",None)
        if self.page == self.pages:
            self.has_next = False
        else:
            self.has_next = True

        if self.page == 1:
            self.has_prev = False
        else:
            self.has_prev = True

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
            eff_rc = [page for page in range(self.page,self.pages-right_edge+1)]
        else:
            eff_rc = [page for page in range(self.page,self.page+right_current+1)]
        
        # if eff_le end eff_re start points and end points are not consecutive then 
        # insert None value for pagination separation
        if len(eff_le) != 0 and len(eff_lc) != 0 and eff_le[-1] != eff_lc[0]-1:
                pages.append(None)

        pages += eff_lc + eff_rc

        # effective right edge
        if self.pages - self.page < right_edge:
            eff_re = [page for page in range(self.page,self.pages+1)]
        else:
            eff_re = [page for page in range(self.pages-right_edge+1,self.pages+1)]
        
        # same as above
        if len(eff_rc) != 0 and len(eff_re) != 0 and eff_rc[-1] != eff_re[0]-1:
            pages.append(None)
        
        pages += eff_re
        return pages
