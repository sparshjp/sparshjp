import React from 'react';
import { Briefcase } from 'lucide-react';

function Projects() {
  return (
    <div className="p-4 sm:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        <h1 className="heading-font text-4xl font-black tracking-tighter text-slate-900">Projects & Tasks</h1>
        <div className="bg-white border border-slate-200 rounded-sm p-12 text-center">
          <Briefcase className="mx-auto mb-4 text-slate-300" size={64} />
          <p className="text-slate-600">Projects module coming soon</p>
          <p className="text-sm text-slate-400 mt-2">Use AI: "Create task: Design homepage, assign to John"</p>
        </div>
      </div>
    </div>
  );
}

export default Projects;
