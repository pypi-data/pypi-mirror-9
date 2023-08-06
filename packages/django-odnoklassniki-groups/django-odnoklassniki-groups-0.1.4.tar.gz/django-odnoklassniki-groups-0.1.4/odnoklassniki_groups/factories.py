from models import Group
import factory
import random

class GroupFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Group

    id = factory.Sequence(lambda n: n)
    members_count = random.randrange(0, 10000)