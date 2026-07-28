import React, { useState } from 'react';
import './ComparisonTable.css';

function ComparisonTable({ results, loading }) {
    const [expandedRows, setExpandedRows] = useState({});

    if (loading) {
        return (
            <div className="table-container">
                <div className="loading-state">
                    <div className="loading-spinner"></div>
                    <div>Loading disagreements...</div>
                </div>
            </div>
        );
    }

    if (!results || results.length === 0) {
        return null;
    }

    const getReasonColor = (reason) => {
        const colors = {
            'missing_in_a': '#ff4444',
            'missing_in_b': '#ff4444',
            'both_missing': '#ff4444',
            'numeric_difference': '#ffaa00',
            'rounding_difference': '#ffaa00',
            'case_difference': '#44bb88',
            'whitespace_difference': '#44bb88',
            'value_mismatch': '#ff8800',
            'record_only_in_a': '#8888ff',
            'record_only_in_b': '#8888ff',
            'duplicate_in_b': '#ff66aa',
            'date_difference': '#ff66aa',
            'field_only_in_a': '#66aaff',
            'field_only_in_b': '#66aaff'
        };
        return colors[reason] || '#555';
    };

    const getReasonLabel = (reason) => {
        const labels = {
            'missing_in_a': 'Missing in A',
            'missing_in_b': 'Missing in B',
            'both_missing': 'Missing in Both',
            'numeric_difference': 'Numeric Diff',
            'rounding_difference': 'Rounding Diff',
            'case_difference': 'Case Diff',
            'whitespace_difference': 'Whitespace Diff',
            'value_mismatch': 'Value Mismatch',
            'record_only_in_a': 'Only in A',
            'record_only_in_b': 'Only in B',
            'duplicate_in_b': 'Duplicate in B',
            'date_difference': 'Date Diff',
            'field_only_in_a': 'Field Only in A',
            'field_only_in_b': 'Field Only in B'
        };
        return labels[reason] || reason;
    };

    const toggleRow = (recordId) => {
        setExpandedRows(prev => ({
            ...prev,
            [recordId]: !prev[recordId]
        }));
    };

    // Group results by record_id
    const groupedResults = {};
    results.forEach(result => {
        if (!groupedResults[result.record_id]) {
            groupedResults[result.record_id] = [];
        }
        groupedResults[result.record_id].push(result);
    });

    const sortedRecordIds = Object.keys(groupedResults).sort((a, b) => {
        return a.localeCompare(b, undefined, { numeric: true });
    });

    // Check if a record has only special entries (record-level only)
    const isRecordLevelOnly = (recordId) => {
        const items = groupedResults[recordId];
        return items.length === 1 && 
               (items[0].field_name === '[RECORD]' || 
                items[0].field_name.includes('[DUPLICATE') ||
                items[0].field_name === '[RECORD]' ||
                items[0].reason === 'record_only_in_a' ||
                items[0].reason === 'record_only_in_b');
    };

    // Check if a record has field-level disagreements
    const hasFieldDisagreements = (recordId) => {
        const items = groupedResults[recordId];
        return items.some(item => 
            item.field_name !== '[RECORD]' && 
            !item.field_name.includes('[DUPLICATE') &&
            item.reason !== 'record_only_in_a' &&
            item.reason !== 'record_only_in_b'
        );
    };

    return (
        <div className="table-container">
            <div className="table-wrapper">
                <table className="comparison-table">
                    <thead>
                        <tr>
                            <th style={{ width: '30px' }}></th>
                            <th>Record ID</th>
                            <th>Field</th>
                            <th>System A Value</th>
                            <th>System B Value</th>
                            <th>Reason</th>
                            <th>Location</th>
                        </tr>
                    </thead>
                    <tbody>
                        {sortedRecordIds.map((recordId) => {
                            const items = groupedResults[recordId];
                            const isExpanded = expandedRows[recordId];
                            const isRecordOnly = isRecordLevelOnly(recordId);
                            const hasFields = hasFieldDisagreements(recordId);
                            
                            // For record-only cases, show as single row
                            if (isRecordOnly) {
                                const item = items[0];
                                const bgColor = getReasonColor(item.reason);
                                return (
                                    <tr key={`${recordId}-single`} style={{ 
                                        background: bgColor ? `${bgColor}0d` : '#0d0d0d',
                                        borderBottom: '1px solid #1a1a1a'
                                    }}>
                                        <td></td>
                                        <td className="record-id">{item.record_id}</td>
                                        <td className="field-name">{item.field_name}</td>
                                        <td className={`value-cell ${!item.system_a_value ? 'empty' : ''}`}>
                                            {item.system_a_value || '—'}
                                        </td>
                                        <td className={`value-cell ${!item.system_b_value ? 'empty' : ''}`}>
                                            {item.system_b_value || '—'}
                                        </td>
                                        <td>
                                            <span className="reason-badge">
                                                <span className="reason-dot" style={{ background: bgColor }} />
                                                {getReasonLabel(item.reason)}
                                            </span>
                                        </td>
                                        <td className="location-cell">{item.location}</td>
                                    </tr>
                                );
                            }

                            // For records with field disagreements, show expandable rows
                            const firstItem = items[0];
                            const bgColor = getReasonColor(firstItem.reason);
                            
                            return (
                                <React.Fragment key={recordId}>
                                    {/* Summary row */}
                                    <tr 
                                        style={{ 
                                            background: bgColor ? `${bgColor}0d` : '#0d0d0d',
                                            borderBottom: '1px solid #1a1a1a',
                                            cursor: 'pointer'
                                        }}
                                        onClick={() => toggleRow(recordId)}
                                    >
                                        <td style={{ textAlign: 'center' }}>
                                            <span className="expand-icon">{isExpanded ? '▼' : '▶'}</span>
                                        </td>
                                        <td className="record-id">{recordId}</td>
                                        <td className="field-name" style={{ color: '#ffaa00' }}>
                                            {hasFields ? `${items.length - 1} field(s) differ` : 'No differences'}
                                        </td>
                                        <td className="value-cell" style={{ color: '#ff4444' }}>
                                            {items.filter(i => i.reason !== 'duplicate_in_b' && i.field_name !== '[RECORD]').length} disagreement(s)
                                        </td>
                                        <td className="value-cell" style={{ color: '#44bb88' }}>
                                            {items.filter(i => i.system_b_value && i.system_b_value !== '[MISSING]').length} value(s)
                                        </td>
                                        <td>
                                            <span className="reason-badge">
                                                <span className="reason-dot" style={{ background: bgColor }} />
                                                {getReasonLabel(firstItem.reason)}
                                            </span>
                                        </td>
                                        <td className="location-cell">{firstItem.location}</td>
                                    </tr>
                                    
                                    {/* Expanded rows - show ALL field disagreements */}
                                    {isExpanded && items.map((item, index) => {
                                        // Skip the summary item if it's a duplicate or record-level
                                        if (item.field_name === '[RECORD]' || 
                                            item.field_name.includes('[DUPLICATE') ||
                                            item.reason === 'record_only_in_a' ||
                                            item.reason === 'record_only_in_b') {
                                            return null;
                                        }
                                        
                                        const itemBgColor = getReasonColor(item.reason);
                                        return (
                                            <tr key={`${recordId}-${index}`} style={{
                                                background: itemBgColor ? `${itemBgColor}08` : '#0d0d0d',
                                                borderBottom: '1px solid #1a1a1a'
                                            }}>
                                                <td></td>
                                                <td></td>
                                                <td className="field-name" style={{ paddingLeft: '30px' }}>
                                                    {item.field_name}
                                                </td>
                                                <td className={`value-cell ${!item.system_a_value ? 'empty' : ''}`}>
                                                    {item.system_a_value || '—'}
                                                </td>
                                                <td className={`value-cell ${!item.system_b_value ? 'empty' : ''}`}>
                                                    {item.system_b_value || '—'}
                                                </td>
                                                <td>
                                                    <span className="reason-badge">
                                                        <span className="reason-dot" style={{ background: itemBgColor }} />
                                                        {getReasonLabel(item.reason)}
                                                    </span>
                                                </td>
                                                <td className="location-cell">{item.location}</td>
                                            </tr>
                                        );
                                    })}
                                </React.Fragment>
                            );
                        })}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

export default ComparisonTable;