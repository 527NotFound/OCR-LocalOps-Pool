import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css'; 

// 🎯 K8s Service NodePort 주소로 설정해야 합니다. 
// 예: http://<UTM_VM_IP>:<Router_NodePort>
const ROUTER_API_URL = "http://192.168.64.17:30001/ocr/process"; 
const STATUS_API_URL = "http://192.168.64.17:30001/status";

function App() {
  const [file, setFile] = useState(null);
  const [language, setLanguage] = useState('ENG');
  const [quality, setQuality] = useState('HIGH');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [workerStatus, setWorkerStatus] = useState({});

  // 1. 상태 모니터링: 라우터 상태 확인 (워커 상태는 라우터가 취합)
  const fetchStatus = async () => {
    try {
      const response = await axios.get(STATUS_API_URL);
      setWorkerStatus(response.data);
    } catch (error) {
      setWorkerStatus({ error: "라우터 API 연결 실패 또는 워커 오류" });
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 10000); // 10초마다 상태 업데이트
    return () => clearInterval(interval);
  }, []);

  // 2. OCR 요청 처리
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);
    formData.append('language', language);
    formData.append('quality', quality);

    setLoading(true);
    setResult(null);

    try {
      const response = await axios.post(ROUTER_API_URL, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setResult(response.data);
    } catch (error) {
      setResult({ error: "요청 실패", details: error.response?.data?.detail || error.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App-container">
      <h1>OCR LocalOps Pool CI/CD Tester 🚀</h1>
      
      {/* 상태 대시보드 */}
      <div className="status-panel">
        <h2>Worker Status: {workerStatus.status || '...Loading'}</h2>
        <p>Worker IDs: {workerStatus.workers_configured ? workerStatus.workers_configured.join(', ') : 'N/A'}</p>
        <p style={{color: workerStatus.error ? 'red' : 'green'}}>
          Health Check: {workerStatus.error ? workerStatus.error : 'All configured.'}
        </p>
      </div>

      <hr />

      {/* OCR 요청 폼 */}
      <form onSubmit={handleSubmit} className="ocr-form">
        <label>
          Image File:
          <input type="file" onChange={(e) => setFile(e.target.files[0])} required />
        </label>
        
        <label>
          Language:
          <select value={language} onChange={(e) => setLanguage(e.target.value)}>
            <option value="ENG">English (A/C)</option>
            <option value="KOR">Korean (B)</option>
            <option value="JPN">Japanese (B)</option>
          </select>
        </label>

        <label>
          Image Quality Hint:
          <select value={quality} onChange={(e) => setQuality(e.target.value)}>
            <option value="HIGH">High (Routes to A/B)</option>
            <option value="LOW">Low (Routes to C - Complex Pre-process)</option>
          </select>
        </label>

        <button type="submit" disabled={loading}>
          {loading ? 'Processing...' : 'Submit OCR Request'}
        </button>
      </form>
      
      {/* 결과 표시 */}
      {result && (
        <div className="result-panel">
          <h3>OCR Result (Routed by: {result.routed_by})</h3>
          {result.error ? (
            <pre style={{color: 'red'}}>Error: {JSON.stringify(result.details, null, 2)}</pre>
          ) : (
            <>
              <p>Worker ID: <strong>{result.worker_id}</strong></p>
              <pre>{result.detected_text}</pre>
            </>
          )}
        </div>
      )}
    </div>
  );
}

export default App;