"""
Test cases for Dimension and Dimensioned object comparison.
"""

from holoviews.core import Dimension, Dimensioned
from holoviews.element.comparison import ComparisonTestCase


class DimensionsComparisonTestCase(ComparisonTestCase):

    def setUp(self):
        super(DimensionsComparisonTestCase, self).setUp()
        self.dimension1 = Dimension('dim1', range=(0,1))
        self.dimension2 = Dimension('dim2', range=(0,1))
        self.dimension3 = Dimension('dim1', range=(0,2))
        self.dimension4 = Dimension('dim1')
        self.dimension5 = Dimension('dim1', cyclic=True)
        self.dimension6 = Dimension('dim1', cyclic=True, range=(0,1))
        self.dimension7 = Dimension('dim1', cyclic=True, range=(0,1), unit='ms')
        self.dimension8 = Dimension('dim1', values=['a', 'b'])
        self.dimension9 = Dimension('dim1', format_string='{name}')
        self.dimension10 = Dimension('dim1', type=int)
        self.dimension11 = Dimension('dim1', type=float)

    def test_dimension_comparison_equal1(self):
        self.assertEqual(self.dimension1, self.dimension1)

    def test_dimension_comparison_equal2(self):
        self.assertEqual(self.dimension1,
                         Dimension('dim1', range=(0,1)))

    def test_dimension_comparison_equal3(self):
        self.assertEqual(self.dimension7,
                         Dimension('dim1', cyclic=True, range=(0,1), unit='ms'))

    def test_dimension_comparison_names_unequal(self):
        try:
            self.assertEqual(self.dimension1, self.dimension2)
        except AssertionError as e:
            self.assertEqual(str(e),  'Dimension names mismatched: dim1 != dim2')

    def test_dimension_comparison_range_unequal1(self):
        try:
            self.assertEqual(self.dimension1, self.dimension3)
        except AssertionError as e:
            self.assertEqual(str(e), 'Dimension ranges mismatched: (0, 1) != (0, 2)')

    def test_dimension_comparison_cyclic_unequal(self):
        try:
            self.assertEqual(self.dimension4, self.dimension5)
        except AssertionError as e:
            self.assertEqual(str(e), 'Dimension cyclic declarations mismatched.')

    def test_dimension_comparison_range_unequal2(self):
        try:
            self.assertEqual(self.dimension5, self.dimension6)
        except AssertionError as e:
            self.assertEqual(str(e), 'Dimension ranges mismatched: (None, None) != (0, 1)')

    def test_dimension_comparison_units_unequal(self):
        try:
            self.assertEqual(self.dimension6, self.dimension7)
        except AssertionError as e:
            self.assertEqual(str(e), 'Dimension unit declarations mismatched: None != ms')

    def test_dimension_comparison_values_unequal(self):
        try:
            self.assertEqual(self.dimension4, self.dimension8)
        except AssertionError as e:
            self.assertEqual(str(e), "Dimension value declarations mismatched: [] != ['a', 'b']")

    def test_dimension_comparison_format_unequal(self):
        try:
            self.assertEqual(self.dimension4, self.dimension9)
        except AssertionError as e:
            self.assertEqual(str(e), 'Dimension format string declarations mismatched: {name}: {val}{unit} != {name}')

    def test_dimension_comparison_types_unequal(self):
        try:
            self.assertEqual(self.dimension10, self.dimension11)
        except AssertionError as e:
            self.assertEqual(str(e)[:39], "Dimension type declarations mismatched:")



class DimensionedComparisonTestCase(ComparisonTestCase):

    def setUp(self):
        super(DimensionedComparisonTestCase, self).setUp()
        # Value dimension lists
        self.value_list1 = [Dimension('val1')]
        self.value_list2 = [Dimension('val2')]
        # Key dimension lists
        self.key_list1 = [Dimension('key1')]
        self.key_list2 = [Dimension('key2')]
        # Dimensioned instances
        self.dimensioned1 = Dimensioned('data1', value_dimensions=self.value_list1,
                                                 key_dimensions=self.key_list1)
        self.dimensioned2 = Dimensioned('data2', value_dimensions=self.value_list2,
                                                 key_dimensions=self.key_list1)

        self.dimensioned3 = Dimensioned('data3', value_dimensions=self.value_list1,
                                                 key_dimensions=self.key_list2)

        self.dimensioned4 = Dimensioned('data4', value_dimensions=[],
                                                 key_dimensions=self.key_list1)

        self.dimensioned5 = Dimensioned('data5', value_dimensions=self.value_list1,
                                                 key_dimensions=[])
        # Value / Label comparison tests
        self.dimensioned6 = Dimensioned('data6', group='foo',
                                        value_dimensions=self.value_list1,
                                        key_dimensions=self.key_list1)

        self.dimensioned7 = Dimensioned('data7', group='foo', label='bar',
                                        value_dimensions=self.value_list1,
                                        key_dimensions=self.key_list1)


    def test_dimensioned_comparison_equal(self):
        "Note that the data is not compared at the Dimensioned level"
        self.assertEqual(self.dimensioned1,
                         Dimensioned('other_data',
                                     value_dimensions=self.value_list1,
                                     key_dimensions=self.key_list1))

    def test_dimensioned_comparison_unequal_value_dims(self):
        try:
            self.assertEqual(self.dimensioned1, self.dimensioned2)
        except AssertionError as e:
            self.assertEqual(str(e), "Dimension names mismatched: val1 != val2")


    def test_dimensioned_comparison_unequal_key_dims(self):
        try:
            self.assertEqual(self.dimensioned1, self.dimensioned3)
        except AssertionError as e:
            self.assertEqual(str(e), 'Dimension names mismatched: key1 != key2')

    def test_dimensioned_comparison_unequal_value_dim_lists(self):
        try:
            self.assertEqual(self.dimensioned1, self.dimensioned4)
        except AssertionError as e:
            self.assertEqual(str(e), "Value dimension list mismatched")

    def test_dimensioned_comparison_unequal_key_dim_lists(self):
        try:
            self.assertEqual(self.dimensioned1, self.dimensioned5)
        except AssertionError as e:
            self.assertEqual(str(e), 'Key dimension list mismatched')

    def test_dimensioned_comparison_unequal_group(self):
        try:
            self.assertEqual(self.dimensioned1, self.dimensioned6)
        except AssertionError as e:
            self.assertEqual(str(e), 'Group labels mismatched.')

    def test_dimensioned_comparison_unequal_label(self):
        try:
            self.assertEqual(self.dimensioned6, self.dimensioned7)
        except AssertionError as e:
            self.assertEqual(str(e), 'Labels mismatched.')


if __name__ == "__main__":
    import sys
    import nose
    nose.runmodule(argv=[sys.argv[0], "--logging-level", "ERROR"])
