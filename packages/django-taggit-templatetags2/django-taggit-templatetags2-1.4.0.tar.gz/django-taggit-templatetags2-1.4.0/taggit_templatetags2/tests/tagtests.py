import django

from django.test import TestCase
from django.template import Context, Template
from django.template.loader import get_template

from testapp.models import (
    AlphaModel,
    BetaModel,
    CharPkModel,
    AnotherCharPkModel)
from taggit_templatetags2.templatetags.taggit_templatetags2_tags import \
    get_weight_fun


# From
# https://github.com/alex/django-taggit/blob/develop/tests/tests.py
# START
class BaseTaggingTest(object):

    def assert_tags_equal(self, qs, tags, sort=True, attr="name"):
        got = [getattr(obj, attr) for obj in qs]
        if sort:
            got.sort()
            tags.sort()
        self.assertEqual(got, tags)

    def _get_form_str(self, form_str):
        if django.VERSION >= (1, 3):
            form_str %= {
                "help_start": '<span class="helptext">',
                "help_stop": "</span>"
            }
        else:
            form_str %= {
                "help_start": "",
                "help_stop": ""
            }
        return form_str

    def assert_form_renders(self, form, html):
        self.assertHTMLEqual(str(form), self._get_form_str(html))
# END


class SetUpTestCase():
    a_model = AlphaModel
    b_model = BetaModel

    def setUp(self):
        a1 = self.a_model.objects.create(name="apple")
        a2 = self.a_model.objects.create(name="pear")
        b1 = self.b_model.objects.create(name="dog")
        b2 = self.b_model.objects.create(name="kitty")

        a1.tags.add("green")
        a1.tags.add("sweet")
        a1.tags.add("fresh")

        a2.tags.add("yellow")
        a2.tags.add("sour")

        b1.tags.add("sweet")
        b1.tags.add("yellow")

        b2.tags.add("sweet")
        b2.tags.add("green")


class TestWeightFun(TestCase):

    def test_one(self):
        t_min = 1
        t_max = 6
        f_min = 10
        f_max = 20
        weight_fun = get_weight_fun(t_min, t_max, f_min, f_max)
        self.assertEqual(weight_fun(20), 6)
        self.assertEqual(weight_fun(10), 1)
        self.assertEqual(weight_fun(15), 3.5)

    def test_two(self):
        t_min = 10
        t_max = 100
        f_min = 5
        f_max = 7
        weight_fun = get_weight_fun(t_min, t_max, f_min, f_max)
        self.assertEqual(weight_fun(5), 10)
        self.assertEqual(weight_fun(7), 100)
        self.assertEqual(weight_fun(6), 55)


class TemplateTagListTestCase(SetUpTestCase, BaseTaggingTest, TestCase):

    def get_template(self, argument):
        return """      {%% load taggit_templatetags2_tags %%}
                        {%% get_taglist %s %%}
                """ % argument

    def test_project(self):
        t = Template(self.get_template("as taglist"))
        c = Context({})
        t.render(c)
        self.assert_tags_equal(
            c.get("taglist"),
            ["sweet", "green", "yellow", "fresh", "sour"],
            False)

    def test_app(self):
        t = Template(self.get_template("as taglist for 'testapp'"))
        c = Context({})
        t.render(c)
        self.assert_tags_equal(
            c.get("taglist"),
            ["sweet", "green", "yellow", "fresh", "sour"],
            False)

    def test_model(self):
        t = Template(self.get_template("as taglist for 'testapp.BetaModel'"))
        c = Context({})
        t.render(c)
        self.assert_tags_equal(
            c.get("taglist"), ["sweet", "green", "yellow"],
            False)


class TemplateTagCloudTestCase(SetUpTestCase, BaseTaggingTest, TestCase):

    def get_template(self, argument):
        return """      {%% load taggit_templatetags2_tags %%}
                        {%% get_tagcloud %s %%}
                """ % argument

    def test_project(self):
        t = Template(self.get_template("as taglist"))
        c = Context({})
        t.render(c)
        self.assert_tags_equal(
            c.get("taglist"),
            ["fresh", "green", "sour", "sweet", "yellow"],
            False)
        self.assertEqual(c.get("taglist")[3].name, "sweet")
        self.assertEqual(c.get("taglist")[3].weight, 6.0)
        self.assertEqual(c.get("taglist")[1].name, "green")
        self.assertEqual(c.get("taglist")[1].weight, 3.5)
        self.assertEqual(c.get("taglist")[2].name, "sour")
        self.assertEqual(c.get("taglist")[2].weight, 1.0)

    def test_app(self):
        t = Template(self.get_template("as taglist for 'testapp'"))
        c = Context({})
        t.render(c)
        self.assert_tags_equal(
            c.get("taglist"),
            ["fresh", "green", "sour", "sweet", "yellow"],
            False)
        self.assertEqual(c.get("taglist")[3].name, "sweet")
        self.assertEqual(c.get("taglist")[3].weight, 6.0)
        self.assertEqual(c.get("taglist")[1].name, "green")
        self.assertEqual(c.get("taglist")[1].weight, 3.5)
        self.assertEqual(c.get("taglist")[2].name, "sour")
        self.assertEqual(c.get("taglist")[2].weight, 1.0)

    def test_model(self):
        t = Template(self.get_template("as taglist for 'testapp.BetaModel'"))
        c = Context({})
        t.render(c)
        self.assert_tags_equal(
            c.get("taglist"),
            ["green", "sweet", "yellow"],
            False)
        self.assertEqual(c.get("taglist")[0].name, "green")
        self.assertEqual(c.get("taglist")[0].weight, 1.0)
        self.assertEqual(c.get("taglist")[1].name, "sweet")
        self.assertEqual(c.get("taglist")[1].weight, 6.0)
        self.assertEqual(c.get("taglist")[2].name, "yellow")
        self.assertEqual(c.get("taglist")[2].weight, 1.0)


class TemplateInclusionTagTest(SetUpTestCase, TestCase, BaseTaggingTest):

    def test_taglist_project(self):
        t = get_template('taggit_templatetags2/taglist_include.html')
        c = Context({'forvar': None})
        t.render(c)
        self.assert_tags_equal(
            c.get("tags"),
            ["sweet", "green", "yellow", "fresh", "sour"],
            False)

    def test_taglist_app(self):
        t = get_template('taggit_templatetags2/taglist_include.html')
        c = Context({'forvar': 'testapp'})
        t.render(c)
        self.assert_tags_equal(
            c.get("tags"),
            ["sweet", "green", "yellow", "fresh", "sour"],
            False)

    def test_taglist_model(self):
        t = get_template('taggit_templatetags2/taglist_include.html')
        c = Context({'forvar': 'testapp.BetaModel'})
        t.render(c)
        self.assert_tags_equal(
            c.get("tags"),
            ["sweet", "green", "yellow"],
            False)

    def test_tagcloud_project(self):
        t = get_template('taggit_templatetags2/tagcloud_include.html')
        c = Context({'forvar': None})
        t.render(c)
        self.assert_tags_equal(
            c.get("tags"),
            ["fresh", "green", "sour", "sweet", "yellow"],
            False)

    def test_tagcloud_app(self):
        t = get_template('taggit_templatetags2/tagcloud_include.html')
        c = Context({'forvar': 'testapp'})
        t.render(c)
        self.assert_tags_equal(
            c.get("tags"),
            ["fresh", "green", "sour", "sweet", "yellow"],
            False)

    def test_tagcloud_model(self):
        t = get_template('taggit_templatetags2/tagcloud_include.html')
        c = Context({'forvar': 'testapp.BetaModel'})
        t.render(c)
        self.assert_tags_equal(
            c.get("tags"), ["green", "sweet", "yellow"], False)


class AlphaPathologicalCaseTestCase(TestCase, BaseTaggingTest):

    """
    This is a testcase for one tag once.
    """
    a_model = AlphaModel

    def setUp(self):
        a1 = self.a_model.objects.create(name="apple")
        a1.tags.add("green")

    def test_tagcloud(self):
        t = get_template('taggit_templatetags2/tagcloud_include.html')
        c = Context({'forvar': None})
        t.render(c)
        self.assert_tags_equal(c.get("tags"), ["green"], False)
        self.assertEqual(c.get("tags")[0].name, "green")
        self.assertEqual(c.get("tags")[0].weight, 6.0)


class BetaPathologicalCaseTestCase(TestCase, BaseTaggingTest):

    """
    This is a testcase for one tag thrice.
    """
    a_model = AlphaModel
    b_model = BetaModel

    def setUp(self):
        a1 = self.a_model.objects.create(name="apple")
        a2 = self.a_model.objects.create(name="pear")
        b1 = self.b_model.objects.create(name="dog")
        a1.tags.add("green")
        a2.tags.add("green")
        b1.tags.add("green")

    def test_tagcloud(self):
        t = get_template('taggit_templatetags2/tagcloud_include.html')
        c = Context({'forvar': None})
        t.render(c)
        self.assert_tags_equal(c.get("tags"), ["green"], False)
        self.assertEqual(c.get("tags")[0].name, "green")
        self.assertEqual(c.get("tags")[0].weight, 6.0)


class GammaPathologicalCaseTestCase(TestCase, BaseTaggingTest):

    """
    This is a pathological testcase for no tag at all.
    """
    a_model = AlphaModel
    b_model = BetaModel

    def setUp(self):
        self.a_model.objects.create(name="apple")
        self.b_model.objects.create(name="dog")

    def test_tagcloud(self):
        t = get_template('taggit_templatetags2/tagcloud_include.html')
        c = Context({'forvar': None})
        t.render(c)
        self.assert_tags_equal(c.get("tags"), [], False)


class CustomThroughModelTestCase(TestCase, BaseTaggingTest):

    """
    Test tags with a custom 'through' parameter.
    """

    def setUp(self):
        a1 = CharPkModel.objects.create()
        a1.tags.add("green")
        a1.tags.add("blue")
        a2 = AnotherCharPkModel.objects.create()
        a2.ttaaggss.add("yellow")
        a2.ttaaggss.add("orange")

    def test_default_tags_name(self):
        t = get_template('taggit_templatetags2/tagcloud_include.html')
        c = Context({'forvar': 'testapp.CharPkModel'})
        t.render(c)
        self.assert_tags_equal(c.get("tags"), ["blue", "green"], False)

    def test_custom_tags_name(self):
        t = get_template('taggit_templatetags2/tagcloud_include.html')
        c = Context({'forvar': 'testapp.AnotherCharPkModel:ttaaggss'})
        t.render(c)
        self.assert_tags_equal(c.get("tags"), ["orange", "yellow"], False)
