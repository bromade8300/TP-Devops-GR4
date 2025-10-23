import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [history, setHistory] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(false);

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      // Check if file is PNG or JPEG
      if (!file.type.match(/^image\/(png|jpeg|jpg)$/)) {
        setError('Please select a PNG or JPEG image file');
        return;
      }
      
      setSelectedFile(file);
      setError(null);
      setResult(null);
      
      // Create preview
      const reader = new FileReader();
      reader.onload = (e) => {
        setImagePreview(e.target.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const fetchHistory = async () => {
    setLoadingHistory(true);
    try {
      const response = await axios.get(`${process.env.REACT_APP_API_URL}/detections`);
      setHistory(response.data.detections || []);
    } catch (err) {
      console.error('Failed to fetch history:', err);
    } finally {
      setLoadingHistory(false);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please select a file first');
      return;
    }

    setUploading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await axios.post(`${process.env.REACT_APP_API_URL}/detect`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setResult(response.data);
      // Refresh history after successful upload
      fetchHistory();
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setResult(null);
    setError(null);
    setImagePreview(null);
  };

  // Load history on component mount
  useEffect(() => {
    fetchHistory();
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <h1>Image Detection App</h1>
        <p>Upload an image to detect objects using AI</p>
      </header>

      <main className="App-main">
        <div className="upload-section">
          <div className="file-input-container">
            <input
              type="file"
              accept="image/png,image/jpeg,image/jpg"
              onChange={handleFileSelect}
              className="file-input"
              id="file-input"
            />
            <label htmlFor="file-input" className="file-input-label">
              {selectedFile ? selectedFile.name : 'Choose Image File'}
            </label>
          </div>

          {imagePreview && (
            <div className="image-preview">
              <img src={imagePreview} alt="Preview" />
            </div>
          )}

          <div className="button-container">
            <button
              onClick={handleUpload}
              disabled={!selectedFile || uploading}
              className="upload-button"
            >
              {uploading ? 'Detecting...' : 'Detect Objects'}
            </button>
            
            <button
              onClick={handleReset}
              className="reset-button"
            >
              Reset
            </button>
          </div>

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          {result && (
            <div className="result-section">
              <h3>Detection Results</h3>
              <div className="result-image">
                <img src={`data:image/jpeg;base64,${result.annotated_image}`} alt="Detection Result" />
              </div>
              <div className="detection-info">
                <h4>Detected Objects:</h4>
                <ul>
                  {result.detections.map((detection, index) => (
                    <li key={index}>
                      <strong>{detection.class}</strong> - Confidence: {(detection.confidence * 100).toFixed(1)}%
                    </li>
                  ))}
                </ul>
                <p><strong>Total objects detected:</strong> {result.detections.length}</p>
              </div>
            </div>
          )}
        </div>

        {/* History Section */}
        <div className="history-section">
          <div className="history-header">
            <h3>Detection History</h3>
            <button 
              onClick={fetchHistory} 
              className="refresh-button"
              disabled={loadingHistory}
            >
              {loadingHistory ? 'Loading...' : 'Refresh'}
            </button>
          </div>
          
          {history.length === 0 ? (
            <div className="no-history">
              <p>No detection history available. Upload an image to get started!</p>
            </div>
          ) : (
            <div className="history-table-container">
              <table className="history-table">
                <thead>
                  <tr>
                    <th>Filename</th>
                    <th>Objects Detected</th>
                    <th>Count</th>
                    <th>Date</th>
                  </tr>
                </thead>
                <tbody>
                  {history.map((item) => (
                    <tr key={item.id}>
                      <td className="filename-cell">{item.filename}</td>
                      <td className="objects-cell">
                        {item.detections && item.detections.length > 0 ? (
                          <div className="objects-list">
                            {item.detections.slice(0, 3).map((detection, idx) => (
                              <span key={idx} className="object-tag">
                                {detection.class}
                              </span>
                            ))}
                            {item.detections.length > 3 && (
                              <span className="more-objects">+{item.detections.length - 3} more</span>
                            )}
                          </div>
                        ) : (
                          <span className="no-objects">No objects detected</span>
                        )}
                      </td>
                      <td className="count-cell">{item.total_objects}</td>
                      <td className="date-cell">
                        {new Date(item.timestamp).toLocaleString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
