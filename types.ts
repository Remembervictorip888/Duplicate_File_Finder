export type ProcessState = 'idle' | 'processing' | 'done';

export interface ImageFile {
  file: File;
  previewUrl: string;
  path: string;
}

export interface ProcessedFile {
  path: string;
  hash: string;
  name: string;
  size: number;
  type: string;
}

export interface DuplicateGroup {
  id: string;
  hash: string;
  files: ProcessedFile[];
  size: number;
}

export interface Stats {
  numGroups: number;
  numDuplicateFiles: number;
  spaceWasted: number;
}

export interface FileProcessingError {
  path: string;
  name: string;
  error: string;
}