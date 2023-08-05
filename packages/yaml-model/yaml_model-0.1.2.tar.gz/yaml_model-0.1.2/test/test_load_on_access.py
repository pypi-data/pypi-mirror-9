"""
Test the LoadOnAccess class
"""
import pytest
import yaml

from yaml_model import LoadOnAccess, Model


class TestBase(Model):
    """
    Base test model that just has a default slug
    """
    slug = 'test'


@pytest.mark.usefixtures("cleandir")
class TestLoadOnAccess(object):
    """
    Test the LoadOnAccess class
    """
    def test_lazy_load(self, cleandir):
        """
        Tests that params are lazy loaded
        """
        class Test(TestBase):  # pylint:disable=missing-docstring
            field1 = LoadOnAccess()
            field2 = LoadOnAccess()

        data_file = cleandir.join('data', 'tests', 'test.yaml')
        data_file.ensure()
        with data_file.open('w') as handle:
            handle.write("""
            field1: hey there
            field2: just testing
            """)

        test = Test()

        assert test._lazy_vals == {}
        assert test.field1 == 'hey there'
        assert test._lazy_vals == {'field1': 'hey there',
                                   'field2': 'just testing'}
        assert test.field2 == 'just testing'

    @pytest.mark.parametrize('create', [True, False])  # Model exists first
    @pytest.mark.parametrize('kwarg_name,yaml_data', [
        ('generate', {'field1': 'hey there'}),
        ('default', {})
    ])
    def test_default_generate_persist(self,
                                      cleandir,
                                      create,
                                      kwarg_name,
                                      yaml_data):
        """
        Tests to make sure that generate/default kwarg generates
        """
        kwargs = {kwarg_name: 'hey there'}

        class Test(TestBase):  # pylint:disable=missing-docstring
            field1 = LoadOnAccess(**kwargs)

        data_file = cleandir.join('data', 'tests', 'test.yaml')
        if create:
            data_file.ensure()

        test = Test()
        test.save()
        with data_file.open() as handle:
            assert yaml.load(handle) == yaml_data

    @pytest.mark.parametrize('kwarg_name', ['generate', 'default'])
    def test_generators_pass_model(self, kwarg_name):
        """
        Tests to make sure that the generate/default kwargs are passed the
        model object when they are callables (also make tests that callables
        work)
        """
        data = {}

        def test_self(self_):
            """
            A "generator" that asserts the id of models match
            """
            assert id(self_) == id(data['model'])

        kwargs = {kwarg_name: test_self}

        class Test(TestBase):  # pylint:disable=missing-docstring
            field1 = LoadOnAccess(**kwargs)

        data['model'] = Test()
        # Not pointless; this triggers a load. Test pass if no exception
        data['model'].field1  # pylint:disable=pointless-statement

    @pytest.mark.parametrize('kwarg_name', ['generate', 'default'])
    @pytest.mark.parametrize('value', ['test', 22, {}, [], True, False])
    def test_generators_static(self, kwarg_name, value):
        """
        Test to make sure that generate/default kwargs can static values
        """
        kwargs = {kwarg_name: value}

        class Test(TestBase):  # pylint:disable=missing-docstring
            field1 = LoadOnAccess(**kwargs)

        assert Test().field1 == value

    @pytest.mark.parametrize(
        'kwarg_name',
        ['input_transform', 'output_transform']
    )
    def test_transforms(self, kwarg_name):
        """
        Test that input/output transforms apply as expected
        """
        kwargs = {kwarg_name: lambda value: value + 1}

        class Test(TestBase):  # pylint:disable=missing-docstring
            field1 = LoadOnAccess(**kwargs)

        test = Test()
        test.field1 = 1
        assert test.field1 == 2
