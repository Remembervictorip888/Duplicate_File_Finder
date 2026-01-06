import electronLogger from '../services/electronLogger';

export interface ProcessedFile {
  name: string;
  path: string;
  size: number;
  lastModified: number;
  content?: ArrayBuffer;
}

/**
 * Filter files to only include image files
 */
export const filterImageFiles = (files: FileList): File[] => {
  const imageFiles: File[] = [];
  const imageRegex = /\.(jpe?g|png|gif|bmp|webp|svg)$/i;

  for (let i = 0; i < files.length; i++) {
    const file = files[i];
    if (file && imageRegex.test(file.name)) {
      imageFiles.push(file);
    } else {
      electronLogger.info(`Skipping non-image file: ${file?.name || 'unknown'}`);
    }
  }

  return imageFiles;
};

/**
 * Convert File objects to data that can be processed by the worker
 */
export const convertFilesToData = async (files: File[]): Promise<ProcessedFile[]> => {
  const results: ProcessedFile[] = [];

  for (const file of files) {
    electronLogger.info(`Reading file: ${file.name}`);
    try {
      const arrayBuffer = await file.arrayBuffer();
      results.push({
        name: file.name,
        path: URL.createObjectURL(file),
        size: file.size,
        lastModified: file.lastModified,
        content: arrayBuffer
      });
    } catch (error) {
      electronLogger.error(`Error reading file ${file.name}: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  return results;
};