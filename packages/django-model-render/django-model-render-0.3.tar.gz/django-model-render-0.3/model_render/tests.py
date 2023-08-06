from django.db import models
from django.test import TestCase
from model_render import ModelRenderMixin


class SampleUnrenderedModel(models.Model):
    field = "Message"


class SampleRenderedModel(ModelRenderMixin, SampleUnrenderedModel):
    field = "Message"


class SampleRenderedModelWithTemplateName(SampleRenderedModel):
    template_path = "model_render/models/samplerenderredmodeltemplatename.html"


class ModelRenderTests(TestCase):
    def test_render(self):
        self.assertFalse(getattr(SampleUnrenderedModel, "render", False))
        self.assertTrue(getattr(SampleRenderedModel, "render", False))

        inst = SampleRenderedModel()
        self.assertEqual(inst.render().strip(), "Message")
        self.assertEqual(inst.render("model_render/models/samplerenderredmodel2.html").strip(), "MessageMessage")

        tninst = SampleRenderedModelWithTemplateName()
        self.assertEqual(tninst.render().strip(), "MessageMessageMessage")
        self.assertEqual(inst.render("model_render/models/samplerenderredmodel2.html").strip(), "MessageMessage")
