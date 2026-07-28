import React from 'react';
import './FilterBar.css';

function FilterBar({ reasons, selectedReason, onFilterChange, totalDisagreements }) {
    const reasonColors = {
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
        'duplicate_in_b': '#ff66aa'
    };

    const groupedReasons = {
        'Missing Data': ['missing_in_a', 'missing_in_b', 'both_missing'],
        'Numeric': ['numeric_difference', 'rounding_difference'],
        'Text': ['case_difference', 'whitespace_difference', 'value_mismatch'],
        'Record': ['record_only_in_a', 'record_only_in_b', 'duplicate_in_b']
    };

    const getGroupColor = (group) => {
        const colors = {
            'Missing Data': '#ff4444',
            'Numeric': '#ffaa00',
            'Text': '#44bb88',
            'Record': '#8888ff'
        };
        return colors[group] || '#555';
    };

    const formatReason = (reason) => {
        const mapping = {
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
            'duplicate_in_b': 'Duplicate in B'
        };
        return mapping[reason] || reason;
    };

    return (
        <div className="filter-bar">
            <div className="filter-header">
                <span className="filter-title">Filter by reason</span>
            </div>
            
            <div className="filter-groups">
                <button
                    className={`filter-btn all ${selectedReason === '' ? 'active' : ''}`}
                    onClick={() => onFilterChange('')}
                >
                    All ({totalDisagreements})
                </button>
                
                {Object.entries(groupedReasons).map(([group, reasonsList]) => {
                    const groupCount = reasonsList.reduce((sum, r) => {
                        const reasonObj = reasons.find(rev => rev.reason === r);
                        return sum + (reasonObj ? reasonObj.count : 0);
                    }, 0);
                    
                    if (groupCount === 0) return null;
                    
                    return (
                        <button
                            key={group}
                            className="filter-btn group"
                            onClick={() => {
                                const firstReason = reasonsList.find(r => 
                                    reasons.some(rev => rev.reason === r)
                                );
                                if (firstReason) onFilterChange(firstReason);
                            }}
                        >
                            <span className="group-dot" style={{ background: getGroupColor(group) }} />
                            {group} ({groupCount})
                        </button>
                    );
                })}
            </div>
            
            {selectedReason && (
                <div className="filter-selected">
                    <span className="selected-label">Selected:</span>
                    {reasons.map((r) => {
                        const isSelected = selectedReason === r.reason;
                        return (
                            <button
                                key={r.reason}
                                className={`reason-chip ${isSelected ? 'selected' : ''}`}
                                onClick={() => onFilterChange(isSelected ? '' : r.reason)}
                            >
                                <span 
                                    className="chip-dot"
                                    style={{ background: reasonColors[r.reason] || '#555' }}
                                />
                                {formatReason(r.reason)} ({r.count})
                            </button>
                        );
                    })}
                    <button className="clear-btn" onClick={() => onFilterChange('')}>Clear</button>
                </div>
            )}
        </div>
    );
}

export default FilterBar;