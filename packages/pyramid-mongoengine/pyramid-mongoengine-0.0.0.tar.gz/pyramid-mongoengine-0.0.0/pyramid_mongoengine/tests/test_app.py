from . import PyramidMongoEngineTestCase


class TestSimpleApp(PyramidMongoEngineTestCase):

    def setUp(self):

        super(TestSimpleApp, self).setUp()

        from .apptest import main
        app = main({"mongodb_name": "dbapp_test"})
        from webtest import TestApp
        self.app = TestApp(app)

        params = {"email": "default@email.com", "username": "testerd"}
        self.app.post('/users/', params=params)

    def tearDown(self):
        super(TestSimpleApp, self).tearDown()
        from .apptest import User
        User.drop_collection()

    def test_simple_get(self):
        res = self.app.get('/')

        self.assertEquals(200, res.status_code)
        self.assertEquals({"msg": "hello test app"}, res.json)

    def test_simple_save_user(self):
        params = {"email": "test@email.com", "username": "tester"}
        res = self.app.post('/users/', params=params)

        json_res = res.json["user"]

        self.assertEquals(200, res.status_code)
        self.assertEquals(params["username"], json_res["username"])

    def test_simple_get_users(self):
        res = self.app.get("/users/")

        self.assertEquals(1, len(res.json["users"]))
