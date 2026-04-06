import React from 'react';

export function KairosIcon({ size = 20, className = '' }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 40 40"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      {/* White vertical bar */}
      <rect x="5" y="4" width="5" height="32" rx="2.5" fill="white" />
      {/* Upper teal diagonal stroke */}
      <line x1="14" y1="20" x2="27" y2="8" stroke="#00C9A7" strokeWidth="4.5" strokeLinecap="round" />
      {/* Lower teal diagonal stroke */}
      <line x1="14" y1="20" x2="27" y2="32" stroke="#00C9A7" strokeWidth="4.5" strokeLinecap="round" />
      {/* Teal dot */}
      <circle cx="33" cy="20" r="3.5" fill="#00C9A7" />
    </svg>
  );
}
