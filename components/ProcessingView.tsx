import React from 'react';

interface ProcessingViewProps {
  statusMessage: string;
  totalFiles: number;
}

export const ProcessingView: React.FC<ProcessingViewProps> = ({ statusMessage, totalFiles }) => {
  return (
    <div className="flex-grow flex flex-col items-center justify-center text-center p-8 bg-gray-800 rounded-lg shadow-2xl border border-gray-700">
      <div className="animate-spin rounded-full h-32 w-32 border-t-4 border-b-4 border-cyan-500 mb-8"></div>
      <h2 className="text-3xl font-bold text-white mb-2">Processing Images...</h2>
      <p className="text-gray-400 max-w-xl text-lg">Please wait while we scan your folder. This might take a few moments for large collections.</p>
      <div className="mt-6 w-full max-w-2xl bg-gray-700 rounded-full h-4">
        {/* This is a visual-only indeterminate progress bar */}
        <div className="bg-cyan-500 h-4 rounded-full animate-pulse"></div>
      </div>
      <p className="mt-4 text-sm text-cyan-300 font-mono break-all px-4">{statusMessage}</p>
      <p className="mt-2 text-xs text-gray-500">Processing {totalFiles} files...</p>
    </div>
  );
};