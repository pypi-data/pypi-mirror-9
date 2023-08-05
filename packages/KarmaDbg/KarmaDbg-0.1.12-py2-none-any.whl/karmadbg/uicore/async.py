
def async(fn):

    def wrapper(*args, **kwargs):

        try:
            async = fn(*args, **kwargs)
            asyncOp = async.next()
            asyncOp.doTaskAsync(async)
        except StopIteration:
            pass

    return wrapper


class AsyncOperation(object):
    
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def doTaskAsync(self,async):
        pass

    def task(self, *args, **kwargs):
        pass
        



