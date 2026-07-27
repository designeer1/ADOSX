from django.test import TestCase
import pandas as pd
from .utils.comparator import RecordComparator

class ComparatorLogicTests(TestCase):
    
    def test_catches_missing_in_a(self):
        """Test: record in B but not in A"""
        df_a = pd.DataFrame({'record_id': ['1'], 'value': ['100']})
        df_b = pd.DataFrame({'record_ref': ['1', '2'], 'value': ['100', '200']})
        
        comparator = RecordComparator(df_a, df_b)
        disagreements = comparator.compare()
        
        only_b = [d for d in disagreements if d.reason == 'record_only_in_b']
        self.assertEqual(len(only_b), 1)
        self.assertEqual(only_b[0].record_id, '2')
    
    def test_catches_missing_in_b(self):
        """Test: record in A but not in B"""
        df_a = pd.DataFrame({'record_id': ['1', '2'], 'value': ['100', '200']})
        df_b = pd.DataFrame({'record_ref': ['1'], 'value': ['100']})
        
        comparator = RecordComparator(df_a, df_b)
        disagreements = comparator.compare()
        
        only_a = [d for d in disagreements if d.reason == 'record_only_in_a']
        self.assertEqual(len(only_a), 1)
        self.assertEqual(only_a[0].record_id, '2')
    
    def test_catches_duplicate_in_b(self):
        """Test: duplicate entries in System B"""
        df_a = pd.DataFrame({'record_id': ['1'], 'value': ['100']})
        df_b = pd.DataFrame({
            'record_ref': ['1', '1'],
            'value': ['100', '100'],
            'entry_id': ['ENT-1', 'ENT-2']
        })
        
        comparator = RecordComparator(df_a, df_b)
        disagreements = comparator.compare()
        
        duplicates = [d for d in disagreements if d.reason == 'duplicate_in_b']
        self.assertEqual(len(duplicates), 1)
    
    def test_catches_numeric_difference(self):
        """Test: numeric values differ"""
        df_a = pd.DataFrame({'record_id': ['1'], 'amount': ['100']})
        df_b = pd.DataFrame({'record_ref': ['1'], 'value': ['150']})
        
        comparator = RecordComparator(df_a, df_b)
        disagreements = comparator.compare()
        
        diff = [d for d in disagreements if d.reason == 'numeric_difference']
        self.assertEqual(len(diff), 1)
    
    def test_handles_trailing_zeros_as_equal(self):
        """Test: 100.0 == 100"""
        df_a = pd.DataFrame({'record_id': ['1'], 'amount': ['100']})
        df_b = pd.DataFrame({'record_ref': ['1'], 'value': ['100.0']})
        
        comparator = RecordComparator(df_a, df_b)
        disagreements = comparator.compare()
        
        self.assertEqual(len(disagreements), 0)
    
    def test_handles_dirty_data(self):
        """Test: dirty data survives without errors"""
        df_a = pd.DataFrame({
            'record_id': ['1', '2', None, ''],
            'value': ['100', '200', None, '400']
        })
        df_b = pd.DataFrame({
            'record_ref': ['1', '2', '3', ''],
            'value': ['100', '200', '300', '']
        })
        
        comparator = RecordComparator(df_a, df_b)
        disagreements = comparator.compare()
        
        self.assertIsInstance(disagreements, list)