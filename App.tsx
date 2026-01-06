import React from 'react';

interface ErrorViewProps {
  error: string;
  onRetry: () => void;
  onReset: () => void;
}

export const ErrorView: React.FC<ErrorViewProps> = ({ error, onRetry, onReset }) => {
  return (
    <div className="flex flex-col items-center justify-center p-8 bg-gray-800 rounded-lg shadow-lg max-w-2xl mx-auto">
      <div className="text-red-400 mb-6">
        <svg className="w-16 h-16 mx-auto" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
        </svg>
      </div>
      
      <h2 className="text-2xl font-bold mb-4 text-center">Something went wrong</h2>
      
      <div className="bg-gray-700 p-4 rounded-lg mb-6 w-full">
        <p className="text-gray-300 whitespace-pre-wrap">{error}</p>
      </div>
      
      <div className="flex space-x-4">
        <button
          onClick={onReset}
          className="px-6 py-3 bg-gray-700 hover:bg-gray-600 text-white font-medium rounded-lg transition-colors duration-200"
        >
          Start Over
        </button>
        
        <button
          onClick={onRetry}
          className="px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white font-medium rounded-lg transition-colors duration-200"
        >
          Try Again
        </button>
      </div>
      
      <div className="mt-6 text-sm text-gray-400">
        <p>If the problem persists, try selecting fewer files or different image formats.</p>
      </div>
    </div>
  );
};