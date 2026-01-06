import { useState, useEffect, useCallback } from 'react';
import type { ProcessedFile } from '../../types';
import { filterImageFiles, convertFilesToData } from '../services/fileService';

interface WorkerDuplicateGroup {
  id: string;
  hash: string;
  files: ProcessedFile[];
  size: number;
}

interface FileProcessingError {
  path: string;
  name: string;
  error: string;
}

interface UseWorkerManagerResult {
  worker: Worker | null;
  duplicateGroups: WorkerDuplicateGroup[];
  processingErrors: FileProcessingError[];
  statusMessage: string;
  processState: 'idle' | 'processing' | 'done';
}

export const useWorkerManager = (): UseWorkerManagerResult => {
  const [worker, setWorker] = useState<Worker | null>(null);
  const [processState, setProcessState] = useState<'idle' | 'processing' | 'done'>('idle');
  const [statusMessage, setStatusMessage] = useState<string>('');
  const [duplicateGroups, setDuplicateGroups] = useState<WorkerDuplicateGroup[]>([]);
  const [processingErrors, setProcessingErrors] = useState<FileProcessingError[]>([]);

  // Initialize Web Worker
  useEffect(() => {
    console.log('Initializing worker...');
    
    if (typeof Worker !== 'undefined') {
      try {
        // Create the worker from the JavaScript file
        const workerUrl = new URL('../workers/fileProcessor.js', import.meta.url);
        console.log('Creating worker with URL:', workerUrl);
        
        const newWorker = new Worker(workerUrl);
        
        // Handle messages from the worker
        newWorker.onmessage = (e) => {
          console.log('Received message from worker:', e.data);
          const { type, groups, error, index, total, fileName, errors } = e.data;
          
          switch (type) {
            case 'progress':
              setStatusMessage(`Processing file ${index} of ${total}: ${fileName}`);
              break;
              
            case 'completed':
              setDuplicateGroups(groups);
              setProcessState('done');
              if (processingErrors.length > 0) {
                setStatusMessage(`Processing completed with ${processingErrors.length} errors. See details in results.`);
              } else {
                setStatusMessage('Duplicate detection completed successfully');
              }
              break;
              
            case 'errors':
              setProcessingErrors(prev => [...prev, ...errors]);
              break;
              
            case 'error':
              console.error('Worker error:', error);
              setStatusMessage(`Error: ${error}`);
              setProcessState('idle');
              break;
          }
        };
        
        setWorker(newWorker);
        
        // Cleanup function
        return () => {
          console.log('Terminating worker...');
          newWorker.terminate();
        };
      } catch (err) {
        console.error('Error initializing worker:', err);
        setStatusMessage('Failed to initialize the processing worker. Please check the console for details.');
      }
    } else {
      console.error('Web Workers are not supported in this browser');
      setStatusMessage('Web Workers are not supported in your browser. Please use a modern browser.');
    }
    
    console.log('Worker initialization complete');
  }, []);

  return {
    worker,
    duplicateGroups,
    processingErrors,
    statusMessage,
    processState,
  };
};

export const useWorkerActions = (
  worker: Worker | null, 
  setProcessState: (state: 'idle' | 'processing' | 'done') => void
) => {
  const processFiles = useCallback(async (files: FileList) => {
    console.log('Processing files:', files);
    if (!worker) {
      console.error('Worker not initialized yet.');
      return;
    }
    
    setProcessState('processing');

    // Filter image files using the service
    const imageFiles = filterImageFiles(files);

    console.log(`Found ${imageFiles.length} image files out of ${files.length} total files`);

    if (imageFiles.length < 2) {
      console.warn('Not enough images to compare');
      setProcessState('idle');
      return;
    }

    try {
      // Prepare file data for the worker using the service
      const fileData = await convertFilesToData(imageFiles);
      console.log(`Sending ${fileData.length} files to worker for processing`);
      
      // Send file data to the worker for processing
      worker.postMessage({
        type: 'processFiles',
        files: fileData
      });
    } catch (error) {
      console.error('Error preparing files for worker:', error);
      setProcessState('idle');
    }
  }, [worker, setProcessState]);

  return { processFiles };
};