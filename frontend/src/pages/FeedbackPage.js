import { useState, useEffect } from 'react';
import { API } from '../App';

export default function FeedbackPage() {

  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    fetch(`${API}/feedback`).then(r => r.json()).then(d => { setData(Array.isArray(d) ? d : []); setLoading(false); }).catch(() => setLoading(false));
  }, []);
  return (
    <div className="p-6 space-y-6" data-testid="feedbackpage-page">
      <h1 className="text-2xl font-bold text-[#E8EDF2]">Client Feedback</h1>
      {loading ? <p className="text-[#4A5B6E]">Loading...</p> : <pre className="text-xs text-[#c8d4e0] bg-[#0D1B2A] p-4 rounded-lg border border-[#1B2D42] overflow-auto">{JSON.stringify(data, null, 2)}</pre>}
    </div>
  );
}
