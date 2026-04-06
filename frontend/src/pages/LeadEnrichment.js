import { useState, useEffect } from 'react';
import { API } from '../App';

export default function LeadEnrichment() {
  return (
    <div className="p-6 space-y-6" data-testid="lead-enrichment-page">
      <h1 className="text-2xl font-bold text-[#E8EDF2]">Enrich Lead Data</h1>
      <p className="text-[#4A5B6E]">Paste LinkedIn or Email text here to auto-fill lead details.</p>
    </div>
  );
}
