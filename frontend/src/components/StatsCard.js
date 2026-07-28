import React from 'react';
import './StatsCard.css';

function StatsCard({ stats, summary }) {
    const reasonColors = {
        'Missing in System A': '#ff4444',
        'Missing in System B': '#ff4444',
        'Missing in Both': '#ff4444',
        'Numeric Difference': '#ffaa00',
        'Rounding Difference': '#ffaa00',
        'Case Difference': '#44bb88',
        'Whitespace Difference': '#44bb88',
        'Value Mismatch': '#ff8800',
        'Record Only in A': '#8888ff',
        'Record Only in B': '#8888ff',
        'Duplicate in B': '#ff66aa',
        'Date Difference': '#ff66aa'
    };

    const sortedSummary = Object.entries(summary).sort((a, b) => b[1] - a[1]);

    return (
        <div className="stats-card">
            <div className="stats-header">
                <h3 className="stats-title">Comparison Summary</h3>
            </div>

            <div className="stats-grid">
                <div className="stat-item">
                    <div className="stat-icon">A</div>
                    <div className="stat-content">
                        <div className="stat-value">{stats.total_records_a}</div>
                        <div className="stat-label">System A Records</div>
                    </div>
                </div>

                <div className="stat-item">
                    <div className="stat-icon">B</div>
                    <div className="stat-content">
                        <div className="stat-value">{stats.total_records_b}</div>
                        <div className="stat-label">System B Records</div>
                    </div>
                </div>

                <div className="stat-item">
                    <div className="stat-icon">C</div>
                    <div className="stat-content">
                        <div className="stat-value">{stats.common_records}</div>
                        <div className="stat-label">Common Records</div>
                    </div>
                </div>

                <div className="stat-item matched">
                    <div className="stat-icon">✓</div>
                    <div className="stat-content">
                        <div className="stat-value" style={{ color: '#44bb88' }}>
                            {stats.records_matched}
                        </div>
                        <div className="stat-label">Records Matched</div>
                        <div className="stat-hint">No differences found</div>
                    </div>
                </div>

                <div className="stat-item with-issues">
                    <div className="stat-icon">!</div>
                    <div className="stat-content">
                        <div className="stat-value" style={{ color: '#ffaa00' }}>
                            {stats.records_with_issues}
                        </div>
                        <div className="stat-label">Records with Issues</div>
                        <div className="stat-hint">Have at least one disagreement</div>
                    </div>
                </div>

                <div className="stat-item disagreements">
                    <div className="stat-icon">#</div>
                    <div className="stat-content">
                        <div className="stat-value" style={{ color: '#ff4444' }}>
                            {stats.field_disagreements}
                        </div>
                        <div className="stat-label">Field Disagreements</div>
                        <div className="stat-hint">Total individual field differences</div>
                    </div>
                </div>
            </div>

            {sortedSummary.length > 0 && (
                <div className="stats-breakdown">
                    <div className="breakdown-title">Disagreement Breakdown</div>
                    <div className="breakdown-grid">
                        {sortedSummary.map(([reason, count]) => (
                            <div key={reason} className="breakdown-item">
                                <span 
                                    className="breakdown-dot" 
                                    style={{ background: reasonColors[reason] || '#555' }}
                                />
                                <span className="breakdown-label">{reason}</span>
                                <span className="breakdown-count">{count}</span>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            <div className="stats-footnote">
                <small>
                    Records Matched = Common records with no differences.<br/>
                    Records with Issues = Common records with at least one field difference.<br/>
                    Field Disagreements = Total individual field-level differences.
                </small>
            </div>
        </div>
    );
}

export default StatsCard;