const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  selectFolder: () => ipcRenderer.invoke('select-folder'),
  log: (level, message) => ipcRenderer.invoke('log', level, message),
  readFileContent: (filePath) => ipcRenderer.invoke('read-file-content', filePath)
});