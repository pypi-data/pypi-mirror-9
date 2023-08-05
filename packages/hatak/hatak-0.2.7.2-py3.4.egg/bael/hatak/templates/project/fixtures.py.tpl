from pytest import fixture

from haplugin.sql.fixtures import BaseFixtures


class Fixtures(BaseFixtures):

    def make_all(self):
        # example:
        # self.create_nameless(Model, name=value)
        pass


@fixture(scope="session")
def fixtures(db, app):
    print("Creating fixtures...")
    return Fixtures(db, app).create_all()
