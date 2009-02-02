import unittest

facets = [
    'price',
    'price:0-100',
    'price:100-500',
    'price:100-*',
    'color',
    'color:blue',
    'color:red',
    'size',
    'size:small',
    'size:medium',
    'size:large',
    'style',
    'style:gucci',
    'style:gucci:handbag',
    'style:gucci:dress',
    ]

class TestCatalogFacetIndex(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.catalog.indexes.facet import CatalogFacetIndex
        return CatalogFacetIndex

    def _makeOne(self, facets):
        klass = self._getTargetClass()
        return klass(lambda x, default: x, facets)

    def test_class_conforms_to_ICatalogIndex(self):
        from zope.interface.verify import verifyClass
        from repoze.catalog.interfaces import ICatalogIndex
        verifyClass(ICatalogIndex, self._getTargetClass())

    def test_instance_conforms_to_ICatalogIndex(self):
        from zope.interface.verify import verifyObject
        from repoze.catalog.interfaces import ICatalogIndex
        verifyObject(ICatalogIndex, self._makeOne(facets))

    def _populateIndex(self, idx):
        idx.index_doc(1, ['price:0-100', 'color:blue', 'style:gucci:handbag'])
        idx.index_doc(2, ['price:0-100', 'color:blue', 'style:gucci:dress'])
        idx.index_doc(3, ['price:0-100', 'color:red', 'color:blue',
                          'style:gucci'])
        idx.index_doc(4, ['size:large'])

    def test_search(self):
        index = self._makeOne(facets)
        self._populateIndex(index)

        result = index.search(['color:blue', 'color:red'])
        self.assertEqual(sorted(list(result)), [3])
        result = index.search(['price'])
        self.assertEqual(sorted(list(result)), [1,2,3])
        result = index.search(['price:0-100'])
        self.assertEqual(sorted(list(result)), [1,2,3])
        result = index.search(['style:gucci'])
        self.assertEqual(sorted(list(result)), [1,2,3])
        result = index.search(['style:gucci:handbag'])
        self.assertEqual(sorted(list(result)), [1])
        result = index.search(['size'])
        self.assertEqual(sorted(list(result)), [4])
        result = index.search(['size:large'])
        self.assertEqual(sorted(list(result)), [4])
        result = index.search(['size:nonexistent'])
        self.assertEqual(sorted(list(result)), [])
        result = index.search(['nonexistent'])
        self.assertEqual(sorted(list(result)), [])

        index.unindex_doc(1)
        result = index.search(['price'])
        self.assertEqual(sorted(list(result)), [2,3])
        result = index.search(['price:0-100'])
        self.assertEqual(sorted(list(result)), [2,3])
        result = index.search(['style:gucci'])
        self.assertEqual(sorted(list(result)), [2,3])
        result = index.search(['style:gucci:handbag'])
        self.assertEqual(sorted(list(result)), [])
        
        index.unindex_doc(2)
        result = index.search(['price'])
        self.assertEqual(sorted(list(result)), [3])
        result = index.search(['price:0-100'])
        self.assertEqual(sorted(list(result)), [3])
        result = index.search(['style:gucci'])
        self.assertEqual(sorted(list(result)), [3])
        
        index.unindex_doc(4)
        result = index.search(['size'])
        self.assertEqual(sorted(list(result)), [])
        result = index.search(['size:large'])
        self.assertEqual(sorted(list(result)), [])
        result = index.search(['size:nonexistent'])
        self.assertEqual(sorted(list(result)), [])
        result = index.search(['nonexistent'])
        self.assertEqual(sorted(list(result)), [])

    def test_counts(self):
        index = self._makeOne(facets)
        self._populateIndex(index)

        search = ['price:0-100']
        result = index.search(search)
        self.assertEqual(sorted(list(result)), [1,2,3])
        counts = index.counts(result, search)
        self.assertEqual(counts['style'], 3)
        self.assertEqual(counts['style:gucci'], 3)
        self.assertEqual(counts['style:gucci:handbag'], 1)
        self.assertEqual(counts['style:gucci:dress'], 1)
        self.assertEqual(counts['color'], 3)
        self.assertEqual(counts['color:blue'], 3)
        self.assertEqual(counts['color:red'], 1)
        self.assertEqual(len(counts), 7)

        search = ['price:0-100', 'color:red']
        result = index.search(search)
        self.assertEqual(sorted(list(result)), [3])
        counts = index.counts(result, search)
        self.assertEqual(counts['style'], 1)
        self.assertEqual(counts['style:gucci'], 1)
        self.assertEqual(counts['color:blue'], 1)
        self.assertEqual(len(counts), 3)

        search = ['size:large']
        result = index.search(search)
        self.assertEqual(sorted(list(result)), [4])
        counts = index.counts(result, search)
        self.assertEqual(counts, {})

        search = ['size']
        result = index.search(search)
        self.assertEqual(sorted(list(result)), [4])
        counts = index.counts(result, search)
        self.assertEqual(counts, {'size:large':1})
