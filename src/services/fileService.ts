/**
 * File service to handle file-related operations
 */

export const filterImageFiles = (files: FileList): File[] => {
  return Array.from(files).filter(file => 
    /image\/(jpeg|png|gif|bmp|webp)/.test(file.type)
  );
};

export const convertFilesToData = async (files: File[]): Promise<Array<{
  path: string;
  name: string;
  size: number;
  type: string;
  arrayBuffer: ArrayBuffer;
}>> => {
  const fileDataPromises = files.map(async (file) => {
    try {
      console.log(`Reading file: ${file.name}`);
      const arrayBuffer = await file.arrayBuffer();
      return {
        path: (file as any).webkitRelativePath || file.name,
        name: file.name,
        size: file.size,
        type: file.type,
        arrayBuffer
      };
    } catch (error) {
      console.error(`Error reading file ${file.name}:`, error);
      throw new Error(`Failed to read file ${file.name}: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  });

  // Wait for all array buffers to be ready
  const fileDataResults = await Promise.all(fileDataPromises);
  return fileDataResults;
};