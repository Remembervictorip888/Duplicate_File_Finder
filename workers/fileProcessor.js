// File processing Web Worker
// This worker will handle hashing and duplicate detection without blocking the UI
// Now with chunked processing for better scalability

const CHUNK_SIZE = 50; // Process files in chunks of 50

// This is a module that will run in the worker context
self.onmessage = async function(e) {
  const { type, files } = e.data;
  
  if (type === 'processFiles') {
    try {
      // Process files in chunks to improve scalability
      const processedFiles = await processFilesWithHashesInChunks(files);
      const duplicates = findDuplicates(processedFiles);
      
      // Send the final results back to the main thread
      self.postMessage({
        type: 'completed',
        groups: duplicates
      });
    } catch (error) {
      self.postMessage({
        type: 'error',
        error: error instanceof Error ? error.message : 'Unknown error occurred'
      });
    }
  }
};

async function processFilesWithHashesInChunks(fileArray) {
  const results = [];
  const errors = [];
  
  // Process files in chunks
  for (let i = 0; i < fileArray.length; i += CHUNK_SIZE) {
    const chunk = fileArray.slice(i, i + CHUNK_SIZE);
    
    // Process the current chunk
    for (let j = 0; j < chunk.length; j++) {
      const { path, name, size, type, arrayBuffer } = chunk[j];
      const absoluteIndex = i + j;
      
      // Post progress update
      self.postMessage({
        type: 'progress',
        index: absoluteIndex + 1,
        total: fileArray.length,
        fileName: name
      });
      
      try {
        const hash = await hashFile(arrayBuffer);
        results.push({
          path: path,
          hash,
          name: name,
          size: size,
          type: type
        });
      } catch (error) {
        // Collect the error but continue processing other files
        errors.push({
          path: path,
          name: name,
          error: error instanceof Error ? error.message : 'Unknown error'
        });
        console.error(`Could not process file ${name}:`, error);
      }
    }
    
    // Yield control back to the main thread after each chunk
    // This allows the UI to remain responsive
    await new Promise(resolve => setTimeout(resolve, 0));
  }
  
  // Report any errors to the main thread
  if (errors.length > 0) {
    self.postMessage({
      type: 'errors',
      errors: errors
    });
  }
  
  return results;
}

async function hashFile(arrayBuffer) {
  try {
    const hashBuffer = await crypto.subtle.digest('SHA-256', arrayBuffer);
    return Array.from(new Uint8Array(hashBuffer))
      .map(b => b.toString(16).padStart(2, '0'))
      .join('');
  } catch (error) {
    throw new Error(`Failed to hash file: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}

function findDuplicates(processedFiles) {
  const hashMap = new Map();
  
  // Group files by hash
  for (const file of processedFiles) {
    if (hashMap.has(file.hash)) {
      hashMap.get(file.hash).push(file);
    } else {
      hashMap.set(file.hash, [file]);
    }
  }
  
  // Filter groups that have more than one file (duplicates)
  const duplicateGroups = [];
  let groupId = 0;
  
  hashMap.forEach((group, hash) => {
    if (group.length > 1) {
      duplicateGroups.push({
        id: `group-${groupId++}`,
        hash,
        files: group,
        size: group[0].size
      });
    }
  });
  
  return duplicateGroups;
}