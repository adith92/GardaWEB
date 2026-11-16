const { contextBridge, ipcRenderer } = require('electron');
contextBridge.exposeInMainWorld('garda', { connect: url => ipcRenderer.invoke('garda-connect', url) });
