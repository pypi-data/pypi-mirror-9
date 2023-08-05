"""
Test the LoadOnAccess class
"""
import py.path
import pytest
import yaml

from yaml_model import LoadOnAccess, Model


class TestBase(Model):
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
        class Test(TestBase):
            f1 = LoadOnAccess()
            f2 = LoadOnAccess()

        data_file = cleandir.join('data', 'tests', 'test.yaml')
        data_file.ensure()
        with data_file.open('w') as handle:
            handle.write("""
            f1: hey there
            f2: just testing
            """)

        test = Test()

        assert test._lazy_vals == {}
        assert test.f1 == 'hey there'
        assert test._lazy_vals == {'f1': 'hey there', 'f2': 'just testing'}
        assert test.f2 == 'just testing'

    @pytest.mark.parametrize('create', [True, False])  # Model exists first
    @pytest.mark.parametrize('kwarg_name,yaml_data', [
        ('generate', {'f1': 'hey there'}),
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
        class Test(TestBase):
            f1 = LoadOnAccess(**kwargs)

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
            assert id(self_) == id(data['model'])

        kwargs = {kwarg_name: test_self}
        class Test(TestBase):
            f1 = LoadOnAccess(**kwargs)

        data['model'] = Test()
        data['model'].f1

    @pytest.mark.parametrize('kwarg_name', ['generate', 'default'])
    @pytest.mark.parametrize('value', ['test', 22, {}, [], True, False])
    def test_generators_static(self, kwarg_name, value):
        """
        Test to make sure that generate/default kwargs can static values
        """
        kwargs = {kwarg_name: value}
        class Test(TestBase):
            f1 = LoadOnAccess(**kwargs)

        assert Test().f1 == value

    @pytest.mark.parametrize('kwarg_name',
        ['input_transform', 'output_transform']
    )
    def test_transforms(self, cleandir, kwarg_name):
        """
        Test that input/output transforms apply as expected
        """
        kwargs = {kwarg_name: lambda value: value + 1}
        class Test(TestBase):
            f1 = LoadOnAccess(**kwargs)

        test = Test()
        test.f1 = 1
        assert test.f1 == 2
