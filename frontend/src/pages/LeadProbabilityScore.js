import { useState, useEffect } from 'react';
import { API } from '../App';

export default function LeadProbabilityScore() {
  return (
    <div className="p-6 space-y-6" data-testid="lead-probability-score-page">
      <h1 className="text-2xl font-bold text-[#E8EDF2]">Lead Probability Score</h1>
      <p className="text-[#4A5B6E]">View and manage the probability score for leads.</p>
    </div>
  );
}
