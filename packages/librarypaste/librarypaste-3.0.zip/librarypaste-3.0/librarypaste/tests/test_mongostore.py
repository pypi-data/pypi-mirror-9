import pytest

from . import DataStoreTest
from librarypaste import mongostore


@pytest.fixture(scope='class', autouse=True)
def database(request, mongodb_uri):
	mongodb_uri += '/librarypaste-test'
	request.cls.datastore = mongostore.MongoDBDataStore.from_uri(mongodb_uri)

class TestMongoDBDataStore(DataStoreTest):
	pass
