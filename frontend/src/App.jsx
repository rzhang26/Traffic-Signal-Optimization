import React, { useState } from 'react';

export default function App() {
  const [county, setCounty] = useState('');
  const [month, setMonth] = useState('');
  const [result, setResult] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    const res = await fetch(`http://localhost:8000/api/trends?county=${county}&month=${month}`);
    const data = await res.json();
    setResult(data.message);
  }

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-4">
        Traffic Trends Checker
      </h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          type="text"
          placeholder="County (e.g., Queens)"
          value={county}
          onChange={(e) => setCounty(e.target.value)}
          className="border p-2 rounded w-full"
        />
        <input
          type="month"
          value={month}
          onChange={(e) => setMonth(e.target.value)}
          className="border p-2 rounded w-full"
        />
        <button
          type="submit"
          className="bg-blue-500 text-white px-4 py-2 rounded"
        >
          Check Trends
        </button>
      </form>
      {result && (
        <div className="mt-4 p-4 bg-gray-100 rounded">
          <strong>Response:</strong> {result}
        </div>
      )}
    </div>
  );
}