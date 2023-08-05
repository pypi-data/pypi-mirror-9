# -*- coding: utf-8 -*-
from __future__ import absolute_import
import unittest
from odin.exceptions import MappingSetupError, MappingExecutionError
from odin.mapping import MappingResult
from odin.mapping.helpers import MapDictAs, MapListOf, NoOpMapper
from .resources import *


class SimpleFromResource(odin.Resource):
    title = odin.StringField()


class SimpleToResource(odin.Resource):
    title = odin.StringField()
    title_count = odin.StringField()


class FakeToResource(odin.Resource):
    title = odin.StringField()
    name = odin.StringField()


class SimpleFromTo(odin.Mapping):
    from_obj = SimpleFromResource
    to_obj = SimpleToResource

    @odin.map_field(from_field='title')
    def title_count(self, value):
        if self.in_loop:
            return "%s: %s" % (self.loop_idx, value)
        else:
            return value


class MappingTestCase(unittest.TestCase):
    def assertMappingEquivalent(self, a, b):
        flat_a = sorted(str(i) for i in a)
        flat_b = sorted(str(i) for i in b)
        self.assertListEqual(flat_a, flat_b)


class MappingBaseTestCase(MappingTestCase):
    maxDiff = None

    def test_full_mapping(self):
        self.assertMappingEquivalent([
            (('from_field1',), None, ('to_field1',), False, False, False),
            (('from_field2',), int, ('to_field2',), False, False, False),
            (('from_field3', 'from_field4'), sum_fields, ('to_field3',), False, False, False),
            (('from_field1',), None, ('same_but_different',), False, False, False),
            (('from_field_c1', 'from_field_c2', 'from_field_c3'), 'multi_to_one', ('to_field_c1',), False, False, False),
            (('from_field_c4',), 'one_to_multi', ('to_field_c2', 'to_field_c3'), False, False, False),
            (('not_auto_c5',), 'not_auto_c5', ('not_auto_c5',), False, False, False),
            (('comma_separated_string',), 'comma_separated_string', ('array_string',), True, False, False),
            (None, 'assigned_field', ('assigned_field',), False, False, False),
            (('count',), None, ('count',), False, False, False),
            (('child',), MapDictAs(NoOpMapper), ('child',), False, True, False),
            (('children',), MapListOf(NoOpMapper), ('children',), False, True, False),
            (('title',), None, ('title',), False, False, False),
        ], FromToMapping._mapping_rules)

    def test_map(self):
        from_resource = FromResource(
            # Auto matched
            title="Foo",
            count="42",
            # Excluded
            excluded1=123.4,
            # Mappings
            from_field1="abc",
            from_field2="62",
            from_field3=44,
            from_field4=25,
            same_but_different="def",
            # Custom mappings
            from_field_c1="foo",
            from_field_c2="bar",
            from_field_c3="eek",
            from_field_c4="first-second-third",
            not_auto_c5="do something",
            comma_separated_string="foo,bar,eek",
            child=ChildResource(name='foo'),
            children=[ChildResource(name='foo'), ChildResource(name='bar')]
        )

        to_resource = from_resource.convert_to(ToResource)

        self.assertEqual('Foo', to_resource.title)
        self.assertEqual('42', to_resource.count)
        self.assertEqual(None, to_resource.excluded1)
        self.assertEqual('abc', to_resource.to_field1)
        self.assertEqual(62, to_resource.to_field2)
        self.assertEqual(69, to_resource.to_field3)
        self.assertEqual('abc', to_resource.same_but_different)
        self.assertEqual('foo-bar-eek', to_resource.to_field_c1)
        self.assertEqual('first', to_resource.to_field_c2)
        self.assertEqual('second-third', to_resource.to_field_c3)
        self.assertEqual("DO SOMETHING", to_resource.not_auto_c5)
        self.assertEqual(['foo', 'bar', 'eek'], to_resource.array_string)

    def test_missing_from_resource(self):
        with self.assertRaises(MappingSetupError):
            class _(odin.Mapping):
                to_obj = FakeToResource

    def test_missing_to_resource(self):
        with self.assertRaises(MappingSetupError):
            class _(odin.Mapping):
                from_obj = SimpleFromResource

    def test_unknown_from_field_mappings(self):
        with self.assertRaises(MappingSetupError):
            class _(odin.Mapping):
                from_obj = SimpleFromResource
                to_obj = FakeToResource

                mappings = (
                    ('unknown_field', None, 'title'),
                )

    def test_unknown_from_field_mappings_multiple(self):
        with self.assertRaises(MappingSetupError):
            class _(odin.Mapping):
                from_obj = SimpleFromResource
                to_obj = FakeToResource

                mappings = (
                    (('title', 'unknown_field'), None, 'title'),
                )

    def test_unknown_from_field_custom(self):
        with self.assertRaises(MappingSetupError):
            class _(odin.Mapping):
                from_obj = SimpleFromResource
                to_obj = FakeToResource

                @odin.map_field(from_field='unknown_field', to_field='title')
                def multi_to_one(self, *fields):
                    pass

    def test_bad_action_not_callable(self):
        with self.assertRaises(MappingSetupError):
            class _(odin.Mapping):
                from_obj = SimpleFromResource
                to_obj = FakeToResource

                mappings = (
                    ('title', 123, 'title'),
                )

    def test_bad_action_not_defined(self):
        with self.assertRaises(MappingSetupError):
            class _(odin.Mapping):
                from_obj = SimpleFromResource
                to_obj = FakeToResource

                mappings = (
                    ('title', 'do_transform', 'title'),
                )

    def test_bad_action_defined_not_callable(self):
        with self.assertRaises(MappingSetupError):
            class _(odin.Mapping):
                from_obj = SimpleFromResource
                to_obj = FakeToResource

                do_transform = 123

                mappings = (
                    ('title', 'do_transform', 'title'),
                )

    def test_unknown_to_field_mappings(self):
        with self.assertRaises(MappingSetupError):
            class _(odin.Mapping):
                from_obj = SimpleFromResource
                to_obj = FakeToResource

                mappings = (
                    ('title', None, 'unknown_field'),
                )

    def test_unknown_to_field_mappings_multiple(self):
        with self.assertRaises(MappingSetupError):
            class _(odin.Mapping):
                from_obj = SimpleFromResource
                to_obj = FakeToResource

                mappings = (
                    ('title', None, ('title', 'unknown_field')),
                )

    def test_unknown_to_field_custom(self):
        with self.assertRaises(MappingSetupError):
            class _(odin.Mapping):
                from_obj = SimpleFromResource
                to_obj = FakeToResource

                @odin.map_field(from_field='title', to_field='unknown_field')
                def multi_to_one(self, *fields):
                    pass

    def test_bad_mapping(self):
        with self.assertRaises(MappingSetupError):
            class _(odin.Mapping):
                from_obj = SimpleFromResource
                to_obj = FakeToResource

                mappings = (
                    'i_forgot', None, 'tuples'
                )

    def test_invalid_list_to_multiple_mapping(self):
        with self.assertRaises(MappingSetupError) as cm:
            class _(odin.Mapping):
                from_obj = SimpleFromResource
                to_obj = FakeToResource

                mappings = (
                    ('title', None, ('title', 'name'), True, False, False),
                )
        self.assertIn("specifies a to_list mapping, these can only be applied to a", str(cm.exception))

    def test_assignment_with_no_action(self):
        with self.assertRaises(MappingSetupError) as cm:
            class _(odin.Mapping):
                from_obj = SimpleFromResource
                to_obj = FakeToResource

                mappings = (
                    (None, None, ('title', 'name'), False, False, False),
                )
        self.assertIn("No action supplied for ", str(cm.exception))

    def test_from_field_no_field_resolver(self):
        with self.assertRaises(MappingSetupError) as cm:
            class _(odin.Mapping):
                from_obj = object
                to_obj = FakeToResource
        self.assertIn(r"`from_obj`", str(cm.exception))
        self.assertIn(r"does not have an attribute resolver defined.", str(cm.exception))

    def test_to_field_no_field_resolver(self):
        with self.assertRaises(MappingSetupError) as cm:
            class _(odin.Mapping):
                from_obj = FakeToResource
                to_obj = object

        self.assertIn(r"`to_obj`", str(cm.exception))
        self.assertIn(r"does not have an attribute resolver defined.", str(cm.exception))


class ExecuteMappingTestCase(MappingTestCase):
    def test_not_valid_from_resource(self):
        self.assertRaises(TypeError, FromToMapping, SimpleFromResource())

    def test_invalid_from_value_count(self):
        with self.assertRaises(MappingExecutionError):
            target = FromToMapping(FromResource())
            target._apply_rule((('from_field_c1', 'from_field_c2'), 'one_to_multi', ('title'), False, False, False))

    def test_invalid_to_value_count(self):
        with self.assertRaises(MappingExecutionError):
            target = FromToMapping(FromResource(title='Test'))
            target._apply_rule((('title',), 'multi_to_one', ('from_field_c1', 'from_field_c2'), False, False, False))

    def test_apply_single_resource(self):
        f = SimpleFromResource(title="ABC")
        t = SimpleFromTo.apply(f)

        self.assertIsInstance(t, SimpleToResource)
        self.assertEqual("ABC", t.title)

    def test_apply_single_resource_with_context(self):
        f = SimpleFromResource(title="ABC")
        t = SimpleFromTo.apply(f)

        self.assertIsInstance(t, SimpleToResource)
        self.assertEqual("ABC", t.title_count)

    def test_apply_multiple_resources(self):
        from_resources = [
            SimpleFromResource(title="Foo"),
            SimpleFromResource(title="Bar"),
            SimpleFromResource(title="Eek"),
        ]

        to_resource_iter = SimpleFromTo.apply(from_resources)
        self.assertIsInstance(to_resource_iter, MappingResult)
        self.assertListEqual(['Foo', 'Bar', 'Eek'], [t.title for t in to_resource_iter])

    def test_apply_multiple_resources_with_context(self):
        from_resources = [
            SimpleFromResource(title="Foo"),
            SimpleFromResource(title="Bar"),
            SimpleFromResource(title="Eek"),
        ]

        to_resource_iter = SimpleFromTo.apply(from_resources)
        self.assertIsInstance(to_resource_iter, MappingResult)
        self.assertListEqual(['0: Foo', '1: Bar', '2: Eek'], [t.title_count for t in to_resource_iter])


class ResourceA(odin.Resource):
    class Meta:
        abstract = True

    foo = odin.StringField()


class ResourceB(ResourceA):
    bar = odin.StringField()


class ResourceC(ResourceA):
    eek = odin.StringField()


class ResourceX(odin.Resource):
    class Meta:
        abstract = True

    foo = odin.StringField()


class ResourceY(ResourceX):
    bar = odin.StringField()


class ResourceZ(ResourceX):
    alt = odin.StringField()


class ResourceAToResourceX(odin.Mapping):
    from_obj = ResourceA
    to_obj = ResourceX

    @odin.map_field
    def foo(self, value):
        return "foo: %s" % value


class ResourceBToResourceY(ResourceAToResourceX):
    from_obj = ResourceB
    to_obj = ResourceY


class ResourceCToResourceZ(ResourceAToResourceX):
    from_obj = ResourceC
    to_obj = ResourceZ

    @odin.map_field(from_field='eek')
    def alt(self, value):
        return value


class SubClassMappingTestCase(MappingTestCase):
    """
    Test the concept of a sub class mapping ie

                Resource A          -->         Mapping A-X         -->           Resource X
                    |                                |                                |
               _____|_____                      _____|_____                      _____|_____
              /           \                    /           \                    /           \
             /             \                  /             \                  /             \
        Resource B     Resource C        Mapping B-Y    Mapping C-Z       Resource Y     Resource Z

    Define a mapping that can handle a list of *Resource A* and *Resource B* objects being mapped by an abstract mapping
    *Mapping A-X* to the corresponding *Resource Y* and *Resource Z* objects.

    """
    def test_abstract_resource_definitions(self):
        self.assertListEqual(['bar', 'foo'], [f.name for f in ResourceB._meta.fields])
        self.assertListEqual(['eek', 'foo'], [f.name for f in ResourceC._meta.fields])
        self.assertListEqual(['bar', 'foo'], [f.name for f in ResourceY._meta.fields])
        self.assertListEqual(['alt', 'foo'], [f.name for f in ResourceZ._meta.fields])

    def test_abstract_mapping_definitions(self):
        self.assertMappingEquivalent([
            (('foo',), 'foo', ('foo',), False, False, False),
            (('bar',), None, ('bar',), False, False, False),
        ], ResourceBToResourceY._mapping_rules)

        self.assertMappingEquivalent([
            (('eek',), 'alt', ('alt',), False, False, False),
            (('foo',), 'foo', ('foo',), False, False, False),
        ], ResourceCToResourceZ._mapping_rules)

    def test_abstract_mapping(self):
        source = [ResourceB(foo="1", bar="2"), ResourceC(foo="3", eek="4"), ResourceB(foo="5", bar="6")]
        result = list(ResourceAToResourceX.apply(source))

        self.assertIsInstance(result[0], ResourceY)
        self.assertIsInstance(result[1], ResourceZ)
        self.assertIsInstance(result[2], ResourceY)

    def test_subs(self):
        self.assertEqual({
            ResourceB: ResourceBToResourceY,
            ResourceC: ResourceCToResourceZ,
        }, ResourceAToResourceX._subs)

    def test_invalid_abstract_mapping_from_obj(self):
        # All sub_class.from_obj should be an sub_class of base_class.from_obj
        with self.assertRaises(MappingSetupError) as cm:
            class _(ResourceAToResourceX):
                from_obj = ResourceY
                to_obj = ResourceZ

        self.assertEqual('`from_obj` must be a subclass of `parent.from_obj`', str(cm.exception))

    def test_invalid_abstract_mapping_to_obj(self):
        # All sub_class.from_obj should be an sub_class of base_class.to_obj
        with self.assertRaises(MappingSetupError) as cm:
            class _(ResourceAToResourceX):
                from_obj = ResourceC
                to_obj = ResourceB

        self.assertIn('`to_obj` must be a subclass of `parent.to_obj`', str(cm.exception))

    def test_invalid_inherited_type(self):
        with self.assertRaises(TypeError) as cm:
            class ResourceD(ResourceA):
                pass
            ResourceAToResourceX.apply(ResourceD())

        self.assertIn("`source_resource` parameter must be an instance of", str(cm.exception))
