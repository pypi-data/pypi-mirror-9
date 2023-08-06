from django.db import models
from django.test import TestCase


class SampleModel(models.Model):
    field = "Message"
    pass


class ModelRenderTests(TestCase):
    def test_render(self):
        assert(getattr(SampleModel, "render", False))
        inst = SampleModel()
        self.assertEqual(inst.render().strip(), "Message")
