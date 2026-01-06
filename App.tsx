import React, { useState, useCallback, useEffect } from 'react';
import { useWorkerManager } from './src/hooks/useWorkerManager';
import electronLogger from './src/services/electronLogger';

// Import the CSS file for dynamic progress styles
import './src/styles/progress.css';

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

const App: React.FC = () => {
  const [selectedFolder, setSelectedFolder] = useState<string | null>(null);
  const [isScanning, setIsScanning] = useState(false);
  const { duplicateGroups, processingErrors, statusMessage, processState } = useWorkerManager();

  const handleFolderSelect = useCallback(async () => {
    try {
      setIsScanning(true);
      
      // Log the action
      electronLogger.info('Folder selection initiated');
      
      // Check if we're in an Electron environment
      if (typeof window !== 'undefined' && window.electron) {
        const result = await window.electron.selectFolder();
        if (result.success && result.path) {
          setSelectedFolder(result.path);
          electronLogger.info(`Selected folder: ${result.path}`);
          // Process the selected folder in a real implementation
        }
      } else {
        // Fallback for web development
        const folderPath = prompt("Enter folder path to scan:");
        if (folderPath) {
          setSelectedFolder(folderPath);
          electronLogger.info(`Selected folder: ${folderPath} (web fallback)`);
        }
      }
    } catch (error) {
      electronLogger.error(`Error selecting folder: ${error instanceof Error ? error.message : String(error)}`);
      console.error('Error selecting folder:', error);
    } finally {
      setIsScanning(false);
    }
  }, []);

  // Calculate progress based on processState
  const progress = processState === 'idle' ? 0 : processState === 'done' ? 100 : 50;

  // Log when the app mounts
  useEffect(() => {
    electronLogger.info('Duplicate File Finder App mounted');
  }, []);

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <div className="max-w-6xl mx-auto">
        <header className="mb-12 text-center">
          <h1 className="text-4xl font-bold mb-4">Duplicate File Finder</h1>
          <p className="text-gray-400 max-w-2xl mx-auto">
            Find and manage duplicate files in your folders using fast hashing technology
          </p>
        </header>

        <div className="bg-gray-800 rounded-xl p-8 mb-8">
          <div className="flex flex-col items-center">
            <button
              onClick={handleFolderSelect}
              disabled={isScanning}
              className={`px-8 py-4 rounded-lg font-medium text-lg transition-colors duration-200 ${
                isScanning 
                  ? 'bg-gray-700 cursor-not-allowed' 
                  : 'bg-blue-600 hover:bg-blue-500'
              }`}
            >
              {isScanning ? 'Scanning...' : 'Select Folder to Scan'}
            </button>
            
            {selectedFolder && (
              <div className="mt-4 text-gray-400">
                Selected: {selectedFolder}
              </div>
            )}
          </div>
        </div>

        {(processState === 'processing' || statusMessage) && (
          <div className="mb-8 bg-gray-800 rounded-xl p-6">
            <div className="flex justify-between mb-2">
              <span className="font-medium">Scanning Progress</span>
              <span>{processState === 'processing' ? '50%' : statusMessage ? 'Complete' : '0%'}</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-3 overflow-hidden">
              <div 
                className={`h-full bg-blue-600 rounded-full transition-all duration-300 progress-${progress}`}
              ></div>
            </div>
            {statusMessage && (
              <div className="mt-2 text-sm text-gray-400">{statusMessage}</div>
            )}
          </div>
        )}

        {duplicateGroups.length > 0 && (
          <div className="bg-gray-800 rounded-xl p-6 mb-8">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold">Duplicate Groups Found</h2>
              <span className="bg-red-600 text-white px-3 py-1 rounded-full text-sm">
                {duplicateGroups.length} groups
              </span>
            </div>
            
            <div className="space-y-6">
              {duplicateGroups.map((group, index) => (
                <div key={group.id || index} className="bg-gray-700 p-4 rounded-lg">
                  <h3 className="font-medium mb-3">Group {index + 1} ({group.files.length} files)</h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {group.files.map((file, fileIndex) => (
                      <div key={fileIndex} className="bg-gray-600 rounded p-2">
                        <div className="text-sm truncate mb-1">{file.name || file.path.split('/').pop()}</div>
                        <div className="text-xs text-gray-400 mb-2">{file.size} bytes</div>
                        <img 
                          src={file.path} 
                          alt={`Preview ${fileIndex}`} 
                          className="w-full h-24 object-contain rounded border border-gray-500"
                          onError={(e) => {
                            const target = e.target as HTMLImageElement;
                            target.src = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 24 24"><path fill="gray" d="M19 5v14H5V5h14m0-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2z"/><path fill="gray" d="M14.14 11.86l-3 3.87L9 13.14 7 17h10l-3.86-5.14z"/></svg>';
                          }}
                        />
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {processingErrors.length > 0 && (
          <div className="bg-gray-800 rounded-xl p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-2xl font-bold">Errors</h2>
              <span className="bg-red-600 text-white px-3 py-1 rounded-full text-sm">
                {processingErrors.length} errors
              </span>
            </div>
            <div className="space-y-3 max-h-60 overflow-y-auto">
              {processingErrors.map((error, index) => (
                <div key={index} className="bg-red-900/30 p-3 rounded text-sm text-red-200">
                  {error.path}: {error.error}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default App;