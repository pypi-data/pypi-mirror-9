from ringo.tests import BaseUnitTest
from ringo.lib.imexport import JSONExporter

class GlobalTests(BaseUnitTest):

    def test_clear_cache(self):
        from ringo.lib.cache import CACHE_TABLE_CONFIG, CACHE_FORM_CONFIG
        CACHE_TABLE_CONFIG.clear()
        CACHE_FORM_CONFIG.clear()

class BaseItemTests(BaseUnitTest):

    def _load_item(self):
        from ringo.model.modul import ModulItem
        factory = ModulItem.get_item_factory()
        return factory.load(1)

    def test_load_item(self):
        item = self._load_item()
        result = item.render()
        self.assertEqual(result, "modules")

    def test_get_item(self):
        item = self._load_item()
        result = item['name']
        self.assertEqual(result, "modules")

    def test_unicode(self):
        item = self._load_item()
        result = unicode(item)
        self.assertEqual(result, u"modules")

    def test_json(self):
        item = self._load_item()
        exporter = JSONExporter(item.__class__)
        result = exporter.perform([item])
        self.assertEqual(len(result), len('[{"str_repr": "%s|name", "description": "", "name": "modules", "label": "Modul", "gid": "", "id": "1", "label_plural": "Modules", "display": "admin-menu", "clazzpath": "ringo.model.modul.ModulItem", "uuid": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"}]'))

    def test_get_form_config(self):
        from ringo.model.modul import ModulItem
        from ringo.lib.form import get_form_config
        factory = ModulItem.get_item_factory()
        item = factory.load(1)
        result = get_form_config(item, 'create')
        self.assertEqual(result.id, 'create')

    def test_get_action_routename(self):
        from ringo.model.modul import ModulItem
        from ringo.lib.helpers import get_action_routename
        result = get_action_routename(ModulItem, 'create')
        self.assertEqual(result, 'modules-create')

    def test_get_action_routename_prefixed(self):
        from ringo.model.modul import ModulItem
        from ringo.lib.helpers import get_action_routename
        result = get_action_routename(ModulItem, 'create', 'rest')
        self.assertEqual(result, 'rest-modules-create')

    def test_get_values(self):
        item = self._load_item()
        result = item.get_values()
        self.assertEqual(result['name'], 'modules')

    def test_get_serialized_values(self):
        item = self._load_item()
        result = item.get_values(serialized=True)
        self.assertEqual(result['name'], 'modules')

    def test_save(self):
        item = self._load_item()
        values = item.get_values()
        item.save(values)
        self.assertEqual(item['name'], 'modules')

    def test_get_item_factory(self):
        from ringo.model.modul import ModulItem
        from ringo.model.base import BaseFactory
        result = ModulItem.get_item_factory()
        self.assertEqual(result._clazz, ModulItem)
        self.assertTrue(isinstance(result, BaseFactory))

    def test_get_item_list(self):
        from ringo.model.modul import ModulItem
        from ringo.model.base import BaseList, get_item_list
        result = get_item_list(self.request, ModulItem, user=None)
        self.assertTrue(isinstance(result, BaseList))

    def test_get_item_actions(self):
        from ringo.model.modul import ModulItem
        from ringo.model.modul import ActionItem
        from ringo.lib.helpers import get_item_actions
        result = get_item_actions(self.request, ModulItem)
        self.assertTrue(isinstance(result, list))
        if len(result) > 0:
            self.assertTrue(isinstance(result[0], ActionItem))
