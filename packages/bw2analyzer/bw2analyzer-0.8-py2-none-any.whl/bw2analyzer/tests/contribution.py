import unittest
import numpy as np
from ..contribution import ContributionAnalysis as CA
from scipy import sparse

class ContributionTestCase(unittest.TestCase):
    def test_sort_array_number(self):
        test_data = np.array((1., 2., 4., 3.))
        answer = np.array((
            (4, 2),
            (3, 3),
            (2, 1),
        ))
        ca = CA()
        self.assertTrue(np.allclose(
            answer,
            ca.sort_array(test_data, limit=3)
        ))

    def test_sort_array_percentage(self):
        test_data = np.array((1., 2., 4., 3.))
        answer = np.array((
            (4, 2),
            (3, 3),
        ))
        ca = CA()
        self.assertTrue(np.allclose(
            answer,
            ca.sort_array(test_data, limit=0.3, limit_type='percent')
        ))

    def test_sort_array_errors(self):
        ca = CA()
        with self.assertRaises(ValueError):
            ca.sort_array([], limit_type='foo', total=1.)
        with self.assertRaises(ValueError):
            ca.sort_array([], limit=0., limit_type='percent', total=1.)
        with self.assertRaises(ValueError):
            ca.sort_array([], limit=1.01, limit_type='percent', total=1.)

    def test_top_matrix_array(self):
        matrix = np.array([
            [0, 0, 1, 0],
            [2, 0, 4, 0],
            [3, 0, 1, 1],
            [0, 7, 0, 1]
        ])
        ca = CA()
        elements, rows, columns = ca.top_matrix(matrix, 2, 2)
        self.assertTrue(np.allclose((3, 1), rows))
        self.assertTrue(np.allclose((1, 2), columns))
        self.assertEqual(
            [(3, 1, 0, 0, 7), (1, 2, 1, 1, 4)],
            elements
        )

    def test_top_matrix_matrix(self):
        matrix = sparse.lil_matrix((4,4))
        input_data = [
            [0, 0, 1, 0],
            [2, 0, 4, 0],
            [3, 0, 1, 1],
            [0, 7, 0, 1]
        ]
        for row in range(4):
            for col in range(4):
                if input_data[row][col]:
                    matrix[row, col] = input_data[row][col]
        matrix = matrix.tocsr()
        ca = CA()
        elements, rows, columns = ca.top_matrix(matrix, 2, 2)
        self.assertTrue(np.allclose((3, 1), rows))
        self.assertTrue(np.allclose((1, 2), columns))
        self.assertEqual(
            [(3, 1, 0, 0, 7), (1, 2, 1, 1, 4)],
            elements
        )
