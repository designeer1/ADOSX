import pandas as pd
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .utils.comparator import RecordComparator
from .models import SystemARecord, SystemBRecord, Location, ComparisonResult
from .serializers import ComparisonResultSerializer
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
def compare_files(request):
    """Upload and compare files - ALWAYS fresh data"""
    try:
        file_a = request.FILES.get('file_a')
        file_b = request.FILES.get('file_b')
        file_locations = request.FILES.get('file_locations', None)
        
        if not file_a or not file_b:
            return Response(
                {'error': 'Both files are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 🔥 FORCE CLEAR ALL OLD DATA
        logger.info("🔴 FORCE CLEARING ALL DATA...")
        ComparisonResult.objects.all().delete()
        SystemARecord.objects.all().delete()
        SystemBRecord.objects.all().delete()
        Location.objects.all().delete()
        logger.info("✅ All data cleared")
        
        # Read files
        try:
            df_a = read_file(file_a)
            df_b = read_file(file_b)
            df_locations = read_file(file_locations) if file_locations else None
            
            # 🔥 CRITICAL: Remove empty rows (rows where ALL values are empty/NaN)
            df_a = df_a.dropna(how='all')
            df_b = df_b.dropna(how='all')
            
            # Also remove rows where record_id/record_ref is empty
            if 'record_id' in df_a.columns:
                df_a = df_a[df_a['record_id'].astype(str).str.strip() != '']
                df_a = df_a[df_a['record_id'].astype(str).str.strip() != 'nan']
                df_a = df_a[df_a['record_id'].notna()]
            
            if 'record_ref' in df_b.columns:
                df_b = df_b[df_b['record_ref'].astype(str).str.strip() != '']
                df_b = df_b[df_b['record_ref'].astype(str).str.strip() != 'nan']
                df_b = df_b[df_b['record_ref'].notna()]
            
            # 🔥 Also remove rows where entry_id is empty
            if 'entry_id' in df_b.columns:
                df_b = df_b[df_b['entry_id'].astype(str).str.strip() != '']
                df_b = df_b[df_b['entry_id'].astype(str).str.strip() != 'nan']
                df_b = df_b[df_b['entry_id'].notna()]
            
            logger.info(f"📊 System A: {len(df_a)} rows (after cleaning)")
            logger.info(f"📊 System B: {len(df_b)} rows (after cleaning)")
            
            if df_locations is not None:
                df_locations = df_locations.dropna(how='all')
                if 'location_id' in df_locations.columns:
                    df_locations = df_locations[df_locations['location_id'].astype(str).str.strip() != '']
                    df_locations = df_locations[df_locations['location_id'].notna()]
                logger.info(f"📊 Locations: {len(df_locations)} rows")
            
            # Store in session
            request.session['df_a'] = df_a.to_json()
            request.session['df_b'] = df_b.to_json()
            if df_locations is not None:
                request.session['df_locations'] = df_locations.to_json()
            
            # Save to database
            save_to_database(df_a, df_b, df_locations)
            
        except Exception as e:
            logger.error(f"❌ Error reading files: {str(e)}")
            return Response(
                {'error': f'Error reading files: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Compare
        comparator = RecordComparator(df_a, df_b, df_locations)
        disagreements = comparator.compare()
        
        # Store all results for CSV generation
        request.session['all_results'] = comparator.all_results
        
        # Save results
        results = []
        for d in disagreements:
            a_val = str(d.system_a_value) if d.system_a_value is not None else ''
            b_val = str(d.system_b_value) if d.system_b_value is not None else ''
            
            result = ComparisonResult.objects.create(
                record_id=d.record_id,
                field_name=d.field_name,
                system_a_value=a_val[:500] if len(a_val) > 500 else a_val,
                system_b_value=b_val[:500] if len(b_val) > 500 else b_val,
                reason=d.reason,
                location=d.location
            )
            results.append(result)
        
        # Prepare response with FRESH data
        total_a = len(df_a)
        total_b = len(df_b)
        
        ids_a = set()
        if 'record_id' in df_a.columns:
            ids_a = set(df_a['record_id'].astype(str).str.strip())
        
        ids_b = set()
        if 'record_ref' in df_b.columns:
            ids_b = set(df_b['record_ref'].astype(str).str.strip())
        
        common = len(ids_a.intersection(ids_b))
        
        records_with_issues = set()
        for d in disagreements:
            if '[DUPLICATE' not in d.field_name and d.record_id != '[DUPLICATE]':
                records_with_issues.add(d.record_id)
        
        records_matched = common - len(records_with_issues)
        
        serializer = ComparisonResultSerializer(results, many=True)
        
        logger.info(f"📊 Response: A={total_a}, B={total_b}, Common={common}, Matched={records_matched}, Disagreements={len(results)}")
        
        return Response({
            'total_records_a': total_a,
            'total_records_b': total_b,
            'common_records': common,
            'records_matched': records_matched,
            'records_with_issues': len(records_with_issues),
            'field_disagreements': len(results),
            'results': serializer.data,
            'summary': get_summary(results),
            'columns_a': df_a.columns.tolist() if not df_a.empty else [],
            'columns_b': df_b.columns.tolist() if not df_b.empty else []
        })
        
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}", exc_info=True)
        return Response(
            {'error': f'An error occurred: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

def read_file(file):
    if file is None:
        return None
    filename = file.name.lower()
    if filename.endswith('.csv'):
        return pd.read_csv(file)
    elif filename.endswith(('.xlsx', '.xls')):
        return pd.read_excel(file)
    else:
        raise ValueError(f"Unsupported file format: {filename}")

def save_to_database(df_a, df_b, df_locations):
    """Save data to database - skip empty rows and duplicates"""
    
    # Save System A
    count_a = 0
    for _, row in df_a.iterrows():
        try:
            record_id = str(row.get('record_id', '')).strip()
            if not record_id or record_id == 'nan' or record_id == '':
                continue
            
            SystemARecord.objects.create(
                record_id=record_id,
                location_id=str(row.get('location_id', '')) if pd.notna(row.get('location_id')) else '',
                event_date=str(row.get('event_date', '')) if pd.notna(row.get('event_date')) else '',
                category_code=str(row.get('category_code', '')) if pd.notna(row.get('category_code')) else '',
                actor_id=str(row.get('actor_id', '')) if pd.notna(row.get('actor_id')) else '',
                base_value=str(row.get('base_value', '')) if pd.notna(row.get('base_value')) else '',
                adjustment=str(row.get('adjustment', '')) if pd.notna(row.get('adjustment')) else '',
                total_value=str(row.get('total_value', '')) if pd.notna(row.get('total_value')) else '',
                state=str(row.get('state', '')) if pd.notna(row.get('state')) else ''
            )
            count_a += 1
        except Exception as e:
            logger.warning(f"⚠️ Error saving System A row: {e}")
            continue
    
    # Save System B
    count_b = 0
    for _, row in df_b.iterrows():
        try:
            entry_id = str(row.get('entry_id', '')).strip()
            if not entry_id or entry_id == 'nan' or entry_id == '':
                continue
            
            record_ref = str(row.get('record_ref', '')).strip()
            if not record_ref or record_ref == 'nan' or record_ref == '':
                continue
            
            # Skip if entry_id already exists (avoid duplicates)
            if SystemBRecord.objects.filter(entry_id=entry_id).exists():
                logger.warning(f"⚠️ Skipping duplicate entry_id: {entry_id}")
                continue
            
            SystemBRecord.objects.create(
                entry_id=entry_id,
                record_ref=record_ref,
                location_id=str(row.get('location_id', '')) if pd.notna(row.get('location_id')) else '',
                recorded_on=str(row.get('recorded_on', '')) if pd.notna(row.get('recorded_on')) else '',
                value=str(row.get('value', '')) if pd.notna(row.get('value')) else '',
                label=str(row.get('label', '')) if pd.notna(row.get('label')) else ''
            )
            count_b += 1
        except Exception as e:
            logger.warning(f"⚠️ Error saving System B row: {e}")
            continue
    
    # Save Locations
    if df_locations is not None:
        count_loc = 0
        for _, row in df_locations.iterrows():
            try:
                location_id = str(row.get('location_id', '')).strip()
                if not location_id or location_id == 'nan' or location_id == '':
                    continue
                
                if Location.objects.filter(location_id=location_id).exists():
                    continue
                
                Location.objects.create(
                    location_id=location_id,
                    org_id=str(row.get('org_id', '')) if pd.notna(row.get('org_id')) else '',
                    location_name=str(row.get('location_name', '')) if pd.notna(row.get('location_name')) else ''
                )
                count_loc += 1
            except Exception as e:
                logger.warning(f"⚠️ Error saving Location: {e}")
                continue
        logger.info(f"✅ Saved {count_loc} Locations")
    
    logger.info(f"✅ Saved {count_a} System A records")
    logger.info(f"✅ Saved {count_b} System B records")

def get_summary(results):
    summary = {}
    for r in results:
        friendly_names = {
            'missing_in_a': 'Missing in System A',
            'missing_in_b': 'Missing in System B',
            'both_missing': 'Missing in Both',
            'numeric_difference': 'Numeric Difference',
            'rounding_difference': 'Rounding Difference',
            'case_difference': 'Case Difference',
            'whitespace_difference': 'Whitespace Difference',
            'value_mismatch': 'Value Mismatch',
            'record_only_in_a': 'Record Only in A',
            'record_only_in_b': 'Record Only in B',
            'duplicate_in_b': 'Duplicate in B',
            'date_difference': 'Date Difference',
            'field_only_in_a': 'Field Only in A',
            'field_only_in_b': 'Field Only in B'
        }
        key = friendly_names.get(r.reason, r.reason)
        if key not in summary:
            summary[key] = 0
        summary[key] += 1
    return summary

@api_view(['GET'])
def get_results(request):
    """Get all results with optional filter"""
    results = ComparisonResult.objects.all()
    
    reason = request.query_params.get('reason')
    if reason:
        results = results.filter(reason=reason)
    
    results = results.order_by('record_id')
    serializer = ComparisonResultSerializer(results, many=True)
    return Response({
        'count': len(serializer.data),
        'results': serializer.data
    })

@api_view(['GET'])
def get_reasons(request):
    """Get list of all reasons with counts"""
    from django.db.models import Count
    reasons = ComparisonResult.objects.values('reason').annotate(count=Count('reason'))
    return Response(reasons)

@api_view(['POST'])
def clear_data(request):
    """Clear all data from the database"""
    try:
        ComparisonResult.objects.all().delete()
        SystemARecord.objects.all().delete()
        SystemBRecord.objects.all().delete()
        Location.objects.all().delete()
        return Response({'message': 'All data cleared successfully'})
    except Exception as e:
        return Response(
            {'error': f'Error clearing data: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )