
CherryClass Root:
variable:
    a = 1
function:
    def f1(self):
        return self.f2()
mask:
    def mask1(self):
        mask1
view:
    def view1(self):
        return self.mask2()
mask:
    def mask2(self):
        mask2
view:
    def view2(self):
        return self.f1()
function:
    def f2(self):
        return str(self.b)
variable:
    b = a + 1


CherryClass Shutdown:
view:
    def dummy(self):
        return "OK"
    def regular(self):
        os._exit(0)
    def thread(self):
        for t in threading.enumerate(): t.setName("NOT RUNNING")
        return "OK"        
