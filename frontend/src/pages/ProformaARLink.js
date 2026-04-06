import { useState, useEffect } from 'react';
import { API } from '../App';

export default function ProformaARLink() {
  return (
    <div className="p-6 space-y-6" data-testid="proforma-ar-link-page">
      <h1 className="text-2xl font-bold text-[#E8EDF2]">Link Proforma to AR Credit Check</h1>
      <p className="text-[#4A5B6E]">Select a Proforma and link it to the AR Credit-Check system.</p>
    </div>
  );
}
