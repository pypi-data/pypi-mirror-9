import factory


class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Sequence(lambda n: 'Test_User_%s' % n)
    password = factory.PostGenerationMethodCall('set_password', 'adm1n')
    email = factory.Sequence(lambda n: 'Test_User_%s@example.com' % n)

    class Meta:
        model = 'auth.User'
