const { app, BrowserWindow, dialog, ipcMain } = require('electron');
const { join, dirname } = require('path');
const { existsSync, readdirSync, readFileSync, statSync } = require('fs');
const { platform } = require('process');

// Function to create the main window with detailed error handling
const createWindow = () => {
  console.log('Creating main window...');
  
  const window = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: join(__dirname, 'preload.js')
    },
    icon: join(__dirname, '..', 'public', 'favicon.ico') // Use your app's icon if available
  });

  // Determine the correct URL based on environment
  const appURL = app.isPackaged
    ? new URL(`file://${join(__dirname, '..', 'dist', 'index.html')}`)
    : new URL('http://localhost:5173'); // Default to 5173, Vite typically uses this

  console.log(`Loading URL: ${appURL.href}`);
  
  window.loadURL(appURL.href)
    .then(() => {
      console.log('Window loaded successfully');
    })
    .catch(err => {
      console.error('Error loading window:', err);
    });
  
  // Open dev tools in development mode
  if (!app.isPackaged) {
    console.log('Opening dev tools in development mode');
    window.webContents.openDevTools();
  }

  // Add error handling for the window
  window.webContents.on('did-fail-load', (event, errorCode, errorDescription) => {
    console.error(`WebContents failed to load: ${errorCode} - ${errorDescription}`);
  });

  window.webContents.on('render-process-gone', (event, details) => {
    console.error('Render process gone:', details);
  });

  window.on('unresponsive', () => {
    console.warn('Window became unresponsive');
  });

  return window;
};

// Handle folder selection with error handling
ipcMain.handle('select-folder', async () => {
  console.log('Handling folder selection request');
  try {
    const result = await dialog.showOpenDialog({
      properties: ['openDirectory', 'multiSelections']
    });
    
    if (!result.canceled && result.filePaths.length > 0) {
      const selectedPath = result.filePaths[0];
      
      console.log(`Selected path: ${selectedPath}`);
      
      // Check if the path exists and is a directory
      if (existsSync(selectedPath) && statSync(selectedPath).isDirectory()) {
        try {
          // Get files in the directory
          const allFiles = readdirSync(selectedPath);
          console.log(`Found ${allFiles.length} total files in ${selectedPath}`);
          
          // Filter for image files
          const imageFiles = allFiles.filter(file => {
            const filePath = join(selectedPath, file);
            // Check if it's a file (not a subdirectory) and has an image extension
            return statSync(filePath).isFile() && 
                   /\.(jpe?g|png|gif|bmp|webp)$/i.test(file);
          });
          
          console.log(`Found ${imageFiles.length} image files in ${selectedPath}`);
          
          return {
            path: selectedPath,
            files: imageFiles, // Just the filenames
            fullPathFiles: imageFiles.map(file => join(selectedPath, file)), // Full paths for reading
            success: true
          };
        } catch (err) {
          console.error('Error reading directory:', err);
          return {
            success: false,
            error: err.message
          };
        }
      } else {
        console.error(`Path does not exist or is not a directory: ${selectedPath}`);
        return {
          success: false,
          error: 'Selected path does not exist or is not a directory'
        };
      }
    } else {
      console.log('Folder selection was cancelled or no folder selected');
      return {
        success: false,
        error: 'No folder selected or selection cancelled'
      };
    }
  } catch (error) {
    console.error('Error in folder selection:', error);
    return {
      success: false,
      error: error.message
    };
  }
});

// Handle file reading
ipcMain.handle('read-file-content', async (event, filePath) => {
  console.log('Handling file reading request for:', filePath);
  try {
    const fileContent = readFileSync(filePath);
    console.log(`Successfully read file: ${filePath}, size: ${fileContent.length} bytes`);
    return {
      success: true,
      content: fileContent.buffer.slice(fileContent.byteOffset, fileContent.byteOffset + fileContent.byteLength)
    };
  } catch (error) {
    console.error('Error reading file:', error);
    return {
      success: false,
      error: error.message
    };
  }
});

// Add error handling for the app
process.on('uncaughtException', (error) => {
  console.error('Uncaught Exception:', error);
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
});

app.whenReady().then(() => {
  console.log('App is ready, creating window...');
  createWindow();

  app.on('activate', () => {
    console.log('App activated');
    if (BrowserWindow.getAllWindows().length === 0) {
      console.log('No windows exist, creating new window');
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  console.log('All windows closed');
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

console.log(`App starting, platform: ${platform}, packaged: ${app.isPackaged}`);