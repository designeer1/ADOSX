import pandas as pd
import re
from typing import List, Optional, Any, Dict
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

class Disagreement:
    def __init__(self, record_id: str, field_name: str, 
                 system_a_value: Any, system_b_value: Any, 
                 reason: str, location: str):
        self.record_id = record_id
        self.field_name = field_name
        self.system_a_value = system_a_value
        self.system_b_value = system_b_value
        self.reason = reason
        self.location = location

class RecordComparator:
    """Compare records between System A and System B - Only matching columns"""
    
    def __init__(self, df_a: pd.DataFrame, df_b: pd.DataFrame, 
                 df_locations: Optional[pd.DataFrame] = None):
        self.df_a = df_a
        self.df_b = df_b
        self.df_locations = df_locations
        self.disagreements = []
        self.all_results = []
        self.matched_count = 0
        self.duplicate_entries = []
        self.column_mappings = {}
        
    def compare(self) -> List[Disagreement]:
        """Compare all records and return ONLY REAL disagreements"""
        self.disagreements = []
        self.all_results = []
        self.matched_count = 0
        self.duplicate_entries = []
        
        # Clean the data
        self._clean_data()
        
        # Map columns between systems
        self._map_columns()
        
        # Get IDs
        ids_a = self._get_ids_from_a()
        ids_b = self._get_ids_from_b()
        
        # Check for duplicate entries in B
        self._check_duplicates(ids_b)
        
        # Find common IDs
        common_ids = set(ids_a.keys()) & set(ids_b.keys())
        
        # Compare common records
        for record_id in common_ids:
            self._compare_record(record_id, ids_a[record_id], ids_b[record_id])
        
        # Records only in A
        only_a = set(ids_a.keys()) - set(ids_b.keys())
        for record_id in only_a:
            location = self._get_location(record_id)
            row_a = self.df_a.iloc[ids_a[record_id]]
            
            self.all_results.append({
                'record_id': record_id,
                'system_a_row': row_a.to_dict(),
                'system_b_row': {},
                'is_matched': False
            })
            
            self.disagreements.append(Disagreement(
                record_id=record_id,
                field_name='[RECORD]',
                system_a_value='Present in System A',
                system_b_value='Missing in System B',
                reason='record_only_in_a',
                location=location
            ))
        
        # Records only in B
        only_b = set(ids_b.keys()) - set(ids_a.keys())
        for record_id in only_b:
            location = self._get_location(record_id)
            row_b = self.df_b.iloc[ids_b[record_id][0]]
            
            self.all_results.append({
                'record_id': record_id,
                'system_a_row': {},
                'system_b_row': row_b.to_dict(),
                'is_matched': False
            })
            
            self.disagreements.append(Disagreement(
                record_id=record_id,
                field_name='[RECORD]',
                system_a_value='Missing in System A',
                system_b_value='Present in System B',
                reason='record_only_in_b',
                location=location
            ))
        
        return self.disagreements
    
    def _clean_data(self):
        """Clean column names and data"""
        self.df_a.columns = [c.strip().lower() for c in self.df_a.columns]
        self.df_b.columns = [c.strip().lower() for c in self.df_b.columns]
        if self.df_locations is not None:
            self.df_locations.columns = [c.strip().lower() for c in self.df_locations.columns]
    
    def _map_columns(self):
        """Map columns between System A and System B - ONLY matching columns"""
        a_cols = set(self.df_a.columns)
        b_cols = set(self.df_b.columns)
        
        # Define which columns to compare (matching columns only)
        # These are the columns that exist in both systems with different names
        mapping_pairs = [
            ('total_value', 'value'),      # System A total_value -> System B value
            ('event_date', 'recorded_on'), # System A event_date -> System B recorded_on
            ('location_id', 'location_id'), # Same in both
        ]
        
        # Add exact matches (columns with same name in both systems)
        for col in a_cols:
            if col in b_cols and col not in ['record_id', 'record_ref', 'entry_id']:
                if col not in [pair[0] for pair in mapping_pairs]:
                    mapping_pairs.append((col, col))
        
        # Store the mappings
        for a_col, b_col in mapping_pairs:
            if a_col in a_cols and b_col in b_cols:
                self.column_mappings[a_col] = b_col
        
        logger.info(f"Comparing these mapped columns: {list(self.column_mappings.keys())}")
    
    def _normalize_id(self, id_val: Any) -> str:
        """Normalize record ID for comparison"""
        if pd.isna(id_val):
            return ''
        id_str = str(id_val).strip()
        id_str = re.sub(r'^REC-', '', id_str, flags=re.IGNORECASE)
        id_str = re.sub(r'^rec', '', id_str, flags=re.IGNORECASE)
        id_str = re.sub(r'^ENT/\d+/', '', id_str, flags=re.IGNORECASE)
        id_str = re.sub(r'^REC', '', id_str, flags=re.IGNORECASE)
        id_str = re.sub(r'[^a-zA-Z0-9]', '', id_str)
        return id_str.upper()
    
    def _get_ids_from_a(self) -> Dict[str, int]:
        """Get IDs from System A"""
        ids = {}
        for idx, row in self.df_a.iterrows():
            raw_id = row.get('record_id')
            if pd.isna(raw_id):
                continue
            normalized = self._normalize_id(raw_id)
            if normalized:
                ids[normalized] = idx
        return ids
    
    def _get_ids_from_b(self) -> Dict[str, List[int]]:
        """Get IDs from System B"""
        ids = {}
        for idx, row in self.df_b.iterrows():
            raw_ref = row.get('record_ref')
            if pd.isna(raw_ref):
                continue
            normalized = self._normalize_id(raw_ref)
            if normalized:
                if normalized not in ids:
                    ids[normalized] = []
                ids[normalized].append(idx)
        return ids
    
    def _check_duplicates(self, ids_b: Dict[str, List[int]]):
        """Check for duplicate entries in System B"""
        for record_id, indices in ids_b.items():
            if len(indices) > 1:
                location = self._get_location(record_id)
                self.disagreements.append(Disagreement(
                    record_id=record_id,
                    field_name='[DUPLICATE]',
                    system_a_value=f'Found {len(indices)} entries',
                    system_b_value=f'Multiple entries in System B',
                    reason='duplicate_in_b',
                    location=location
                ))
    
    def _get_location(self, record_id: str) -> str:
        """Get location name from locations.csv"""
        if self.df_locations is None:
            return f"Record {record_id}"
        
        try:
            row_a = self.df_a[self.df_a['record_id'].astype(str).str.strip() == record_id]
            if not row_a.empty and 'location_id' in row_a.columns:
                loc_id = row_a.iloc[0]['location_id']
                if not pd.isna(loc_id):
                    loc_row = self.df_locations[
                        self.df_locations['location_id'].astype(str).str.strip() == str(loc_id)
                    ]
                    if not loc_row.empty:
                        loc_name = loc_row.iloc[0]['location_name']
                        org_id = loc_row.iloc[0]['org_id']
                        return f"{loc_name} ({org_id})"
            
            row_b = self.df_b[self.df_b['record_ref'].astype(str).str.strip() == record_id]
            if not row_b.empty and 'location_id' in row_b.columns:
                loc_id = row_b.iloc[0]['location_id']
                if not pd.isna(loc_id):
                    loc_row = self.df_locations[
                        self.df_locations['location_id'].astype(str).str.strip() == str(loc_id)
                    ]
                    if not loc_row.empty:
                        loc_name = loc_row.iloc[0]['location_name']
                        org_id = loc_row.iloc[0]['org_id']
                        return f"{loc_name} ({org_id})"
        except Exception as e:
            logger.warning(f"Could not get location: {e}")
        
        return f"Record {record_id}"
    
    def _compare_record(self, record_id: str, idx_a: int, idx_b_list: List[int]):
        """Compare a single record - ONLY mapped columns"""
        row_a = self.df_a.iloc[idx_a]
        row_b = self.df_b.iloc[idx_b_list[0]]
        location = self._get_location(record_id)
        
        has_disagreement = False
        
        # Compare ONLY mapped columns
        for a_col, b_col in self.column_mappings.items():
            if a_col in row_a.index and b_col in row_b.index:
                val_a = row_a[a_col]
                val_b = row_b[b_col]
                
                # Compare values
                if not self._values_equal(val_a, val_b):
                    reason = self._get_reason(val_a, val_b)
                    has_disagreement = True
                    self.disagreements.append(Disagreement(
                        record_id=record_id,
                        field_name=a_col,
                        system_a_value=val_a,
                        system_b_value=val_b,
                        reason=reason,
                        location=location
                    ))
        
        # Store result for CSV generation
        self.all_results.append({
            'record_id': record_id,
            'system_a_row': row_a.to_dict(),
            'system_b_row': row_b.to_dict(),
            'is_matched': not has_disagreement
        })
        
        if not has_disagreement:
            self.matched_count += 1
    
    def _values_equal(self, val_a: Any, val_b: Any) -> bool:
        """Check if two values are equal"""
        # Both None/NaN
        if pd.isna(val_a) and pd.isna(val_b):
            return True
        
        # One is None/NaN
        if pd.isna(val_a) or pd.isna(val_b):
            return False
        
        # Try numeric comparison
        try:
            str_a = str(val_a).strip().replace(',', '')
            str_b = str(val_b).strip().replace(',', '')
            # Remove non-numeric chars for comparison
            str_a = re.sub(r'[^\d.\-]', '', str_a)
            str_b = re.sub(r'[^\d.\-]', '', str_b)
            
            if str_a and str_b:
                num_a = Decimal(str_a)
                num_b = Decimal(str_b)
                return num_a == num_b
        except:
            pass
        
        # Try date comparison
        try:
            date_a = pd.to_datetime(val_a, errors='coerce')
            date_b = pd.to_datetime(val_b, errors='coerce')
            if pd.notna(date_a) and pd.notna(date_b):
                return date_a == date_b
        except:
            pass
        
        # String comparison (case insensitive, trimmed)
        str_a = str(val_a).strip()
        str_b = str(val_b).strip()
        
        if str_a.lower() == str_b.lower():
            return True
        
        # Check if category code is in label
        if 'label' in str_b and str_a in str_b:
            return True
        
        return False
    
    def _get_reason(self, val_a: Any, val_b: Any) -> str:
        """Determine the reason for disagreement"""
        str_a = str(val_a).strip() if not pd.isna(val_a) else ''
        str_b = str(val_b).strip() if not pd.isna(val_b) else ''
        
        if str_a == '' and str_b != '':
            return 'missing_in_a'
        if str_a != '' and str_b == '':
            return 'missing_in_b'
        if str_a == '' and str_b == '':
            return 'both_missing'
        
        # Try numeric
        try:
            clean_a = re.sub(r'[^\d.\-]', '', str_a)
            clean_b = re.sub(r'[^\d.\-]', '', str_b)
            if clean_a and clean_b:
                num_a = float(clean_a)
                num_b = float(clean_b)
                if num_a != num_b:
                    if abs(num_a - num_b) < 0.01:
                        return 'rounding_difference'
                    return 'numeric_difference'
        except:
            pass
        
        # Try date
        try:
            date_a = pd.to_datetime(str_a, errors='coerce')
            date_b = pd.to_datetime(str_b, errors='coerce')
            if pd.notna(date_a) and pd.notna(date_b) and date_a != date_b:
                return 'date_difference'
        except:
            pass
        
        if str_a.lower() == str_b.lower():
            return 'case_difference'
        
        if str_a.strip() == str_b.strip():
            return 'whitespace_difference'
        
        return 'value_mismatch'