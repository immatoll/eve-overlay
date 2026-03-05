# eve-overlay

Electron-based overlay window launcher and manager.

- **Purpose:** Provides a small menu window to open and manage overlay windows. Overlays can load either local UI or remote URLs and support frameless transparent windows for in-game overlays.

- **Main entry:** [main.js](main.js)
- **UI files:** [menu.html](menu.html), [window.html](window.html), [test.html](test.html)
- **Styles:** css/ (fonts.css, menu.css, window.css)
- **Fonts:** fonts/

**Run (development)**:

- Install dependencies (Electron is required):

```bash
npm install
```

- Start the app:

```bash
npm start
```

(The `start` script runs `electron .` as defined in `package.json`.)

**Key behavior & IPC channels**

- `main.js` creates a small menu window (`menu.html`) and can spawn overlay windows via `createOverlayWindow()`.
- Overlays support two modes:
  - Remote: loads a URL in a framed window (OS window controls enabled).
  - Local: loads `window.html` in a frameless, transparent window suited for in-game overlays.

- IPC channels used by the app:
  - `window:minimize` — minimize the sending window
  - `window:close` — close/destroy the sending window
  - `window:getBounds` — returns current window bounds
  - `window:setBounds` — apply new window bounds (resize/move)
  - `menu:openOverlay` — request opening a new overlay (payload may be a string title or `{ title, url }`)

**Notes & requirements**

- Requires Node.js and Electron. If Electron is not installed locally, install it as a devDependency or globally:

```bash
npm install --save-dev electron
# or
npm install -g electron
```

- This repository doesn't bundle overlays; `menu.html` is the launcher UI and `window.html` is the local overlay UI.

**Files to inspect**

- [main.js](main.js) — app entry and window management logic
- [menu.html](menu.html) — launcher UI
- [window.html](window.html) — local overlay UI

If you want, I can:
- add a short README section showing how to build an overlay payload example
- add a `devDependencies` entry for `electron` in `package.json`
- create a simple overlay example inside `window.html`
