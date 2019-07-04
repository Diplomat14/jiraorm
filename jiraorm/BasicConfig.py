class SecurityConfig(object):
    
    __user = ''
    __APIToken = ''

    def __init__( self, user : str, APIToken : str ):
        if len(user) != 0 and len(APIToken) != 0:
            self.__user = user
            self.__APIToken = APIToken

    @property
    def user(self):
        return self.__user

    @property
    def APIToken(self):
        return self.__APIToken


class ConnectionConfig(object):

    __serv = ''

    def __init__ ( self, serve : str ):
        if len(serve) != 0:
            self.__serv = serve

    @property
    def server(self):
        return self.__serv