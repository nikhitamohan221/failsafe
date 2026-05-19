import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { studentAPI, facultyAPI } from '../api/axios';
import { UploadCloud, CheckCircle2, AlertCircle, FileText, ArrowRight, Activity, ShieldCheck, AlertTriangle } from 'lucide-react';

const REQUIRED_COLUMNS = [
  'school', 'sex', 'age', 'address', 'famsize', 'Pstatus', 'Medu', 'Fedu', 
  'Mjob', 'Fjob', 'reason', 'guardian', 'traveltime', 'studytime', 'failures', 
  'schoolsup', 'famsup', 'paid', 'activities', 'nursery', 'higher', 'internet', 
  'romantic', 'famrel', 'freetime', 'goout', 'Dalc', 'Walc', 'health', 
  'absences', 'G1', 'G2', 'G3'
];

const UploadPage = () => {
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const droppedFile = e.dataTransfer.files[0];
      if (droppedFile.type === 'text/csv' || droppedFile.name.endsWith('.csv')) {
        setFile(droppedFile);
        setError(null);
      } else {
        setError('Please upload a valid CSV file.');
      }
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      const selectedFile = e.target.files[0];
      if (selectedFile.type === 'text/csv' || selectedFile.name.endsWith('.csv')) {
        setFile(selectedFile);
        setError(null);
      } else {
        setError('Please upload a valid CSV file.');
      }
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    
    setIsUploading(true);
    setError(null);
    
    try {
      // 1. Upload the CSV file
      const res = await studentAPI.uploadCSV(file);
      
      // The backend needs to actually return stats if it processes them.
      // Assuming the backend handles the processing and batch prediction after upload,
      // or we just run batch prediction right after successful upload.
      
      // Optional: Explicitly run batch predict if the backend doesn't automatically do it
      try {
        await facultyAPI.batchPredict();
      } catch (e) {
         console.log("Batch prediction might not be needed or failed.", e);
      }

      // Fetch the updated dashboard stats to show the result
      const dashboardRes = await facultyAPI.getDashboard();

      setUploadResult({
        message: res.message || 'File uploaded and processed successfully.',
        total_students: dashboardRes?.stats?.total_students || 0,
        high_risk: dashboardRes?.stats?.high_risk || 0,
        medium_risk: dashboardRes?.stats?.medium_risk || 0,
        low_risk: dashboardRes?.stats?.low_risk || 0,
      });

    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || 'Failed to upload and process the file.');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="container animate-fade-in">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1>Upload Student Data</h1>
          <p>Import a CSV file to batch predict student failure risks.</p>
        </div>
      </div>

      {!uploadResult ? (
        <div className="dashboard-grid" style={{ gridTemplateColumns: '2fr 1fr' }}>
          {/* Upload Area */}
          <div className="card">
            <h2 className="mb-4">Select CSV File</h2>
            
            <div 
              className={`flex flex-col items-center justify-center p-8 mb-6 transition-all`}
              style={{
                border: `2px dashed ${isDragging ? 'var(--primary)' : 'var(--border)'}`,
                borderRadius: '1rem',
                backgroundColor: isDragging ? 'var(--primary-light)' : 'rgba(0,0,0,0.2)',
                cursor: 'pointer',
                minHeight: '250px'
              }}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current.click()}
            >
              <input 
                type="file" 
                accept=".csv" 
                ref={fileInputRef} 
                style={{ display: 'none' }} 
                onChange={handleFileChange}
              />
              
              {!file ? (
                <>
                  <UploadCloud size={64} color={isDragging ? 'var(--primary)' : 'var(--text-muted)'} className="mb-4" />
                  <h3 className="mb-2" style={{ color: isDragging ? 'var(--primary)' : 'var(--text-main)' }}>
                    Drag & Drop your CSV here
                  </h3>
                  <p className="text-center" style={{ fontSize: '0.875rem' }}>or click to browse from your computer</p>
                </>
              ) : (
                <>
                  <FileText size={64} color="var(--primary)" className="mb-4" />
                  <h3 className="mb-2 text-center">{file.name}</h3>
                  <p className="text-center" style={{ fontSize: '0.875rem' }}>{(file.size / 1024).toFixed(2)} KB</p>
                  <button 
                    className="btn btn-secondary mt-4" 
                    onClick={(e) => { e.stopPropagation(); setFile(null); }}
                    style={{ padding: '0.25rem 0.75rem', fontSize: '0.75rem' }}
                  >
                    Remove File
                  </button>
                </>
              )}
            </div>

            {error && (
              <div className="flex items-center gap-2 mb-4 p-3" style={{ background: 'var(--risk-high-bg)', color: 'var(--risk-high)', borderRadius: '0.5rem', border: '1px solid var(--risk-high-border)' }}>
                <AlertCircle size={18} />
                <span style={{ fontSize: '0.875rem' }}>{error}</span>
              </div>
            )}

            <div className="flex justify-end">
              <button 
                className="btn" 
                onClick={handleUpload} 
                disabled={!file || isUploading}
                style={{ width: '100%' }}
              >
                {isUploading ? 'Uploading & Processing...' : 'Upload and Predict'}
              </button>
            </div>
          </div>

          {/* Guidelines */}
          <div className="card">
            <h3 className="flex items-center gap-2 mb-4 text-main">
              <Info size={18} color="var(--primary)" /> Format Guidelines
            </h3>
            <p style={{ fontSize: '0.875rem', marginBottom: '1rem' }}>
              Your CSV file must include headers matching our ML model's expected features.
            </p>
            
            <div style={{ background: 'rgba(0,0,0,0.2)', padding: '1rem', borderRadius: '0.5rem', border: '1px solid var(--border)' }}>
              <h4 className="mb-2" style={{ fontSize: '0.875rem', color: 'var(--text-main)' }}>Required Columns:</h4>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                {REQUIRED_COLUMNS.map(col => (
                  <span key={col} style={{ 
                    fontSize: '0.75rem', 
                    background: 'rgba(255,255,255,0.05)', 
                    padding: '0.15rem 0.4rem', 
                    borderRadius: '0.25rem',
                    color: 'var(--text-muted)'
                  }}>
                    {col}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      ) : (
        /* Success State */
        <div className="card flex flex-col items-center justify-center p-8" style={{ minHeight: '400px' }}>
          <div style={{ background: 'var(--risk-low-bg)', padding: '1.5rem', borderRadius: '50%', marginBottom: '1.5rem' }}>
            <CheckCircle2 size={64} color="var(--risk-low)" />
          </div>
          
          <h2 className="mb-2">Upload Successful!</h2>
          <p className="mb-8 text-center" style={{ maxWidth: '400px' }}>
            {uploadResult.message} The ML model has evaluated the batch. Here are the current department statistics:
          </p>

          <div className="flex gap-4 mb-8 flex-wrap justify-center">
            <div style={{ background: 'rgba(0,0,0,0.2)', padding: '1rem', borderRadius: '0.75rem', border: '1px solid var(--border)', width: '140px', textAlign: 'center' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Total Processed</div>
              <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-main)' }}>{uploadResult.total_students}</div>
            </div>
            
            <div style={{ background: 'var(--risk-high-bg)', padding: '1rem', borderRadius: '0.75rem', border: '1px solid var(--risk-high-border)', width: '140px', textAlign: 'center' }}>
              <div className="flex items-center justify-center gap-1 mb-1" style={{ color: 'var(--risk-high)' }}>
                <AlertTriangle size={14} />
                <span style={{ fontSize: '0.75rem', textTransform: 'uppercase' }}>High Risk</span>
              </div>
              <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--risk-high)' }}>{uploadResult.high_risk}</div>
            </div>

            <div style={{ background: 'var(--risk-medium-bg)', padding: '1rem', borderRadius: '0.75rem', border: '1px solid var(--risk-medium-border)', width: '140px', textAlign: 'center' }}>
               <div className="flex items-center justify-center gap-1 mb-1" style={{ color: 'var(--risk-medium)' }}>
                <Activity size={14} />
                <span style={{ fontSize: '0.75rem', textTransform: 'uppercase' }}>Medium Risk</span>
              </div>
              <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--risk-medium)' }}>{uploadResult.medium_risk}</div>
            </div>

            <div style={{ background: 'var(--risk-low-bg)', padding: '1rem', borderRadius: '0.75rem', border: '1px solid var(--risk-low-border)', width: '140px', textAlign: 'center' }}>
               <div className="flex items-center justify-center gap-1 mb-1" style={{ color: 'var(--risk-low)' }}>
                <ShieldCheck size={14} />
                <span style={{ fontSize: '0.75rem', textTransform: 'uppercase' }}>Low Risk</span>
              </div>
              <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--risk-low)' }}>{uploadResult.low_risk}</div>
            </div>
          </div>

          <button className="btn" onClick={() => navigate('/faculty')}>
            Go to Faculty Dashboard <ArrowRight size={18} />
          </button>
        </div>
      )}
    </div>
  );
};

export default UploadPage;

