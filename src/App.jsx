import { useState, useRef, useCallback } from 'react'

const EXPIRE_OPTIONS = [
  { label: '30 mins', value: 30 * 60 * 1000 },
  { label: '1 hr', value: 60 * 60 * 1000 },
  { label: '2 hrs', value: 2 * 60 * 60 * 1000 },
  { label: '6 hrs', value: 6 * 60 * 60 * 1000 },
  { label: '12 hrs', value: 12 * 60 * 60 * 1000 },
  { label: '24 hrs', value: 24 * 60 * 60 * 1000 },
  { label: 'Custom', value: 'custom' },
]

function FileDrop() {
  const [isDragActive, setIsDragActive] = useState(false)
  const [selectedExpire, setSelectedExpire] = useState(EXPIRE_OPTIONS[0].value)
  const [showCustomPicker, setShowCustomPicker] = useState(false)
  const [customHours, setCustomHours] = useState(0)
  const [customMinutes, setCustomMinutes] = useState(0)
  const [showConfirmPopup, setShowConfirmPopup] = useState(false)
  const [droppedFiles, setDroppedFiles] = useState([])
  const fileInputRef = useRef(null)

  const handleDrag = useCallback((e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setIsDragActive(true)
    } else if (e.type === 'dragleave') {
      setIsDragActive(false)
    }
  }, [])

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragActive(false)
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      setDroppedFiles(Array.from(e.dataTransfer.files))
    }
  }, [])

  const handleFileSelect = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      setDroppedFiles(Array.from(e.target.files))
    }
  }

  const handleExpireChange = (value) => {
    if (value === 'custom') {
      setShowCustomPicker(true)
      setCustomHours(0)
      setCustomMinutes(30)
    } else {
      setSelectedExpire(value)
      setShowCustomPicker(false)
    }
  }

  const handleCustomConfirm = () => {
    const totalMs = (customHours * 60 + customMinutes) * 60 * 1000
    if (totalMs > 0) {
      setSelectedExpire(totalMs)
      setShowConfirmPopup(true)
    }
  }

  const handleConfirmPopupConfirm = () => {
    setShowConfirmPopup(false)
    setShowCustomPicker(false)
  }

  const formatExpireTime = (ms) => {
    if (ms === 'custom') return 'Custom'
    const hours = Math.floor(ms / (60 * 60 * 1000))
    const minutes = Math.floor((ms % (60 * 60 * 1000)) / (60 * 1000))
    if (hours > 0 && minutes > 0) return `${hours}h ${minutes}m`
    if (hours > 0) return `${hours}h`
    return `${minutes}m`
  }

  const currentExpireLabel = EXPIRE_OPTIONS.find(o => o.value === selectedExpire)?.label || formatExpireTime(selectedExpire)

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center py-12 px-4">
      <div className="fixed top-4 right-4 text-xs text-gray-400 font-mono">
        v1.0.0
      </div>

      <div className="w-full max-w-md bg-white rounded-xl shadow-sm border border-gray-200 p-8">
        <div className="flex items-baseline gap-1 mb-10">
          <span className="text-3xl font-semibold text-blue-600">File</span>
          <span className="text-3xl font-semibold text-gray-900">Drop</span>
        </div>

        <div
          className={`relative border-2 border-dashed rounded-lg p-12 text-center transition-colors cursor-pointer ${
            isDragActive
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-300 hover:border-gray-400'
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <input
            ref={fileInputRef}
            type="file"
            multiple
            className="hidden"
            onChange={handleFileSelect}
          />
          <svg
            className="mx-auto h-12 w-12 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
            />
          </svg>
          <p className="mt-4 text-gray-600 text-lg">Drag and drop files here</p>
          <p className="mt-1 text-gray-400 text-sm">or click to browse</p>
          {droppedFiles.length > 0 && (
            <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg text-left">
              <p className="text-green-800 font-medium text-sm">{droppedFiles.length} file(s) selected</p>
              <ul className="mt-2 max-h-40 overflow-y-auto">
                {droppedFiles.map((file, i) => (
                  <li key={i} className="text-sm text-green-700 flex justify-between">
                    <span className="truncate pr-2">{file.name}</span>
                    <span className="text-green-600">{(file.size / 1024).toFixed(1)} KB</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        <div className="mt-8">
          <label className="block text-sm font-medium text-gray-700 mb-2">Expire after:</label>
          <div className="relative">
            <select
              value={selectedExpire}
              onChange={(e) => handleExpireChange(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent appearance-none bg-white cursor-pointer"
            >
              {EXPIRE_OPTIONS.map((option) => (
                <option key={option.label} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
              <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </div>
          </div>
        </div>

        {showCustomPicker && (
          <div className="mt-6 p-6 bg-gray-50 rounded-lg border border-gray-200 animate-slide-down">
            <p className="text-sm font-medium text-gray-700 mb-4">Set custom expiration time</p>
            <div className="flex justify-center gap-4">
              <div className="relative">
                <label className="sr-only">Hours</label>
                <select
                  value={customHours}
                  onChange={(e) => setCustomHours(Number(e.target.value))}
                  className="w-24 px-3 py-2 border border-gray-300 rounded-lg text-center text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white appearance-none cursor-pointer"
                >
                  {Array.from({ length: 24 }, (_, i) => i).map((h) => (
                    <option key={h} value={h}>{h}h</option>
                  ))}
                </select>
              </div>
              <span className="text-gray-400 flex items-center text-lg">:</span>
              <div className="relative">
                <label className="sr-only">Minutes</label>
                <select
                  value={customMinutes}
                  onChange={(e) => setCustomMinutes(Number(e.target.value))}
                  className="w-24 px-3 py-2 border border-gray-300 rounded-lg text-center text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white appearance-none cursor-pointer"
                >
                  {Array.from({ length: 60 }, (_, i) => i).map((m) => (
                    <option key={m} value={m}>{m.toString().padStart(2, '0')}m</option>
                  ))}
                </select>
              </div>
            </div>
            <div className="mt-6 flex justify-end gap-3">
              <button
                type="button"
                onClick={() => setShowCustomPicker(false)}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleCustomConfirm}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
              >
                Confirm
              </button>
            </div>
          </div>
        )}

        <button
          type="button"
          className="mt-8 w-full py-3 px-6 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          disabled={droppedFiles.length === 0}
        >
          Drop
        </button>
      </div>

      {showConfirmPopup && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 animate-fade-in">
          <div className="bg-white rounded-xl shadow-xl max-w-sm w-full p-6 animate-scale-in">
            <div className="flex items-center justify-center w-12 h-12 mx-auto mb-4 bg-blue-100 rounded-full">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 text-center mb-2">Confirm Expiration</h3>
            <p className="text-gray-600 text-center mb-6">
              Files will expire after <span className="font-medium text-blue-600">
                {customHours}h {customMinutes.toString().padStart(2, '0')}m
              </span>
            </p>
            <div className="flex gap-3">
              <button
                onClick={() => setShowConfirmPopup(false)}
                className="flex-1 py-2 px-4 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleConfirmPopupConfirm}
                className="flex-1 py-2 px-4 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
              >
                Confirm
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default FileDrop