import { useState, useEffect, useCallback } from 'react';
import type { ProcessedFile } from '../../types';
import { filterImageFiles, convertFilesToData } from '../services/fileService';
import electronLogger from '../services/electronLogger';

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
    electronLogger.info('Initializing worker...');
    
    if (typeof Worker !== 'undefined') {
      try {
        // Create the worker from the JavaScript file
        const workerUrl = new URL('../workers/fileProcessor.js', import.meta.url);
        electronLogger.info('Creating worker with URL: ' + workerUrl);
        
        const newWorker = new Worker(workerUrl);
        
        // Handle messages from the worker
        newWorker.onmessage = (e) => {
          electronLogger.info('Received message from worker: ' + JSON.stringify(e.data));
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
              electronLogger.error('Worker error: ' + error);
              setStatusMessage(`Error: ${error}`);
              setProcessState('idle');
              break;
          }
        };
        
        setWorker(newWorker);
        
        // Cleanup function
        return () => {
          electronLogger.info('Terminating worker...');
          newWorker.terminate();
        };
      } catch (err) {
        electronLogger.error('Error initializing worker: ' + (err instanceof Error ? err.message : String(err)));
        setStatusMessage('Failed to initialize the processing worker. Please check the console for details.');
      }
    } else {
      electronLogger.error('Web Workers are not supported in this browser');
      setStatusMessage('Web Workers are not supported in your browser. Please use a modern browser.');
    }
    
    electronLogger.info('Worker initialization complete');
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
  setProcessState: (state: 'idle' | 'processing' | 'done') => void,
  setStatusMessage: (message: string) => void
) => {
  const processFiles = useCallback(async (files: FileList) => {
    electronLogger.info('Processing files: ' + files.length + ' files');
    if (!worker) {
      electronLogger.error('Worker not initialized yet.');
      setStatusMessage('Worker not initialized yet.');
      setProcessState('idle');
      return;
    }
    
    setProcessState('processing');

    // Filter image files using the service
    const imageFiles = filterImageFiles(files);

    electronLogger.info(`Found ${imageFiles.length} image files out of ${files.length} total files`);

    if (imageFiles.length < 2) {
      electronLogger.warn('Not enough images to compare');
      setStatusMessage('Need at least 2 image files to find duplicates');
      setProcessState('idle');
      return;
    }

    try {
      // Prepare file data for the worker using the service
      const fileData = await convertFilesToData(imageFiles);
      electronLogger.info(`Sending ${fileData.length} files to worker for processing`);
      
      // Send file data to the worker for processing
      worker.postMessage({
        type: 'processFiles',
        files: fileData
      });
    } catch (error) {
      electronLogger.error('Error preparing files for worker: ' + (error instanceof Error ? error.message : String(error)));
      setStatusMessage('Failed to prepare files for processing');
      setProcessState('idle');
    }
  }, [worker, setProcessState, setStatusMessage]);

  return { processFiles };
};