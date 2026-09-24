import React, { useEffect, useState } from 'react';
import axios from 'axios';

const API_URL = 'http://127.0.0.1:8001/api/dem/heatmap';

function App() {
  const [matrixData, setMatrixData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    axios.get(API_URL)
      .then((res) => {
        const rawData = res.data.heatmap_matrix || res.data.matrix || res.data;
        setMatrixData(rawData);
        setLoading(false);
      })
      .catch((err) => {
        console.error("API Error:", err);
        setError("Backend se matrix data load nahi ho saka.");
        setLoading(false);
      });
  }, []);
  let previewRows = [];
  if (matrixData && matrixData.length > 0) {
    const midRow = Math.floor(matrixData.length / 2);
    const midCol = Math.floor(matrixData[0].length / 2);
    
    previewRows = matrixData.slice(midRow, midRow + 10).map(row => row.slice(midCol, midCol + 10));
  }

  return (
    <div style={{ padding: '20px', backgroundColor: '#0d1117', color: '#fff', minHeight: '100vh', fontFamily: 'sans-serif' }}>
      <header style={{ borderBottom: '1px solid #30363d', paddingBottom: '15px', marginBottom: '20px' }}>
        <h2>NISAR Matrix Data Viewer</h2>
      
      </header>

      {loading && <h3>Data is Loading</h3>}

      {error && (
        <div style={{ color: '#ff5555', border: '1px solid #ff5555', padding: '15px', borderRadius: '5px' }}>
          <p>{error}</p>
        </div>
      )}

      {matrixData && !loading && (
        <div style={{ background: '#161b22', padding: '20px', borderRadius: '8px', border: '1px solid #30363d' }}>
          <div style={{ marginBottom: '15px' }}>
            <p style={{ color: '#3fb950', fontWeight: 'bold', fontSize: '16px', margin: 0 }}>
              Matrix Dimensions: {matrixData.length} Rows × {matrixData[0]?.length || 0} Columns
            </p>
            <p style={{ color: '#8b949e', fontSize: '13px', marginTop: '5px' }}>
              (Matrix ke beech (center) ka 10x10 sample preview jahan real terrain values milti hain)
            </p>
          </div>

          <div style={{ overflowX: 'auto', background: '#0d1117', padding: '10px', borderRadius: '6px', border: '1px solid #30363d' }}>
            <table style={{ borderCollapse: 'collapse', width: '100%', fontFamily: 'monospace', fontSize: '12px' }}>
              <tbody>
                {previewRows.map((row, rIdx) => (
                  <tr key={rIdx}>
                    {row.map((val, cIdx) => (
                      <td key={cIdx} style={{ border: '1px solid #30363d', padding: '8px', textAlign: 'center', color: '#58a6ff' }}>
                        {typeof val === 'number' ? val.toFixed(2) : val}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;