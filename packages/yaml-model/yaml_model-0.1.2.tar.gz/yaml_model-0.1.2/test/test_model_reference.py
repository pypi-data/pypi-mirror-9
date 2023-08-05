"""
Test the ModelReference class to make sure it persists, and loads data as
expected
"""
import pytest
import yaml

from yaml_model import Model, ModelReference


class RefTo(Model):
    """
    Model referenced by the RefIn model
    """
    slug = None

    def __init__(self, slug):
        super(RefTo, self).__init__()
        self.slug = slug


class RefIn(Model):
    """
    Model that references the RefTo model
    """
    slug = 'refin'
    ref = ModelReference(lambda self: RefTo(self.ref_slug))


@pytest.fixture(params=['test', 'otherslug'])
def model_with_ref(request):
    """
    A slug/model pair
    """
    ref_to = RefTo(request.param)
    ref_in = RefIn()

    ref_in.ref = ref_to

    return request.param, ref_in


class TestModelReference(object):
    """
    Test the ModelReference class
    """
    def test_model_reference(self, cleandir, model_with_ref):
        """
        Test to make sure that refs are persisted correctly, and that lazy load
        is triggered by either the model ref field, or the model slug field
        """
        slug, model = model_with_ref
        assert model.ref_slug == slug

        model.ref.save()
        model.save()

        with cleandir.join('data', 'refins', 'refin.yaml').open() as handle:
            assert yaml.load(handle) == {'ref_slug': slug}

        assert RefIn().ref_slug == slug  # pylint:disable=no-member
        assert RefIn().ref.slug == slug
