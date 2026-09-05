# FileDrop

A lightweight, minimalistic file sharing web application with drag-and-drop functionality and configurable expiration times.

## Features

- **Drag & Drop** - Upload files by dragging them onto the drop zone or clicking to browse
- **Expiration Settings** - Set file expiration: 30 mins, 1 hr, 2 hrs, 6 hrs, 12 hrs, 24 hrs, or custom time
- **Custom Time Picker** - Phone-style scrollable hours/minutes dropdown for precise expiration
- **Confirmation Dialog** - Confirm custom expiration before applying
- **File Preview** - See selected files with names and sizes
- **Minimalistic UI** - Clean, light theme with subtle animations

## Tech Stack

- **React 19** with Vite
- **Tailwind CSS v4** for styling
- **PostCSS** for CSS processing

## Getting Started

### Install dependencies

```bash
npm install
```

### Development server

```bash
npm run dev
```

Opens at `http://localhost:5173`

### Production build

```bash
npm run build
```

Output in `dist/`

### Preview production build

```bash
npm run preview
```

## Project Structure

```
filedrop/
├── src/
│   ├── App.jsx       # Main component with all features
│   ├── main.jsx      # React entry point
│   └── index.css     # Tailwind imports + custom animations
├── index.html        # HTML entry point
├── tailwind.config.js
├── postcss.config.js
├── vite.config.js
└── package.json
```

## Usage

1. Open the app in browser
2. Drag files onto the drop zone or click to select
3. Choose expiration time from dropdown (or select "Custom" for precise time)
4. Click **Drop** to initiate sharing (button enables after file selection)

## Custom Animations

Defined in `src/index.css`:
- `animate-slide-down` - For custom time picker panel
- `animate-fade-in` - For confirmation modal backdrop
- `animate-scale-in` - For confirmation modal content