from models import User
from datetime import datetime
import factory
import random

class UserFactory(factory.DjangoModelFactory):
    FACTORY_FOR = User

    id = factory.Sequence(lambda n: n)
    gender = random.choice([1,2])
    registered_date = datetime.now()