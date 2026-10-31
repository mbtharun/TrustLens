import { useRef, useState } from 'react'

const ACCEPTED = ['image/jpeg', 'image/png', 'image/webp']
const MAX_BYTES = 10 * 1024 * 1024

export default function ImageUploader({ onAnalyze, loading, error }) {
  const inputRef = useRef(null)
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState('')
  const [dragging, setDragging] = useState(false)
  const [localError, setLocalError] = useState('')

  function chooseFile(candidate) {
    if (!candidate) return
    setLocalError('')
    if (!ACCEPTED.includes(candidate.type)) {
      setLocalError('Please choose a JPG, PNG or WebP image.')
      return
    }
    if (candidate.size > MAX_BYTES) {
      setLocalError('The image must be 10 MB or smaller.')
      return
    }
    setFile(candidate)
    setPreview(URL.createObjectURL(candidate))
  }

  function clearFile() {
    if (preview) URL.revokeObjectURL(preview)
    setPreview('')
    setFile(null)
    setLocalError('')
    if (inputRef.current) inputRef.current.value = ''
  }

  return (
    <section className="upload-card" aria-labelledby="upload-heading">
      <div className="section-topline">
        <h2 id="upload-heading">Start an investigation</h2>
        <span className="micro-label">01 / IMAGE INPUT</span>
      </div>
      {!file ? (
        <div
          className={`dropzone ${dragging ? 'is-dragging' : ''}`}
          onDragOver={(event) => { event.preventDefault(); setDragging(true) }}
          onDragLeave={() => setDragging(false)}
          onDrop={(event) => {
            event.preventDefault()
            setDragging(false)
            chooseFile(event.dataTransfer.files?.[0])
          }}
        >
          <input
            ref={inputRef}
            type="file"
            accept="image/jpeg,image/png,image/webp"
            aria-label="Choose an image"
            onChange={(event) => chooseFile(event.target.files?.[0])}
          />
          <div className="upload-glyph" aria-hidden="true">▧</div>
          <strong>Drop an image here to inspect</strong>
          <span className="muted small">or select a file from your device</span>
          <button className="button button-primary" type="button" onClick={() => inputRef.current?.click()}>
            Choose image
          </button>
          <span className="file-hint">JPG, PNG or WebP · up to 10 MB</span>
        </div>
      ) : (
        <div className="selected-file">
          <img src={preview} alt="Selected image preview" />
          <div className="selected-meta">
            <strong>{file.name}</strong>
            <span>{(file.size / (1024 * 1024)).toFixed(2)} MB · {file.type.split('/')[1].toUpperCase()}</span>
            <button className="text-button" type="button" onClick={clearFile}>Remove image</button>
          </div>
          <button className="button button-primary analyze-button" disabled={loading} onClick={() => onAnalyze(file)}>
            {loading ? <><span className="spinner" /> Analyzing…</> : 'Analyze image'}
          </button>
        </div>
      )}
      {(localError || error) && <p className="form-error" role="alert">{localError || error}</p>}
      <div className="upload-footnote">Use only images you have permission to analyze. Avoid uploading private or sensitive material.</div>
    </section>
  )
}