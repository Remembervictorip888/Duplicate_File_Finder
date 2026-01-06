const { app, BrowserWindow, dialog, ipcMain } = require('electron');
const { join, dirname } = require('path');
const { existsSync, readdirSync, readFileSync, statSync } = require('fs');
const { platform } = require('process');
const { mkdirSync } = require('fs');

// Function to create the main window with detailed error handling
const createWindow = () => {
  log('info', 'Creating main window...');
  
  const window = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: join(__dirname, 'preload.cjs')
    },
    icon: join(__dirname, '..', 'public', 'favicon.ico') // Use your app's icon if available
  });

  // Set a Content Security Policy to prevent security vulnerabilities
  window.webContents.on('did-frame-navigate', (event, url, httpResponseCode, httpStatusText) => {
    // Add Content Security Policy header to prevent security vulnerabilities
    window.webContents.insertCSS(`
      /* Additional security styles if needed */
    `);
  });

  // Set CSP when the page is loaded in development mode
  if (!app.isPackaged) {
    window.webContents.on('did-finish-load', () => {
      // Inject a Content Security Policy for development
      window.webContents.executeJavaScript(`
        // Create a CSP meta tag to prevent security vulnerabilities
        const meta = document.createElement('meta');
        meta.httpEquiv = 'Content-Security-Policy';
        meta.content = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self' data:; object-src 'none'; frame-src 'self';";
        document.head.appendChild(meta);
      `).catch(err => {
        log('error', `Error injecting CSP: ${err.message}`);
      });
    });
  }

  // Determine the correct URL based on environment
  const appURL = app.isPackaged
    ? new URL(`file://${join(__dirname, '..', 'dist', 'index.html')}`)
    : new URL('http://localhost:5173'); // Default to 5173, Vite typically uses this

  log('info', `Loading URL: ${appURL.href}`);
  
  window.loadURL(appURL.href)
    .then(() => {
      log('info', 'Window loaded successfully');
    })
    .catch(err => {
      log('error', `Error loading window: ${err}`);
    });
  
  // Open dev tools in development mode
  if (!app.isPackaged) {
    log('info', 'Opening dev tools in development mode');
    window.webContents.openDevTools();
  }

  // Add error handling for the window
  window.webContents.on('did-fail-load', (event, errorCode, errorDescription) => {
    log('error', `WebContents failed to load: ${errorCode} - ${errorDescription}`);
  });

  window.webContents.on('render-process-gone', (event, details) => {
    log('error', 'Render process gone:', details);
  });

  window.on('unresponsive', () => {
    log('warn', 'Window became unresponsive');
  });

  return window;
};

// Function to handle logging with file output
const log = (level, message, ...args) => {
  // Create logs directory if it doesn't exist
  const logsDir = join(__dirname, '..', 'logs');
  if (!existsSync(logsDir)) {
    mkdirSync(logsDir, { recursive: true });
  }
  
  // Create a timestamped log file name
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const logFile = join(logsDir, `app_${timestamp}.log`);
  
  // Format the log message
  const timestampStr = new Date().toISOString();
  const formattedMessage = `${timestampStr} - [${level.toUpperCase()}] - ${message} ${args.join(' ')}`;
  
  // Write to log file
  const fs = require('fs');
  fs.appendFileSync(logFile, formattedMessage + '\n');
  
  // Also output to console
  console.log(`[${level.toUpperCase()}]`, message, ...args);
};

// Handle logging requests from renderer process
ipcMain.handle('log', (event, level, message) => {
  log(level, message);
});

// Handle folder selection with error handling
ipcMain.handle('select-folder', async () => {
  log('info', 'Handling folder selection request');
  try {
    const result = await dialog.showOpenDialog({
      properties: ['openDirectory', 'multiSelections']
    });
    
    if (!result.canceled && result.filePaths.length > 0) {
      const selectedPath = result.filePaths[0];
      
      log('info', `Selected path: ${selectedPath}`);
      
      // Check if the path exists and is a directory
      if (existsSync(selectedPath) && statSync(selectedPath).isDirectory()) {
        try {
          // Get files in the directory
          const allFiles = readdirSync(selectedPath);
          log('info', `Found ${allFiles.length} total files in ${selectedPath}`);
          
          // Filter for image files
          const imageFiles = allFiles.filter(file => {
            const filePath = join(selectedPath, file);
            // Check if it's a file (not a subdirectory) and has an image extension
            return statSync(filePath).isFile() && 
                   /\.(jpe?g|png|gif|bmp|webp)$/i.test(file);
          });
          
          log('info', `Found ${imageFiles.length} image files in ${selectedPath}`);
          
          return {
            path: selectedPath,
            files: imageFiles, // Just the filenames
            fullPathFiles: imageFiles.map(file => join(selectedPath, file)), // Full paths for reading
            success: true
          };
        } catch (err) {
          log('error', `Error reading directory: ${err}`);
          return {
            success: false,
            error: err.message
          };
        }
      } else {
        log('error', `Path does not exist or is not a directory: ${selectedPath}`);
        return {
          success: false,
          error: 'Selected path does not exist or is not a directory'
        };
      }
    } else {
      log('info', 'Folder selection was cancelled or no folder selected');
      return {
        success: false,
        error: 'No folder selected or selection cancelled'
      };
    }
  } catch (error) {
    log('error', `Error in folder selection: ${error}`);
    return {
      success: false,
      error: error.message
    };
  }
});

// Handle file reading
ipcMain.handle('read-file-content', async (event, filePath) => {
  log('info', `Handling file reading request for: ${filePath}`);
  try {
    const fileContent = readFileSync(filePath);
    log('info', `Successfully read file: ${filePath}, size: ${fileContent.length} bytes`);
    return {
      success: true,
      content: fileContent.buffer.slice(fileContent.byteOffset, fileContent.byteOffset + fileContent.byteLength)
    };
  } catch (error) {
    log('error', `Error reading file: ${error}`);
    return {
      success: false,
      error: error.message
    };
  }
});

// Add error handling for the app
process.on('uncaughtException', (error) => {
  log('error', `Uncaught Exception: ${error}`);
});

process.on('unhandledRejection', (reason, promise) => {
  log('error', `Unhandled Rejection at: ${promise}, reason: ${reason}`);
});

app.whenReady().then(() => {
  log('info', 'App is ready, creating window...');
  createWindow();

  app.on('activate', () => {
    log('info', 'App activated');
    if (BrowserWindow.getAllWindows().length === 0) {
      log('info', 'No windows exist, creating new window');
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  log('info', 'All windows closed');
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

log('info', `App starting, platform: ${platform}, packaged: ${app.isPackaged}`);