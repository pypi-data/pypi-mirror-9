"""
Test Plan.

PluginIndex:
    test_unique:
        make sure plugin index is hashable and its uniqueness.

BaseResource, BaseProduct, BaseMessage, _BaseAsset:
    test_init:
        these class can not be initialized.
    test_access_manager_from_instance:
        manager can not be accessed from instance.

Manager:
    test_trace_one_class:
        initialize single derived class of [BaseResource, BaseProduct,
        BaseMessage,], make sure the manager can trace that instance.
    test_trace_multi_classes:
        initialize multiple derived classes of the same base class, make sure
        the manager of base class can trace multiple instances.
    test_usage:
        make sure bussinesses of manager, such as create, add, remove and so
        on, is correct.

ManagerProxyWithOwner:
    test_proxy:
        make sure the method with 'owenr' in signature is binded properly.

BasePlugin, PluginRegister, PluginController:
    test_register:
        ensure plugin is register by metaclass, and so as the process of
        retrieving plugins.
    test_theme_name:
        1. definde class-level theme attr.
        2. undefine class-level theme attr, but PluginRegister defines context
        theme.
    test_plugin_name:
        1. define class-level plugin attr.
        2. undefine ...
    test_default_params:
        1. test run method with 0~3 defined parameters(exclude self).
        2. test run method with parameters more than 3.
    test_accept_parameters:
        make sure accept_parameters works.
    test_accept_owners:
        make sure accept_owners works, and that do not confilct with
        theme_name.

"""

import unittest
from collections import defaultdict
from geekcms import protocol


class PluginIndexTest(unittest.TestCase):

    def test_unique(self):
        item_1 = protocol.PluginIndex('a', 'b')
        item_2 = protocol.PluginIndex('a', 'c')
        self.assertEqual(item_1, 'a.b')
        self.assertNotEqual(item_1, item_2)


class AssetTest(unittest.TestCase):

    def setUp(self):
        class TestClass(protocol.BaseResource):

            def __init__(self, owner):
                self.set_owner(owner)

        self.TestClass = TestClass

    def test_init(self):
        owner = 'testowner'
        attr = 'testattr'

        item = self.TestClass(owner)
        self.assertEqual(item.owner, owner)

        self.assertIsInstance(item, self.TestClass)
        self.assertNotIsInstance(item, protocol.BaseProduct)

    def test_access_manager_from_instance(self):
        with self.assertRaises(Exception):
            item = self.TestClass('testowner')
            # access
            item.objects
        with self.assertRaises(Exception):
            item = self.TestClass('testowner')
            # assign
            item.objects = None
        with self.assertRaises(Exception):
            # remove
            item = self.TestClass('testowner')
            del item.objects


class ManagerRegisterTest(unittest.TestCase):

    def setUp(self):
        protocol.BaseResource.objects.clear()

        # create test class
        class TestAsset(protocol.BaseResource):

            def __init__(self):
                pass

        self.TestAsset = TestAsset

        self.owner = 'testowner'

    def test_trace_one_class(self):
        # get binded owner
        manager = self.TestAsset.get_manager_with_fixed_owner(self.owner)
        item = manager.create()
        self.assertEqual(item.owner, self.owner)
        self.assertIsInstance(item, self.TestAsset)

    def test_trace_multi_classes(self):
        # TestAsset and AnotherTestAsset both derived from BaseResource.
        class AnotherTestAsset(protocol.BaseResource):

            def __init__(self):
                pass

        first_item = self.TestAsset.objects.create(owner=self.owner)
        second_item = AnotherTestAsset.objects.create(owner=self.owner)

        # get all assets.
        self.assertSetEqual(
            set((first_item, second_item)),
            set(protocol.BaseResource.objects.values()),
        )

        # exclusive share field.
        self.assertFalse(protocol.BaseProduct.objects.values())
        self.assertFalse(protocol.BaseMessage.objects.values())


class ManagerUsageTest(unittest.TestCase):

    def setUp(self):
        class TestClass(protocol.BaseResource):

            def __init__(self):
                pass

        self.TestClass = TestClass
        self.owner = 'testowner'
        self.manager = protocol.Manager(TestClass)

    def test_create(self):
        item = self.manager.create(owner=self.owner)
        self.assertEqual(item.owner, self.owner)
        self.assertIsInstance(item, self.TestClass)

    def test_add_remove(self):
        item = self.TestClass()
        item.set_owner(self.owner)
        self.assertEqual(self.manager, defaultdict(list))

        self.manager.add(item)
        self.assertDictEqual(
            dict(self.manager),
            {self.owner: [item]},
        )

        self.manager.remove(item)
        self.assertEqual(self.manager, defaultdict(list))

    def test_filter_keys_values(self):
        owner_1 = 'owner_1'
        owner_2 = 'owner_2'
        item_1 = self.manager.create(owner=owner_1)
        item_2 = self.manager.create(owner=owner_2)

        self.assertListEqual(self.manager.filter(owner_1), [item_1])
        self.assertListEqual(self.manager.filter(owner_2), [item_2])
        self.assertSetEqual(
            set(self.manager.keys()),
            {owner_1, owner_2},
        )
        self.assertSetEqual(
            set(self.manager.values()),
            {item_1, item_2},
        )


class ManagerProxyWithOwnerTest(unittest.TestCase):

    def setUp(self):
        class TestClass(protocol.BaseResource):

            def __init__(self):
                pass

        self.TestClass = TestClass
        self.owner = 'testowner'
        self.manager = protocol.Manager(TestClass)

    def test_proxy(self):
        proxy = protocol.ManagerProxyWithOwner(self.owner, self.manager)

        item = proxy.create()
        self.assertDictEqual(
            dict(self.manager),
            {self.owner: [item]},
        )

        proxy.remove(item)
        self.assertEqual(self.manager, defaultdict(list))

        item = proxy.create()
        self.assertListEqual(proxy.filter(), [item])
        self.assertListEqual(proxy.keys(), [self.owner])
        self.assertListEqual(proxy.values(), [item])


class PluginTest(unittest.TestCase):

    def setUp(self):
        # clean up
        protocol.BaseResource.objects.clear()
        protocol.BaseProduct.objects.clear()
        protocol.BaseMessage.objects.clear()
        protocol.PluginRegister.clean_up_registered_plugins()
        protocol.PluginRegister.unset_context_theme()

        self.theme_name = 'testtheme'
        self.plugin_name = 'testplugin'

    def test_register(self):
        class TestPlugin(protocol.BasePlugin):
            theme = self.theme_name
            plugin = self.plugin_name

            def run(self):
                pass

        self.assertDictEqual(
            protocol.PluginRegister.get_registered_plugins(),
            {protocol.PluginIndex(self.theme_name, self.plugin_name):
             TestPlugin},
        )

    def test_theme_name(self):

        protocol.PluginRegister.context_theme = self.theme_name
        temp_theme_name = 'theme_name_for_test'

        class PluginWithThemeName(protocol.BasePlugin):
            theme = temp_theme_name
            plugin = self.plugin_name

            def run(self):
                pass

        class PluginWithoutThemeName(protocol.BasePlugin):
            plugin = self.plugin_name

            def run(self):
                pass

        self.assertSetEqual(
            # get theme_names
            set(protocol.PluginRegister.get_registered_plugins()),
            set((
                protocol.PluginIndex(temp_theme_name, self.plugin_name),
                protocol.PluginIndex(self.theme_name, self.plugin_name),
                )),
        )

    def test_plugin_name(self):

        protocol.PluginRegister.context_theme = self.theme_name

        class PluginWithPluginName(protocol.BasePlugin):
            plugin = self.plugin_name

            def run(self):
                pass

        class PluginWithoutPluginName(protocol.BasePlugin):

            def run(self):
                pass

        self.assertSetEqual(
            # get theme_names
            set(protocol.PluginRegister.get_registered_plugins()),
            set((
                protocol.PluginIndex(self.theme_name, self.plugin_name),
                protocol.PluginIndex(self.theme_name,
                                     'PluginWithoutPluginName'),
                )),
        )

    def test_default_params(self):

        class TestResource(protocol.BaseResource):

            def __init__(self):
                pass

        class TestProduct(protocol.BaseProduct):

            def __init__(self):
                pass

        class TestMessage(protocol.BaseMessage):

            def __init__(self):
                pass

        theme_zero = 'zero'
        theme_one = 'one'
        theme_three = 'three'

        for theme_name in [theme_zero, theme_one, theme_three]:
            TestResource.objects.create(owner=theme_name)
            TestProduct.objects.create(owner=theme_name)
            TestMessage.objects.create(owner=theme_name)

        test_self = self

        class PluginZeroParam(protocol.BasePlugin):
            theme = theme_zero

            def run(self):
                pass

        class PluginOneParam(protocol.BasePlugin):
            theme = theme_one

            def run(self, resources):
                test_self.assertEqual(len(resources), 1)
                test_self.assertIsInstance(resources[0], TestResource)

        class PluginThreeParam(protocol.BasePlugin):
            theme = theme_three

            def run(self, resources, products, messages):
                test_self.assertEqual(len(resources), 1)
                test_self.assertEqual(len(products), 1)
                test_self.assertEqual(len(messages), 1)

                test_self.assertIsInstance(resources[0], TestResource)
                test_self.assertIsInstance(products[0], TestProduct)
                test_self.assertIsInstance(messages[0], TestMessage)

        plugin_mapping =\
            protocol.PluginRegister.get_registered_plugins().items()

        for _, plugin_cls in plugin_mapping:
            plugin = plugin_cls()
            plugin.run()

    def test_accept_parameters(self):
        protocol.PluginRegister.context_theme = self.theme_name
        pcl = protocol.PluginController
        test_self = self

        class TestMessageBase(protocol.BaseMessage):

            def __init__(self):
                pass

        class TestMessageDerived(TestMessageBase):
            pass

        TestMessageBase.objects.create(owner=self.theme_name)
        TestMessageDerived.objects.create(owner=self.theme_name)

        class TestPluginBase(protocol.BasePlugin):

            @pcl.accept_parameters(pcl.MESSAGES)
            def run(self, messages):
                test_self.assertEqual(len(messages), 2)
                test_self.assertIsInstance(messages[0], TestMessageBase)
                test_self.assertIsInstance(messages[1], TestMessageBase)

        class TestPluginDerived(protocol.BasePlugin):

            TYPED_PARAMS = {pcl.MESSAGES: TestMessageDerived}

            @pcl.accept_parameters(
                pcl.MESSAGES,
                **TYPED_PARAMS
            )
            def run(self, messages):
                test_self.assertEqual(len(messages), 1)
                test_self.assertIsInstance(messages[0], TestMessageDerived)

        class TestPluginAnotherDerived(protocol.BasePlugin):

            @pcl.accept_parameters(
                (pcl.MESSAGES, TestMessageDerived)
            )
            def run(self, messages):
                test_self.assertEqual(len(messages), 1)
                test_self.assertIsInstance(messages[0], TestMessageDerived)

        plugin_base = TestPluginBase()
        plugin_derived = TestPluginDerived()
        plugin_another_derived = TestPluginDerived()
        plugin_base.run()
        plugin_derived.run()
        plugin_another_derived.run()

    def test_accept_owners(self):
        protocol.PluginRegister.context_theme = self.theme_name
        pcl = protocol.PluginController
        test_self = self

        class TestResource(protocol.BaseResource):

            def __init__(self):
                pass

        target_theme_name = 'a'
        noice_theme_name = 'b'

        TestResource.objects.create(owner=target_theme_name)
        TestResource.objects.create(owner=noice_theme_name)

        class TestPlugin(protocol.BasePlugin):
            theme = noice_theme_name

            @pcl.accept_owners(target_theme_name)
            def run(self, resources):
                test_self.assertEqual(len(resources), 1)
                test_self.assertIsInstance(resources[0], TestResource)

        plugin = TestPlugin()
        plugin.run()

if __name__ == '__main__':
    unittest.main()
