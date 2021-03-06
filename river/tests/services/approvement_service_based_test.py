from django.contrib.contenttypes.models import ContentType
import factory

from river.tests.base_test import BaseTestCase
from river.tests.models import TestModel
from river.tests.models.factories import TestModelObjectFactory

__author__ = 'ahmetdal'


class ApprovementServiceBasedTest(BaseTestCase):
    def setUp(self):
        from river.models.factories import \
            TransitionObjectFactory, \
            UserObjectFactory, \
            PermissionObjectFactory, \
            ApprovementMetaObjectFactory, \
            StateObjectFactory

        TransitionObjectFactory.reset_sequence(0)
        ApprovementMetaObjectFactory.reset_sequence(0)
        StateObjectFactory.reset_sequence(0)
        TestModel.objects.all().delete()

        self.content_type = ContentType.objects.get_for_model(TestModel)
        self.permissions = PermissionObjectFactory.create_batch(4)
        self.user1 = UserObjectFactory(user_permissions=[self.permissions[0]])
        self.user2 = UserObjectFactory(user_permissions=[self.permissions[1]])
        self.user3 = UserObjectFactory(user_permissions=[self.permissions[2]])
        self.user4 = UserObjectFactory(user_permissions=[self.permissions[3]])

        self.field = 'my_field'
        self.states = StateObjectFactory.create_batch(
            9,
            label=factory.Sequence(lambda n: "s%s" % str(n + 1) if n <= 4 else ("s4.%s" % str(n - 4) if n <= 6 else "s5.%s" % str(n - 6)))
        )
        self.transitions = TransitionObjectFactory.create_batch(8,
                                                                content_type=self.content_type,
                                                                field=self.field,
                                                                source_state=factory.Sequence(
                                                                    lambda n: self.states[n] if n <= 2 else (self.states[n - 1]) if n <= 4 else (self.states[n - 2] if n <= 6 else self.states[4])),
                                                                destination_state=factory.Sequence(lambda n: self.states[n + 1]))

        self.approvement_metas = ApprovementMetaObjectFactory.create_batch(
            9,
            transition=factory.Sequence(lambda n: self.transitions[n] if n <= 1 else self.transitions[n - 1]),
            order=factory.Sequence(lambda n: 1 if n == 2 else 0)
        )

        for n, approvement_meta in enumerate(self.approvement_metas):
            approvement_meta.permissions.add(self.permissions[n] if n <= 3 else self.permissions[3])

        self.objects = TestModelObjectFactory.create_batch(2)
