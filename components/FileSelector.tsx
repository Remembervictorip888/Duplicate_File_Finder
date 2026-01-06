import React, { useRef } from 'react';
import { FolderIcon } from './icons';

// Define the type for the electronAPI
declare global {
  interface Window {
    electronAPI: {
      selectFolder: () => Promise<{
        success: boolean;
        path?: string;
        files?: string[]; // filenames only
        fullPathFiles?: string[]; // full paths for reading
        error?: string;
      }>;
      readFileContent: (filePath: string) => Promise<{
        success: boolean;
        content?: ArrayBuffer;
        error?: string;
      }>;
    };
  }
}

interface FileSelectorProps {
  onFilesSelect: (files: FileList) => void;
}

export const FileSelector: React.FC<FileSelectorProps> = ({ onFilesSelect }) => {
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    console.log('File input change event triggered');
    if (event.target.files && event.target.files.length > 0) {
      console.log(`Received ${event.target.files.length} files from web input`);
      onFilesSelect(event.target.files);
    } else {
      console.warn('No files received from web input');
    }
  };

  const handleClick = async () => {
    console.log('Button clicked, checking for Electron API');
    // Check if we're running in Electron
    if (window.electronAPI) {
      console.log('Using Electron API to select folder');
      // Use Electron API to select a folder
      const result = await window.electronAPI.selectFolder();
      console.log('Electron API result:', result);
      
      if (result.success && result.path && result.fullPathFiles) {
        console.log(`Selected folder: ${result.path}`);
        console.log(`Found ${result.fullPathFiles.length} image files`);
        
        try {
          // Create actual File objects from the file paths by reading their content
          const fileObjects: File[] = [];
          
          for (const filePath of result.fullPathFiles) {
            console.log(`Reading file: ${filePath}`);
            const fileReadResult = await window.electronAPI.readFileContent(filePath);
            
            if (fileReadResult.success && fileReadResult.content) {
              // Extract filename from path (everything after the last slash)
              const fileName = filePath.split(/[\\/]/).pop() || 'unknown';
              
              // Create a proper File object with the actual content
              const file = new File([fileReadResult.content], fileName, { 
                type: getFileType(fileName) 
              });
              
              fileObjects.push(file);
              console.log(`Created File object for: ${fileName}`);
            } else {
              console.error(`Failed to read file: ${filePath}`, fileReadResult.error);
            }
          }

          // Create a DataTransfer object to hold the files like a real file input
          const dataTransfer = new DataTransfer();
          fileObjects.forEach(file => {
            console.log(`Adding file to DataTransfer: ${file.name}`);
            dataTransfer.items.add(file);
          });
          
          console.log(`Created FileList with ${dataTransfer.files.length} files`);
          
          // Call the onFilesSelect callback with the FileList
          onFilesSelect(dataTransfer.files);
        } catch (error) {
          console.error('Error creating file objects:', error);
          alert(`Error processing files: ${error}`);
        }
      } else {
        console.error('Error selecting folder:', result.error);
        alert(`Error: ${result.error || 'Unknown error'}`);
      }
    } else {
      console.log('Using standard web file input');
      // Use the standard web file input
      inputRef.current?.click();
    }
  };

  // Helper function to determine file type based on extension
  const getFileType = (fileName: string): string => {
    const ext = fileName.toLowerCase().split('.').pop();
    switch (ext) {
      case 'jpg':
      case 'jpeg':
        return 'image/jpeg';
      case 'png':
        return 'image/png';
      case 'gif':
        return 'image/gif';
      case 'bmp':
        return 'image/bmp';
      case 'webp':
        return 'image/webp';
      default:
        return 'application/octet-stream';
    }
  };

  console.log('FileSelector rendering');

  return (
    <div className="flex-grow flex flex-col items-center justify-center text-center p-8 bg-gray-800 rounded-lg shadow-2xl border border-gray-700">
      <FolderIcon className="w-24 h-24 text-gray-500 mb-6" />
      <h2 className="text-3xl font-bold text-white mb-2">Ready to Clean Up?</h2>
      <p className="text-gray-400 max-w-md mb-8">
        Select a folder on your computer to scan for duplicate images. The app will analyze the contents and show you all identical files.
      </p>
      <input
        type="file"
        ref={inputRef}
        onChange={handleFileChange}
        className="hidden"
        // @ts-ignore
        webkitdirectory="true"
        directory="true"
        multiple
        aria-label="Select folder to scan for duplicate images"
      />
      <button
        onClick={handleClick}
        className="bg-cyan-500 hover:bg-cyan-600 text-white font-bold py-3 px-8 rounded-lg text-lg transition-all duration-300 ease-in-out transform hover:scale-105 shadow-lg flex items-center gap-3"
      >
        <FolderIcon className="w-6 h-6" />
        {window.electronAPI ? 'Select Folder to Scan (Desktop)' : 'Select Folder to Scan (Web)'}
      </button>
      <div className="mt-8 text-sm text-gray-500 bg-gray-900 p-4 rounded-md border border-gray-700 max-w-lg">
        <p className="font-semibold text-yellow-400 mb-2">Important Note on Privacy & Security:</p>
        <p>
          This application processes all your files directly in your browser.
          Your images are <span className="font-bold text-green-400">never uploaded</span> to any server, ensuring your data remains completely private and secure on your local machine.
        </p>
      </div>
    </div>
  );
};