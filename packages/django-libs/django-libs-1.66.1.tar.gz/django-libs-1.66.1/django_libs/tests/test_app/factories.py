"""Just some factories for the test app."""
import factory

from ..factories import HvadFactoryMixin, UserFactory
from models import DummyProfile, HvadDummy


class HvadDummyFactory(HvadFactoryMixin, factory.DjangoModelFactory):
    """Factory for the ``HvadDummy`` model."""
    FACTORY_FOR = HvadDummy

    title = factory.Sequence(lambda n: 'title{}'.format(n))


class DummyProfileFactory(factory.DjangoModelFactory):
    """Factory for the ``DummyProfile`` model."""
    FACTORY_FOR = DummyProfile

    user = factory.SubFactory(UserFactory)
    dummy_field = factory.Sequence(lambda n: 'dummyfield{}'.format(n))
