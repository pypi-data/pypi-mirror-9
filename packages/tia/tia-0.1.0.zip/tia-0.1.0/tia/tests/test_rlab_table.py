import unittest
import pandas as pd
import pandas.util.testing as pdtest

import tia.rlab.table as tbl


class TestTable(unittest.TestCase):
    def setUp(self):
        self.df1 = df1 = pd.DataFrame({'A': [.55, .65], 'B': [1234., -5678.]}, index=['I1', 'I2'])
        # Multi-index frame with multi-index
        cols = pd.MultiIndex.from_arrays([['LEFT', 'LEFT', 'RIGHT', 'RIGHT'], ['A', 'B', 'A', 'B']])
        idx = pd.MultiIndex.from_arrays([['TOP', 'BOTTOM'], ['I1', 'I2']])
        self.mdf1 = pd.DataFrame([[.55, 1234., .55, 1234.], [.65, -5678., .65, -5678.]], columns=cols, index=idx)

    def test_span_iter(self):
        s = pd.Series([1, 1, 1, 3, 2, 2])
        items = list(tbl.span_iter(s))
        self.assertEquals(items, [(0, 2), (4, 5)])
        # reverse and ensure it does not break it
        s = s[::-1]
        items = list(tbl.span_iter(s))
        self.assertEquals(items, [(0, 2), (4, 5)])

    def test_level_iter(self):
        l1 = ['L_11', 'L_12']
        l2 = ['L_21', 'L_22']
        l3 = ['L_31', 'L_32']
        midx = pd.MultiIndex.from_arrays([l1, l2, l3], names=['1', '2', '3'])
        actual = list(tbl.level_iter(midx))
        expected = [(0, 0, 'L_11'), (0, 1, 'L_12'), (1, 0, 'L_21'), (1, 1, 'L_22'), (2, 0, 'L_31'), (2, 1, 'L_32')]
        self.assertEquals(actual, expected)

        actual = list(tbl.level_iter(midx, levels=[0, 2]))
        expected = [(0, 0, 'L_11'), (0, 1, 'L_12'), (2, 0, 'L_31'), (2, 1, 'L_32')]
        self.assertEquals(actual, expected)

        actual = list(tbl.level_iter(midx, levels=0))
        expected = [(0, 0, 'L_11'), (0, 1, 'L_12')]
        self.assertEquals(actual, expected)

    def test_region_formatter_iloc(self):
        tf = tbl.TableFormatter(self.df1)
        region = tf.cells
        region.apply_format(lambda x: 'A')
        expected = pd.DataFrame([['A', 'A'], ['A', 'A']], index=[1, 2], columns=[1, 2])
        pdtest.assert_frame_equal(tf.cells.formatted_values, expected)
        #
        # Use the location
        #
        region = region.iloc[:, 1]
        region.apply_format(lambda x: 'B')
        expected = pd.DataFrame([['A', 'B'], ['A', 'B']], index=[1, 2], columns=[1, 2])
        pdtest.assert_frame_equal(tf.cells.formatted_values, expected)
        # Get single cell
        region = region.iloc[1]
        region.apply_format(lambda x: 'D')
        expected = pd.DataFrame([['A', 'B'], ['A', 'D']], index=[1, 2], columns=[1, 2])
        pdtest.assert_frame_equal(tf.cells.formatted_values, expected)
        # Get single cell
        region = tf.cells.iloc[1, 0]
        region.apply_format(lambda x: 'C')
        expected = pd.DataFrame([['A', 'B'], ['C', 'D']], index=[1, 2], columns=[1, 2])
        pdtest.assert_frame_equal(tf.cells.formatted_values, expected)

    def test_region_empty(self):
        tf = tbl.TableFormatter(self.df1)
        empty = tf['ALL'].empty_frame()
        empty.apply_format(lambda x: x)

    def test_detect_spans(self):
        tf = tbl.TableFormatter(self.mdf1)
        tf.header.detect_colspans()
        self.assertEquals(['SPAN', (2,0), (3,0)], tf.style_cmds[0])
        self.assertEquals(['SPAN', (4,0), (5,0)], tf.style_cmds[1])

        tf = tbl.TableFormatter(self.mdf1.T)
        tf.index.detect_rowspans()
        self.assertEquals(['SPAN', (0,2), (0,3)], tf.style_cmds[0])
        self.assertEquals(['SPAN', (0,4), (0,5)], tf.style_cmds[1])

