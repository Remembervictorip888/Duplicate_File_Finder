import React, { useState, useMemo, useCallback, useEffect } from 'react';
import type { Stats, ImageFile, ProcessedFile, FileProcessingError } from '../types';
// FIX: Remove unused and non-existent InformationCircleIcon import.
import { CheckCircleIcon, TrashIcon, XCircleIcon, DuplicateIcon, ResetIcon } from './icons';

const formatBytes = (bytes: number, decimals = 2): string => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
};

// Memoized ImageCard component to prevent unnecessary re-renders
const ImageCard: React.FC<{ image: ImageFile; isSelected: boolean; onToggleSelect: (path: string) => void; isKept: boolean; }> = React.memo(({ image, isSelected, onToggleSelect, isKept }) => {
  const [previewUrl, setPreviewUrl] = React.useState(image.previewUrl);

  // Create preview URL if not provided
  useEffect(() => {
    if (!image.previewUrl && image.file) {
      const url = URL.createObjectURL(image.file);
      setPreviewUrl(url);

      // Cleanup
      return () => {
        URL.revokeObjectURL(url);
      };
    }
  }, [image]);

  return (
    <div className={`relative border-2 rounded-lg overflow-hidden transition-all duration-200 ${isSelected ? 'border-red-500 scale-105 shadow-lg' : 'border-gray-700'} ${isKept ? 'opacity-50' : ''}`}>
      <img src={previewUrl || image.previewUrl} alt={image.path} className="w-full h-48 object-cover" loading="lazy" />
      <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent"></div>
      <div className="absolute bottom-0 left-0 p-2 w-full">
        <p className="text-xs text-white font-mono truncate" title={image.path}>{image.path}</p>
      </div>
      {!isKept && (
        <button onClick={() => onToggleSelect(image.path)} className="absolute top-2 right-2 w-6 h-6 rounded-full flex items-center justify-center bg-black/50 hover:bg-black/75 transition-colors" aria-label={isSelected ? "Deselect image" : "Select image"}>
          {isSelected ? <XCircleIcon className="w-5 h-5 text-red-400" aria-hidden="true"/> : <CheckCircleIcon className="w-5 h-5 text-gray-400 hover:text-green-400" aria-hidden="true"/>}
        </button>
      )}
      {isKept && (
        <div className="absolute top-2 right-2 px-2 py-1 text-xs bg-cyan-600 text-white rounded-md font-bold">KEEP</div>
      )}
    </div>
  );
});

const DeletionModal: React.FC<{ filesToDelete: string[]; onClose: () => void }> = ({ filesToDelete, onClose }) => {
    const [copied, setCopied] = useState(false);
    const textToCopy = filesToDelete.map(f => `"${f}"`).join(' ');

    const handleCopy = () => {
        navigator.clipboard.writeText(textToCopy).then(() => {
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        });
    };

    return (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50">
            <div className="bg-gray-800 rounded-lg shadow-2xl max-w-2xl w-full p-6 border border-gray-700">
                <div className="flex justify-between items-center mb-4">
                    <h2 className="text-2xl font-bold text-red-400 flex items-center gap-2"><TrashIcon className="w-6 h-6"/>Deletion Instructions</h2>
                    <button onClick={onClose} className="text-gray-400 hover:text-white" aria-label="Close modal"><XCircleIcon className="w-6 h-6" aria-hidden="true" /></button>
                </div>
                <div className="bg-yellow-900/50 border border-yellow-700 text-yellow-300 p-4 rounded-md mb-4 text-sm">
                    <p className="font-bold mb-1">Security Warning: This App Cannot Delete Files</p>
                    <p>For security reasons, web applications cannot delete files from your computer. You must delete the selected files manually.</p>
                </div>
                <p className="text-gray-300 mb-4">Below is a list of file paths you selected for deletion. You can copy this list and use a command-line tool to delete them.</p>
                <div className="bg-gray-900 p-3 rounded-md h-48 overflow-y-auto font-mono text-sm text-gray-400 border border-gray-700">
                    {filesToDelete.join('\n')}
                </div>
                <div className="mt-4 flex gap-4">
                    <button onClick={handleCopy} className="bg-cyan-500 hover:bg-cyan-600 text-white font-bold py-2 px-4 rounded-md w-full" aria-label="Copy file paths to clipboard">
                        {copied ? 'Copied to Clipboard!' : 'Copy Command-Line Paths'}
                    </button>
                </div>
                <p className="text-xs text-gray-500 mt-2">Example command: <code className="bg-gray-900 p-1 rounded">xargs rm &lt; pasted_paths</code></p>
            </div>
        </div>
    );
};

// Define a type for the group data returned by the worker
interface WorkerDuplicateGroup {
  id: string;
  hash: string;
  files: ProcessedFile[];
  size: number;
}

export const ResultsView: React.FC<{ 
  groups: WorkerDuplicateGroup[], 
  stats: Stats, 
  onReset: () => void, 
  originalFiles?: File[],
  processingErrors?: FileProcessingError[]
}> = ({ groups, stats, onReset, originalFiles = [], processingErrors = [] }) => {
  const [selectedFiles, setSelectedFiles] = useState<Set<string>>(new Set());
  const [showModal, setShowModal] = useState(false);
  const [showErrors, setShowErrors] = useState(false);
  // Pagination state
  const [currentPage, setCurrentPage] = useState(0);
  const [itemsPerPage, setItemsPerPage] = useState(10); // Default to 10 groups per page

  // Map to store original files by path
  const fileMap = useMemo(() => {
    const map = new Map<string, File>();
    originalFiles.forEach(file => {
      const path = (file as any).webkitRelativePath || file.name;
      map.set(path, file);
    });
    return map;
  }, [originalFiles]);

  // Convert processed group data back to ImageFile format
  const imageGroups = useMemo(() => {
    return groups.map(group => ({
      ...group,
      files: group.files.map(fileData => {
        const originalFile = fileMap.get(fileData.path);
        return {
          file: originalFile || new File([], fileData.name, { type: fileData.type, lastModified: Date.now() }),
          previewUrl: '',
          path: fileData.path
        } as ImageFile;
      })
    }));
  }, [groups, fileMap]);

  // Pagination calculations
  const totalPages = Math.ceil(imageGroups.length / itemsPerPage);
  const startIndex = currentPage * itemsPerPage;
  const endIndex = Math.min(startIndex + itemsPerPage, imageGroups.length);
  const currentGroups = imageGroups.slice(startIndex, endIndex);

  // Handle page changes
  const goToNextPage = () => {
    if (currentPage < totalPages - 1) {
      setCurrentPage(prev => prev + 1);
    }
  };

  const goToPrevPage = () => {
    if (currentPage > 0) {
      setCurrentPage(prev => prev - 1);
    }
  };

  const goToPage = (page: number) => {
    setCurrentPage(Math.max(0, Math.min(page, totalPages - 1)));
  };

  // Handle items per page changes
  const handleItemsPerPageChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newItemsPerPage = parseInt(e.target.value, 10);
    setItemsPerPage(newItemsPerPage);
    // Reset to first page when changing items per page
    setCurrentPage(0);
  };

  const handleToggleSelect = useCallback((path: string) => {
    setSelectedFiles(prev => {
      const newSet = new Set(prev);
      if (newSet.has(path)) {
        newSet.delete(path);
      } else {
        newSet.add(path);
      }
      return newSet;
    });
  }, []);

  const selectAllButOneInGroups = useCallback(() => {
    const newSelections = new Set<string>();
    imageGroups.forEach(group => {
        group.files.slice(1).forEach(file => newSelections.add(file.path));
    });
    setSelectedFiles(newSelections);
  }, [imageGroups]);

  const filesToDelete = useMemo(() => Array.from(selectedFiles), [selectedFiles]);
  const deletionSize = useMemo(() => {
    let size = 0;
    const selectedPaths = Array.from(selectedFiles);
    for (const group of imageGroups) {
      for (const file of group.files) {
        if (selectedPaths.includes(file.path)) {
          size += file.file.size;
        }
      }
    }
    return size;
  }, [selectedFiles, imageGroups]);

  if (imageGroups.length === 0 && processingErrors.length === 0) {
    return (
      <div className="flex-grow flex flex-col items-center justify-center text-center p-8 bg-gray-800 rounded-lg shadow-2xl border border-gray-700">
        <CheckCircleIcon className="w-24 h-24 text-green-500 mb-6" aria-hidden="true" />
        <h2 className="text-3xl font-bold text-white mb-2">All Clean!</h2>
        <p className="text-gray-400 max-w-md mb-8">
          We scanned your folder and found no duplicate images. Your collection is perfectly organized!
        </p>
        <button
          onClick={onReset}
          className="bg-cyan-500 hover:bg-cyan-600 text-white font-bold py-3 px-8 rounded-lg text-lg transition-all duration-300 ease-in-out transform hover:scale-105 shadow-lg flex items-center gap-3"
          aria-label="Scan another folder for duplicates"
        >
          <ResetIcon className="w-6 h-6" aria-hidden="true"/>
          Scan Another Folder
        </button>
      </div>
    );
  }

  return (
    <div className="w-full">
      {showModal && <DeletionModal filesToDelete={filesToDelete} onClose={() => setShowModal(false)} />}
      <div className="bg-gray-800 p-4 rounded-lg shadow-lg mb-6 border border-gray-700 sticky top-0 z-10">
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4 items-center">
            <div className="lg:col-span-2">
                <h2 className="text-2xl font-bold text-white flex items-center gap-2"><DuplicateIcon className="w-6 h-6 text-cyan-400" aria-hidden="true"/>Results</h2>
                <p className="text-sm text-gray-400">Found <span className="font-bold text-cyan-400">{stats.numDuplicateFiles} duplicates</span> in <span className="font-bold text-cyan-400">{stats.numGroups} groups</span>.</p>
                <p className="text-sm text-gray-400">Potential space to save: <span className="font-bold text-green-400">{formatBytes(stats.spaceWasted)}</span></p>
                
                {processingErrors.length > 0 && (
                  <div className="mt-2">
                    <button 
                      onClick={() => setShowErrors(!showErrors)}
                      className="text-sm text-yellow-400 hover:text-yellow-300 flex items-center gap-1"
                      aria-label={showErrors ? "Hide processing errors" : "Show processing errors"}
                    >
                      <span>{showErrors ? 'Hide' : 'Show'} {processingErrors.length} processing errors</span>
                    </button>
                  </div>
                )}
            </div>
            <div className="flex flex-col sm:flex-row gap-2">
                <button onClick={selectAllButOneInGroups} className="bg-gray-600 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded-md text-sm w-full" aria-label="Select all duplicate files except one per group">
                  Select All Duplicates
                </button>
                <button onClick={() => setSelectedFiles(new Set())} className="bg-gray-600 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded-md text-sm w-full" aria-label="Deselect all files">
                  Deselect All
                </button>
            </div>
            <div className="flex flex-col sm:flex-row gap-2">
                <button 
                  onClick={() => setShowModal(true)} 
                  disabled={selectedFiles.size === 0} 
                  className="bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded-md text-sm disabled:bg-red-900 disabled:cursor-not-allowed w-full flex items-center justify-center gap-2"
                  aria-label={`Delete ${selectedFiles.size} selected files`}
                >
                  <TrashIcon className="w-5 h-5" aria-hidden="true"/>
                  Delete {selectedFiles.size} Files ({formatBytes(deletionSize)})
                </button>
                <button onClick={onReset} className="bg-cyan-500 hover:bg-cyan-600 text-white font-bold py-2 px-4 rounded-md text-sm w-full flex items-center justify-center gap-2" aria-label="Reset and start over">
                  <ResetIcon className="w-5 h-5" aria-hidden="true"/>
                  Start Over
                </button>
            </div>
        </div>
        
        {showErrors && processingErrors.length > 0 && (
          <div className="mt-4 bg-yellow-900/30 border border-yellow-700 rounded-md p-4">
            <h3 className="text-lg font-semibold text-yellow-400 mb-2">File Processing Errors:</h3>
            <ul className="max-h-40 overflow-y-auto">
              {processingErrors.map((error, index) => (
                <li key={index} className="py-1 border-b border-yellow-800/50 last:border-0">
                  <div className="font-mono text-sm text-yellow-200 truncate" title={error.path}>
                    {error.path}
                  </div>
                  <div className="text-xs text-yellow-400 italic">{error.error}</div>
                </li>
              ))}
            </ul>
          </div>
        )}
        
        {/* Pagination controls */}
        {imageGroups.length > itemsPerPage && (
          <div className="mt-4 flex flex-col sm:flex-row items-center justify-between gap-4 pt-4 border-t border-gray-700">
            <div className="flex items-center">
              <span className="text-sm text-gray-300 mr-2">Show:</span>
              <select 
                value={itemsPerPage} 
                onChange={handleItemsPerPageChange}
                className="bg-gray-700 text-white rounded px-2 py-1 text-sm"
                aria-label="Items per page"
              >
                <option value={5}>5</option>
                <option value={10}>10</option>
                <option value={20}>20</option>
                <option value={50}>50</option>
              </select>
              <span className="text-sm text-gray-300 ml-2">per page</span>
            </div>
            
            <div className="flex items-center gap-2">
              <button 
                onClick={goToPrevPage}
                disabled={currentPage === 0}
                className={`px-3 py-1 rounded ${currentPage === 0 ? 'bg-gray-700 text-gray-500 cursor-not-allowed' : 'bg-gray-600 text-white hover:bg-gray-500'}`}
                aria-label="Previous page"
              >
                Previous
              </button>
              
              <span className="text-gray-300">
                Page {currentPage + 1} of {totalPages}
              </span>
              
              <button 
                onClick={goToNextPage}
                disabled={currentPage === totalPages - 1}
                className={`px-3 py-1 rounded ${currentPage === totalPages - 1 ? 'bg-gray-700 text-gray-500 cursor-not-allowed' : 'bg-gray-600 text-white hover:bg-gray-500'}`}
                aria-label="Next page"
              >
                Next
              </button>
              
              <div className="flex gap-1">
                {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                  let pageNum;
                  if (totalPages <= 5) {
                    pageNum = i; // Pages 0 to 4 if total <= 5
                  } else if (currentPage < 2) {
                    pageNum = i; // First 5 pages if we're near the beginning
                  } else if (currentPage >= totalPages - 2) {
                    pageNum = totalPages - 5 + i; // Last 5 pages if we're near the end
                  } else {
                    pageNum = currentPage - 2 + i; // 5 pages centered on current
                  }
                  
                  return (
                    <button
                      key={i}
                      onClick={() => goToPage(pageNum)}
                      className={`w-8 h-8 rounded-full ${currentPage === pageNum ? 'bg-cyan-600 text-white' : 'bg-gray-600 text-white hover:bg-gray-500'}`}
                      aria-label={`Go to page ${pageNum + 1}`}
                    >
                      {pageNum + 1}
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="space-y-8">
        {currentGroups.map((group) => (
          <div key={group.id} className="bg-gray-800/50 p-4 rounded-lg border border-gray-700">
            <h3 className="text-lg font-semibold mb-3 text-gray-300">
              Group of {group.files.length} duplicates ({formatBytes(group.size)} each)
            </h3>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
              {group.files.map((image, index) => (
                <ImageCard 
                  key={image.path} 
                  image={image} 
                  isSelected={selectedFiles.has(image.path)}
                  onToggleSelect={handleToggleSelect}
                  isKept={index === 0}
                />
              ))}
            </div>
          </div>
        ))}
      </div>
      
      {/* Show pagination controls at the bottom as well */}
      {imageGroups.length > itemsPerPage && (
        <div className="mt-6 flex flex-col sm:flex-row items-center justify-between gap-4 pt-4 border-t border-gray-700">
          <div className="flex items-center">
            <span className="text-sm text-gray-300 mr-2">Show:</span>
            <select 
              value={itemsPerPage} 
              onChange={handleItemsPerPageChange}
              className="bg-gray-700 text-white rounded px-2 py-1 text-sm"
              aria-label="Items per page"
            >
              <option value={5}>5</option>
              <option value={10}>10</option>
              <option value={20}>20</option>
              <option value={50}>50</option>
            </select>
            <span className="text-sm text-gray-300 ml-2">per page</span>
          </div>
          
          <div className="flex items-center gap-2">
            <button 
              onClick={goToPrevPage}
              disabled={currentPage === 0}
              className={`px-3 py-1 rounded ${currentPage === 0 ? 'bg-gray-700 text-gray-500 cursor-not-allowed' : 'bg-gray-600 text-white hover:bg-gray-500'}`}
              aria-label="Previous page"
            >
              Previous
            </button>
            
            <span className="text-gray-300">
              Page {currentPage + 1} of {totalPages}
            </span>
            
            <button 
              onClick={goToNextPage}
              disabled={currentPage === totalPages - 1}
              className={`px-3 py-1 rounded ${currentPage === totalPages - 1 ? 'bg-gray-700 text-gray-500 cursor-not-allowed' : 'bg-gray-600 text-white hover:bg-gray-500'}`}
              aria-label="Next page"
            >
              Next
            </button>
            
            <div className="flex gap-1">
              {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                let pageNum;
                if (totalPages <= 5) {
                  pageNum = i;
                } else if (currentPage < 2) {
                  pageNum = i;
                } else if (currentPage >= totalPages - 2) {
                  pageNum = totalPages - 5 + i;
                } else {
                  pageNum = currentPage - 2 + i;
                }
                
                return (
                  <button
                    key={i}
                    onClick={() => goToPage(pageNum)}
                    className={`w-8 h-8 rounded-full ${currentPage === pageNum ? 'bg-cyan-600 text-white' : 'bg-gray-600 text-white hover:bg-gray-500'}`}
                    aria-label={`Go to page ${pageNum + 1}`}
                  >
                    {pageNum + 1}
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};