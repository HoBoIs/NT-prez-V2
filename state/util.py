def always(*args):
    return True
_uid=0
_m={}
def getuid():
    global _uid
    _uid+=1
    return _uid

def connectWrapper(sgnl,fun,fil,u):
    def res(*param):
        print(*param)
        if fil(*param):
            fun(*param)
            print(u,"=u")
            sgnl.disconnect(_m[u])
            #_m[u].disconnect()
    return res


def connectOnce(sgnl, fun, fil=always):
    u=getuid()
    connection = sgnl.connect(connectWrapper(sgnl,fun,fil,u))
    _m[u]=connection


