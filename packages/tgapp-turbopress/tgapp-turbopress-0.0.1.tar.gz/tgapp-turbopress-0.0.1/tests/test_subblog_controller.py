from test_auth_controller import TurboPressAuthControllerTests
from .base import configure_app


class TestSubBlogAuthenticatedSQLA(TurboPressAuthControllerTests):
    BLOG = 'testblog'

    @classmethod
    def setupClass(cls):
        cls.app_config = configure_app('sqlalchemy')


class TestSubBlogAuthenticatedMing(TurboPressAuthControllerTests):
    BLOG = 'testblog'

    @classmethod
    def setupClass(cls):
        cls.app_config = configure_app('ming')

