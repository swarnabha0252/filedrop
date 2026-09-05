import { useState, useRef, useCallback, useEffect } from 'react'
import { Routes, Route, Navigate, useParams } from 'react-router-dom'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const EXPIRE_OPTIONS = [
  { label: '30 mins', value: 30 * 60 * 1000 },
  { label: '1 hr', value: 60 * 60 * 1000 },
  { label: '2 hrs', value: 2 * 60 * 60 * 1000 },
  { label: '6 hrs', value: 6 * 60 * 60 * 1000 },
  { label: '12 hrs', value: 12 * 60 * 60 * 1000 },
  { label: '24 hrs', value: 24 * 60 * 60 * 1000 },
  { label: 'Custom', value: 'custom' },
]

function formatFileSize(bytes) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function formatTimeRemaining(expiresAt) {
  const now = new Date()
  const expiry = new Date(expiresAt)
  const diffMs = expiry - now

  if (diffMs <= 0) return 'Expired'

  const minutes = Math.floor(diffMs / 60000)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)

  if (days > 0) return `${days}d ${hours % 24}h`
  if (hours > 0) return `${hours}h ${minutes % 60}m`
  return `${minutes}m`
}



function UploadPage() {
  const [isDragActive, setIsDragActive] = useState(false)
  const [selectedExpire, setSelectedExpire] = useState(EXPIRE_OPTIONS[0].value)
  const [showCustomPicker, setShowCustomPicker] = useState(false)
  const [customHours, setCustomHours] = useState(0)
  const [customMinutes, setCustomMinutes] = useState(0)
  const [showConfirmPopup, setShowConfirmPopup] = useState(false)
  const [downloadLimit, setDownloadLimit] = useState('')
  const [droppedFiles, setDroppedFiles] = useState([])
  const [uploading, setUploading] = useState(false)
  const [uploadError, setUploadError] = useState(null)
  const [successData, setSuccessData] = useState(null)
  const [copyStatus, setCopyStatus] = useState('idle')
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

  const handleUpload = async () => {
    if (droppedFiles.length === 0) return

    setUploading(true)
    setUploadError(null)
    setSuccessData(null)

    const file = droppedFiles[0]
    const expirySeconds = Math.floor(selectedExpire / 1000)
    const limit = downloadLimit ? parseInt(downloadLimit, 10) : null

    const formData = new FormData()
    formData.append('file', file)
    formData.append('expiry', expirySeconds.toString())
    if (limit) formData.append('download_limit', limit.toString())

    try {
      const res = await fetch(`${API_BASE}/api/v1/files`, {
        method: 'POST',
        body: formData,
      })

      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail?.message || err.detail || 'Upload failed')
      }

      const data = await res.json()
      setSuccessData(data)
      setDroppedFiles([])
    } catch (_err) {
      setUploadError(_err.message)
    } finally {
      setUploading(false)
    }
  }

  const handleCopyLink = async () => {
    if (!successData) return

    try {
      await navigator.clipboard.writeText(successData.download_url)
      setCopyStatus('copied')
      setTimeout(() => setCopyStatus('idle'), 2000)
    } catch {
      setCopyStatus('failed')
      setTimeout(() => setCopyStatus('idle'), 2000)
    }
  }

  const handleNewUpload = () => {
    setSuccessData(null)
    setUploadError(null)
  }

  if (successData) {
    const shareUrl = successData.download_url
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col items-center py-12 px-4">
        <div className="fixed top-4 right-4 text-xs text-gray-400 font-mono">
          v1.0.0
        </div>

        <div className="w-full max-w-md bg-white rounded-xl shadow-sm border border-gray-200 p-8 animate-scale-in">
          <div className="flex items-baseline gap-1 mb-10">
            <span className="text-3xl font-semibold text-blue-600">File</span>
            <span className="text-3xl font-semibold text-gray-900">Drop</span>
          </div>

          <div className="text-center mb-8">
            <div className="flex items-center justify-center w-16 h-16 mx-auto mb-4 bg-green-100 rounded-full">
              <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h2 className="text-2xl font-semibold text-gray-900 mb-1">File uploaded</h2>
            <p className="text-gray-500">Your file is ready to share</p>
          </div>

          <div className="mb-6 p-4 bg-gray-50 rounded-lg border border-gray-200 text-center">
            <p className="font-medium text-gray-900 truncate">{successData.filename}</p>
            <p className="text-sm text-gray-500 mt-1">{formatFileSize(successData.size)}</p>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
            <p className="text-sm font-medium text-blue-800 text-center mb-4">Your file is ready to share</p>

            <div className="bg-white border border-blue-200 rounded-lg p-4 mb-4">
              <div className="font-mono text-sm text-blue-900 break-all text-center select-all" id="share-link">
                {shareUrl}
              </div>
            </div>

            <button
              onClick={handleCopyLink}
              className="w-full py-3 px-6 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={copyStatus !== 'idle'}
            >
              {copyStatus === 'copied' ? 'Copied!' : copyStatus === 'failed' ? 'Failed' : 'Copy Link'}
            </button>

            <p className="mt-4 text-center text-sm text-blue-700">
              Expires in {formatTimeRemaining(successData.expires_at)}
            </p>
          </div>

          <button
            onClick={handleNewUpload}
            className="mt-6 w-full py-3 px-6 bg-gray-100 text-gray-700 font-medium rounded-lg hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2 transition-colors"
          >
            Upload Another File
          </button>
        </div>
      </div>
    )
  }

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
                    <span className="text-green-600">{formatFileSize(file.size)}</span>
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

        <div className="mt-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">Download limit (optional):</label>
          <input
            type="number"
            min="1"
            placeholder="Unlimited"
            value={downloadLimit}
            onChange={(e) => setDownloadLimit(e.target.value)}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
            aria-describedby="download-limit-help"
          />
          <p id="download-limit-help" className="mt-1 text-xs text-gray-500">Leave empty for unlimited downloads</p>
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

        {uploadError && (
          <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
            {uploadError}
          </div>
        )}

        <button
          type="button"
          onClick={handleUpload}
          className="mt-8 w-full py-3 px-6 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          disabled={droppedFiles.length === 0 || uploading}
        >
          {uploading ? 'Uploading...' : 'Drop'}
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

function DownloadPage() {
  const { token } = useParams()
  const [metadata, setMetadata] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [downloading, setDownloading] = useState(false)
  const [downloadError, setDownloadError] = useState(null)
  const [showPasswordModal, setShowPasswordModal] = useState(false)
  const [password, setPassword] = useState('')
  const [passwordError, setPasswordError] = useState('')
  const [countdown, setCountdown] = useState('')

  useEffect(() => {
    const fetchMetadata = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/v1/files/${token}`)
        if (!res.ok) {
          setError(true)
          return
        }
        const data = await res.json()
        setMetadata(data)
      } catch {
        setError(true)
      } finally {
        setLoading(false)
      }
    }
    fetchMetadata()
  }, [token])

  useEffect(() => {
    if (!metadata) return

    const updateCountdown = () => {
      const now = new Date()
      const expiry = new Date(metadata.expires_at)
      const diffMs = expiry - now

      if (diffMs <= 0) {
        setCountdown('Expired')
        setError(true)
        setMetadata(null)
        return
      }

      const totalSeconds = Math.floor(diffMs / 1000)
      const hours = Math.floor(totalSeconds / 3600)
      const minutes = Math.floor((totalSeconds % 3600) / 60)
      const seconds = totalSeconds % 60

      if (hours > 0) {
        setCountdown(`${hours}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`)
      } else {
        setCountdown(`${minutes}:${seconds.toString().padStart(2, '0')}`)
      }
    }

    updateCountdown()
    const interval = setInterval(updateCountdown, 1000)
    return () => clearInterval(interval)
  }, [metadata])

  const handleDownload = async () => {
    if (!metadata) return

    if (metadata.password_required) {
      setShowPasswordModal(true)
      return
    }

    setDownloading(true)
    setDownloadError(null)

    try {
      const res = await fetch(`${API_BASE}/api/v1/files/${token}/download`)
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail?.message || 'Download failed')
      }

      const blob = await res.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = metadata.filename
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (_err) {
      setDownloadError(_err.message)
    } finally {
      setDownloading(false)
    }
  }

  const handlePasswordDownload = async () => {
    setPasswordError('')
    setDownloading(true)

    try {
      const verifyRes = await fetch(`${API_BASE}/api/v1/files/${token}/verify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password }),
      })

      if (!verifyRes.ok) {
        const err = await verifyRes.json()
        throw new Error(err.detail?.message || 'Invalid password')
      }

      const { download_url } = await verifyRes.json()
      const res = await fetch(download_url)

      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail?.message || 'Download failed')
      }

      const blob = await res.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = metadata.filename
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      setShowPasswordModal(false)
      setPassword('')
    } catch (_err) {
      setPasswordError(_err.message)
    } finally {
      setDownloading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
        <div className="w-full max-w-md bg-white rounded-xl shadow-sm border border-gray-200 p-8 text-center">
          <div className="flex items-center justify-center w-12 h-12 mx-auto mb-4 bg-blue-100 rounded-full animate-pulse">
            <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <p className="text-gray-600">Loading file info...</p>
        </div>
      </div>
    )
  }

  if (error || !metadata) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
        <div className="w-full max-w-md bg-white rounded-xl shadow-sm border border-gray-200 p-8 text-center animate-fade-in">
          <div className="flex items-center justify-center w-16 h-16 mx-auto mb-6 bg-amber-100 rounded-full">
            <svg className="w-8 h-8 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h1 className="text-2xl font-semibold text-gray-900 mb-2">Link Expired</h1>
          <p className="text-gray-600 leading-relaxed">
            This file is no longer available.
          </p>
          <p className="text-gray-500 text-sm mt-2">
            The link may have expired or reached its download limit.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center py-12 px-4">
      <div className="fixed top-4 right-4 text-xs text-gray-400 font-mono">
        v1.0.0
      </div>

      <div className="w-full max-w-md bg-white rounded-xl shadow-sm border border-gray-200 p-8 animate-scale-in">
        <div className="flex items-baseline gap-1 mb-10">
          <span className="text-3xl font-semibold text-blue-600">File</span>
          <span className="text-3xl font-semibold text-gray-900">Drop</span>
        </div>

        <div className="text-center mb-8">
          <div className="flex items-center justify-center w-16 h-16 mx-auto mb-4 bg-blue-100 rounded-full">
            <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
            </svg>
          </div>
          <h2 className="text-2xl font-semibold text-gray-900 mb-1">{metadata.filename}</h2>
          <p className="text-gray-500">{formatFileSize(metadata.size)}</p>
        </div>

        <div className="mb-6 p-4 bg-gray-50 rounded-lg border border-gray-200 text-center">
          <p className="text-sm text-gray-600">Expires in</p>
          <p className="text-2xl font-mono font-semibold text-blue-600 mt-1">{countdown || formatTimeRemaining(metadata.expires_at)}</p>
        </div>

        {downloadError && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
            {downloadError}
          </div>
        )}

        <button
          onClick={handleDownload}
          disabled={downloading}
          className="w-full py-3 px-6 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {downloading ? 'Downloading...' : 'Download'}
        </button>

        {metadata.password_required && (
          <p className="mt-4 text-center text-sm text-gray-500">
            This file is password protected
          </p>
        )}

        {metadata.download_limit && (
          <p className="mt-4 text-center text-sm text-gray-500">
            Downloads: {metadata.download_count} / {metadata.download_limit}
          </p>
        )}
      </div>

      {showPasswordModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 animate-fade-in">
          <div className="bg-white rounded-xl shadow-xl max-w-sm w-full p-6 animate-scale-in">
            <div className="flex items-center justify-center w-12 h-12 mx-auto mb-4 bg-blue-100 rounded-full">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 text-center mb-2">Password Required</h3>
            <p className="text-gray-600 text-center mb-6">Enter the password to download this file</p>

            {passwordError && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm text-center">
                {passwordError}
              </div>
            )}

            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter password"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white mb-4"
              autoFocus
            />

            <div className="flex gap-3">
              <button
                onClick={() => { setShowPasswordModal(false); setPassword(''); setPasswordError(''); }}
                className="flex-1 py-2 px-4 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handlePasswordDownload}
                disabled={downloading}
                className="flex-1 py-2 px-4 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {downloading ? 'Downloading...' : 'Download'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<UploadPage />} />
      <Route path="/f/:token" element={<DownloadPage />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App