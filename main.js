const { app, BrowserWindow, ipcMain } = require("electron")

let menuWindow

function createMenu(){

  menuWindow = new BrowserWindow({
    width: 210,
    height: 360,
    minHeight: 360,
    maxHeight: 840,
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    resizable: false,
    webPreferences:{
      nodeIntegration: true,
      contextIsolation: false
    }
  })

  menuWindow.loadFile("menu.html")
}

function createOverlayWindow(opts = {}) {
  const { title = "Overlay", isRemote = true, url = "" } = opts || {}

  // Build options conditionally: remote URLs get a framed window so OS controls work;
  // local overlay UI uses a frameless window with custom chrome.
  const overlay = new BrowserWindow({
    width: 800,
    height: 600,
    minWidth: 200,
    minHeight: 150,
    frame: !!isRemote,              // framed if loading a remote URL
    transparent: isRemote ? false : true,
    alwaysOnTop: true,
    resizable: true,
    webPreferences: isRemote ? {
      nodeIntegration: false,
      contextIsolation: true
    } : {
      nodeIntegration: true,
      contextIsolation: false,
      webviewTag: true
    }
  })

  if (isRemote) {
    // Load the external URL directly in the framed window so window chrome is available
    overlay.loadURL(url).catch(err => console.error('overlay.loadURL failed', err))
  } else {
    // Load the local overlay UI and pass title/url via query
    overlay.loadFile("window.html", { query: { title, url } })
  }

  return overlay
}

app.whenReady().then(createMenu)

// IPC Listener für Menu-Klicks
ipcMain.on("window:minimize", (event) => {
  const win = BrowserWindow.fromWebContents(event.sender)
  win.minimize()
})

ipcMain.on("window:close", (event) => {
  const win = BrowserWindow.fromWebContents(event.sender)
  win.destroy()
})

// Provide current bounds to renderer (used for resizing calculations)
ipcMain.handle('window:getBounds', (event) => {
  const win = BrowserWindow.fromWebContents(event.sender)
  return win.getBounds()
})

// Apply new bounds requested by renderer during resize
ipcMain.on('window:setBounds', (event, bounds) => {
  const win = BrowserWindow.fromWebContents(event.sender)
  if (!win) return

  // Sanitize and enforce minimums
  const sanitized = {
    x: Math.round(bounds.x || 0),
    y: Math.round(bounds.y || 0),
    width: Math.max(200, Math.round(bounds.width || win.getBounds().width)),
    height: Math.max(150, Math.round(bounds.height || win.getBounds().height))
  }

  win.setBounds(sanitized)
})

// Öffnet ein neues Overlay-Fenster
ipcMain.on("menu:openOverlay", (event, payload) => {
  // payload may be a string (title) or an object { title, url }
  if (payload && typeof payload === 'object') {
    createOverlayWindow(payload)
  } else {
    createOverlayWindow({ title: String(payload || 'Overlay') })
  }
})

app.on("window-all-closed", () => {
  app.quit()
})