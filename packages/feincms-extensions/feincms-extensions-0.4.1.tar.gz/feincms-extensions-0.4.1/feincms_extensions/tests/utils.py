from incuna_test_utils.testcases.integration import BaseIntegrationTestCase

from .factories import UserFactory


class RenderedContentTestCase(BaseIntegrationTestCase):
    user_factory = UserFactory
