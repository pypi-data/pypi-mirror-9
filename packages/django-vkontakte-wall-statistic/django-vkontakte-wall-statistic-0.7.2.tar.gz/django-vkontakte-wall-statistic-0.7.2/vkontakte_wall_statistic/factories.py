from models import PostStatistic
from vkontakte_wall.factories import PostFactory
import factory

class PostStatisticFactory(factory.DjangoModelFactory):
    FACTORY_FOR = PostStatistic

    post = factory.SubFactory(PostFactory)