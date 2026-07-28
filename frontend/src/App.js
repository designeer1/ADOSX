import React, { useState, useEffect } from 'react';
import UploadSection from './components/UploadSection';
import FilterBar from './components/FilterBar';
import ComparisonTable from './components/ComparisonTable';
import StatsCard from './components/StatsCard';
import axios from 'axios';
import './App.css';

function App() {
    const [results, setResults] = useState([]);
    const [filteredResults, setFilteredResults] = useState([]);
    const [reasons, setReasons] = useState([]);
    const [selectedReason, setSelectedReason] = useState('');
    const [loading, setLoading] = useState(false);
    const [summary, setSummary] = useState({});
    const [error, setError] = useState(null);
    const [columns, setColumns] = useState({ a: [], b: [] });
    const [hasData, setHasData] = useState(false);
    const [uploadKey, setUploadKey] = useState(0); // Force re-render on upload
    const [stats, setStats] = useState({
        total_records_a: 0,
        total_records_b: 0,
        common_records: 0,
        records_matched: 0,
        records_with_issues: 0,
        field_disagreements: 0
    });

    const API_URL = 'http://localhost:8000/api';

    // Clear any existing data on page load
    useEffect(() => {
        const clearExistingData = async () => {
            try {
                // Clear data on backend
                await axios.post(`${API_URL}/clear/`);
                setResults([]);
                setFilteredResults([]);
                setHasData(false);
                setReasons([]);
                console.log('Data cleared on startup');
            } catch (err) {
                console.log('No existing data to clear');
            }
        };
        clearExistingData();
    }, []);

    const fetchReasons = async () => {
        try {
            const response = await axios.get(`${API_URL}/reasons/`);
            setReasons(response.data);
        } catch (err) {
            console.error('Failed to fetch reasons:', err);
        }
    };

    const handleUpload = async (fileA, fileB, fileLocations) => {
        setLoading(true);
        setError(null);
        setHasData(false);
        
        const formData = new FormData();
        formData.append('file_a', fileA);
        formData.append('file_b', fileB);
        if (fileLocations) {
            formData.append('file_locations', fileLocations);
        }

        try {
            const response = await axios.post(`${API_URL}/compare/`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            
            // Force re-render by incrementing key
            setUploadKey(prev => prev + 1);
            
            // Set fresh data
            setResults(response.data.results);
            setFilteredResults(response.data.results);
            setSummary(response.data.summary);
            setColumns({
                a: response.data.columns_a || [],
                b: response.data.columns_b || []
            });
            setStats({
                total_records_a: response.data.total_records_a,
                total_records_b: response.data.total_records_b,
                common_records: response.data.common_records,
                records_matched: response.data.records_matched,
                records_with_issues: response.data.records_with_issues,
                field_disagreements: response.data.field_disagreements
            });
            setSelectedReason('');
            setHasData(true);
            
            // Fetch reasons for the filter
            await fetchReasons();
            
            console.log('Upload complete. Stats:', response.data);
            
        } catch (err) {
            setError(err.response?.data?.error || 'Upload failed: ' + err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleFilterChange = (reason) => {
        setSelectedReason(reason);
        if (reason) {
            setFilteredResults(results.filter(r => r.reason === reason));
        } else {
            setFilteredResults(results);
        }
    };

    return (
        <div className="app" key={uploadKey}>
            <header className="app-header">
                <div className="logo">
                    <svg width="32" height="32" viewBox="0 0 40 40" fill="none">
                        <rect x="4" y="4" width="32" height="32" rx="6" fill="#333" opacity="0.3"/>
                        <path d="M12 12L28 28M12 28L28 12" stroke="#888" strokeWidth="3"/>
                        <circle cx="20" cy="20" r="4" fill="#fff"/>
                    </svg>
                    <h1>Record Comparator</h1>
                </div>
                <p className="subtitle">Upload files to compare records across systems</p>
            </header>

            <main>
                {error && (
                    <div className="error-banner">
                        <span>⚠</span>
                        {error}
                        <button className="error-close" onClick={() => setError(null)}>×</button>
                    </div>
                )}

                <UploadSection onUpload={handleUpload} loading={loading} />

                {hasData && stats.common_records > 0 && (
                    <>
                        <div style={{ 
                            background: '#111111', 
                            padding: '12px 16px', 
                            borderRadius: '8px',
                            marginBottom: '16px',
                            border: '1px solid #222',
                            display: 'flex',
                            flexWrap: 'wrap',
                            gap: '20px',
                            fontSize: '12px',
                            color: '#888'
                        }}>
                            <div>
                                <strong style={{ color: '#e0e0e0' }}>System A Columns:</strong>{' '}
                                {columns.a.map((col, i) => (
                                    <span key={i} style={{ 
                                        background: '#1a1a1a', 
                                        padding: '2px 8px', 
                                        borderRadius: '4px',
                                        margin: '2px 4px',
                                        display: 'inline-block',
                                        color: '#ccc'
                                    }}>
                                        {col}
                                    </span>
                                ))}
                            </div>
                            <div>
                                <strong style={{ color: '#e0e0e0' }}>System B Columns:</strong>{' '}
                                {columns.b.map((col, i) => (
                                    <span key={i} style={{ 
                                        background: '#1a1a1a', 
                                        padding: '2px 8px', 
                                        borderRadius: '4px',
                                        margin: '2px 4px',
                                        display: 'inline-block',
                                        color: '#ccc'
                                    }}>
                                        {col}
                                    </span>
                                ))}
                            </div>
                        </div>

                        <StatsCard stats={stats} summary={summary} />
                    </>
                )}

                {hasData && results.length > 0 && (
                    <>
                        <FilterBar 
                            reasons={reasons}
                            selectedReason={selectedReason}
                            onFilterChange={handleFilterChange}
                            totalDisagreements={results.length}
                        />
                        <ComparisonTable results={filteredResults} loading={loading} />
                        <div className="table-footer">
                            Showing {filteredResults.length} of {results.length} disagreements
                        </div>
                    </>
                )}

                {hasData && results.length === 0 && !loading && stats.common_records > 0 && (
                    <div className="empty-state success">
                        <h2>All records matched</h2>
                        <p>{stats.records_matched} out of {stats.common_records} records are identical across both systems.</p>
                    </div>
                )}

                {!hasData && !loading && (
                    <div className="empty-state">
                        <div style={{ fontSize: '48px', marginBottom: '16px' }}>📂</div>
                        <h2>No data loaded</h2>
                        <p>Upload System A and System B files above to start comparing records.</p>
                    </div>
                )}
            </main>

            <footer className="app-footer">
                <p>Built with Django + React</p>
            </footer>
        </div>
    );
}

export default App;