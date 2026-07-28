import React, { useState } from 'react';
import './UploadSection.css';

function UploadSection({ onUpload, loading }) {
    const [fileA, setFileA] = useState(null);
    const [fileB, setFileB] = useState(null);
    const [fileLocations, setFileLocations] = useState(null);

    const handleSubmit = (e) => {
        e.preventDefault();
        if (fileA && fileB) {
            onUpload(fileA, fileB, fileLocations);
        }
    };

    return (
        <div className="upload-section">
            <form onSubmit={handleSubmit}>
                <div className="upload-grid">
                    <div className="upload-group">
                        <label className="upload-label">
                            System A File
                            <span className="label-badge">Required</span>
                        </label>
                        <div className="upload-dropzone">
                            <input
                                type="file"
                                id="fileA"
                                onChange={(e) => setFileA(e.target.files[0])}
                                accept=".csv,.xlsx,.xls"
                                disabled={loading}
                                className="upload-input"
                            />
                            <label htmlFor="fileA" className="upload-area">
                                {!fileA ? (
                                    <>
                                        <span className="upload-icon">+</span>
                                        <span className="upload-text">Drop or click to upload</span>
                                        <span className="upload-hint">CSV or Excel files</span>
                                    </>
                                ) : (
                                    <div className="file-selected">
                                        <span className="file-icon">📄</span>
                                        <div className="file-display">
                                            <span className="file-name">{fileA.name}</span>
                                            <span className="file-size">{(fileA.size / 1024).toFixed(1)} KB</span>
                                        </div>
                                    </div>
                                )}
                            </label>
                        </div>
                    </div>

                    <div className="upload-group">
                        <label className="upload-label">
                            System B File
                            <span className="label-badge">Required</span>
                        </label>
                        <div className="upload-dropzone">
                            <input
                                type="file"
                                id="fileB"
                                onChange={(e) => setFileB(e.target.files[0])}
                                accept=".csv,.xlsx,.xls"
                                disabled={loading}
                                className="upload-input"
                            />
                            <label htmlFor="fileB" className="upload-area">
                                {!fileB ? (
                                    <>
                                        <span className="upload-icon">+</span>
                                        <span className="upload-text">Drop or click to upload</span>
                                        <span className="upload-hint">CSV or Excel files</span>
                                    </>
                                ) : (
                                    <div className="file-selected">
                                        <span className="file-icon">📄</span>
                                        <div className="file-display">
                                            <span className="file-name">{fileB.name}</span>
                                            <span className="file-size">{(fileB.size / 1024).toFixed(1)} KB</span>
                                        </div>
                                    </div>
                                )}
                            </label>
                        </div>
                    </div>

                    <div className="upload-group optional">
                        <label className="upload-label">
                            Locations File
                            <span className="label-badge optional">Optional</span>
                        </label>
                        <div className="upload-dropzone">
                            <input
                                type="file"
                                id="fileLocations"
                                onChange={(e) => setFileLocations(e.target.files[0])}
                                accept=".csv,.xlsx,.xls"
                                disabled={loading}
                                className="upload-input"
                            />
                            <label htmlFor="fileLocations" className="upload-area optional">
                                {!fileLocations ? (
                                    <>
                                        <span className="upload-icon">+</span>
                                        <span className="upload-text">Drop or click to upload</span>
                                        <span className="upload-hint">CSV or Excel files</span>
                                    </>
                                ) : (
                                    <div className="file-selected">
                                        <span className="file-icon">📄</span>
                                        <div className="file-display">
                                            <span className="file-name">{fileLocations.name}</span>
                                            <span className="file-size">{(fileLocations.size / 1024).toFixed(1)} KB</span>
                                        </div>
                                    </div>
                                )}
                            </label>
                        </div>
                    </div>
                </div>

                <button
                    type="submit"
                    disabled={!fileA || !fileB || loading}
                    className={`compare-btn ${loading ? 'loading' : ''}`}
                >
                    {loading ? (
                        <>
                            <span className="spinner"></span>
                            Comparing...
                        </>
                    ) : (
                        'Compare Records'
                    )}
                </button>
            </form>
        </div>
    );
}

export default UploadSection;