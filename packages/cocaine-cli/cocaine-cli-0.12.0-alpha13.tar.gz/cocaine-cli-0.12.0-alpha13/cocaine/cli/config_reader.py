


def reader(fields, D):

        D1 = {}

        for k,v in D.iteritems():
            if k in fields:
                if not fields[k]:
                    continue
                elif fields[k] == True:
                    D1[k] = v
                elif type(fields[k]) == dict:
                    if len(fields[k])==1 and "*" in fields[k]:
                        D2 = {}
                        D1[k] = D2
                        for k1,v1 in v.iteritems():
                            D2[k1] = reader(fields[k]["*"], v1)
                    else:
                        D1[k] = reader(fields[k], v)
            elif "*" in fields and fields["*"]:
                D1[k] = v
        return D1



class Reader(object):
    fields = {}
    
    @classmethod
    def read(cls, D):

        return reader(cls.fields, D)
    

class ProjectReader(Reader):

    fields = {
        "name" : True,
        "members": True,
        "clusters": {
            "*": {
                "*": True,
                "profile": False,
                "manifest": False
            }
        }
    }



class VersionReader(Reader):

    fields = {
        "name": True,
        "version": True,
        "clusters":{
            "*": {
                "manifest": True,
                "profile": True
            }
        },
        "source": True
    }
        

