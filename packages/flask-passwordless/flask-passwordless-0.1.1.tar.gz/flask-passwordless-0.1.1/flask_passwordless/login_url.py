import abc


class LoginURL(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, config):
        pass

    @abc.abstractmethod
    def generate(self, token, userid):
        return

    @abc.abstractmethod
    def parse(self, request):
        return


class PlainLoginURL(LoginURL):
    def generate(self, token, userid):
        from flask import url_for
        return "".join([
            url_for('authenticate', _external=True),
            "?token={0}&uid={1}".format(token, userid)
        ])

    def parse(self, request):
        token = request.values['token']
        uid = request.values['uid']
        return token, uid


LOGIN_URLS = {
    'plain': PlainLoginURL,
}
