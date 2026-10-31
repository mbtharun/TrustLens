import { useEffect, useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import Navbar from '../components/Navbar.jsx'
import Footer from '../components/Footer.jsx'
import Disclaimer from '../components/Disclaimer.jsx'
import AnalysisSummary from '../components/AnalysisSummary.jsx'
import EvidencePanel from '../components/EvidencePanel.jsx'
import FileMetadata from '../components/FileMetadata.jsx'
import { loadAnalysis, clearAnalysis } from '../services/analysisStore.js'

export default function Results() {
  const location = useLocation()
  const navigate = useNavigate()
  const [record, setRecord] = useState(null)
  const [imageUrl, setImageUrl] = useState('')
  const [dimensions, setDimensions] = useState('')
  const [loading, setLoading] = useState(!record)
  const [loadError, setLoadError] = useState('')

  useEffect(() => {
    let active = true
    async function hydrate() {
      try {
        const saved = await loadAnalysis()
        if (!active) return
        if (saved?.result && saved?.file && saved?.metadata) {
          setRecord(saved)
          return
        }
        if (location.state?.result && location.state?.metadata) {
          setRecord({ result: location.state.result, metadata: location.state.metadata, file: null })
          return
        }
        setLoadError('There is no saved analysis in this browser session. Start a new investigation to analyze an image.')
      } catch {
        setLoadError('The saved analysis could not be restored. Start a new investigation.')
      } finally {
        if (active) setLoading(false)
      }
    }
    if (!record) hydrate()
    return () => { active = false }
  }, [])

  useEffect(() => {
    if (!record?.file) return
    const url = URL.createObjectURL(record.file)
    setImageUrl(url)
    const image = new Image()
    image.onload = () => setDimensions(`${image.naturalWidth} × ${image.naturalHeight}`)
    image.src = url
    return () => URL.revokeObjectURL(url)
  }, [record])

  async function newAnalysis() {
    await clearAnalysis().catch(() => {})
    navigate('/')
  }

  if (loading) return <><Navbar /><main className="shell state-shell"><p className="muted">Restoring your analysis…</p></main></>
  if (!record?.result || !record?.metadata) {
    return (
      <><Navbar /><main className="shell state-shell">
        <p className="eyebrow">TRUSTLENS / INVESTIGATION</p>
        <h1 className="serif-heading">No analysis to display.</h1>
        <p className="muted">{loadError || 'The analysis state is unavailable.'}</p>
        <Link className="button button-primary inline-button" to="/">Start an investigation</Link>
        <Footer />
      </main></>
    )
  }

  const file = record.file
  return (
    <>
      <Navbar />
      <main className="shell results-shell">
        <div className="breadcrumb"><Link to="/">Home</Link><span>›</span><span>Example analysis</span></div>
        <div className="results-title-row">
          <div><p className="eyebrow">IMAGE ANALYSIS / MODEL OUTPUT</p><h1 className="serif-heading">A closer look at the evidence.</h1><p className="muted small">{record.metadata.name} · {new Date(record.metadata.uploadedAt).toLocaleString()}</p></div>
          <div className="result-actions"><button className="button button-primary" onClick={newAnalysis}>Analyze another</button><button className="button button-secondary" onClick={() => window.print()}>Export report</button></div>
        </div>
        <Disclaimer />
        <section className="result-top-grid">
          <figure className="original-image">
            {imageUrl && <img src={imageUrl} alt={`Uploaded image ${record.metadata.name}`} />}
            <figcaption><span>01 / ORIGINAL IMAGE</span><span>{record.metadata.name}</span></figcaption>
          </figure>
          <AnalysisSummary result={record.result} />
        </section>
        <section className="details-grid">
          <EvidencePanel result={record.result} />
          {file ? <FileMetadata file={file} dimensions={dimensions} uploadedAt={record.metadata.uploadedAt} /> : (
            <section className="metadata-card"><p className="eyebrow">04 / FILE DETAILS</p><h2 className="serif-heading section-heading">About the file</h2><p className="muted small">File details are available after restoring the uploaded image from this browser.</p></section>
          )}
        </section>
        <section className="interpretation">
          <p className="eyebrow">05 / INTERPRETATION</p>
          <h2 className="serif-heading section-heading">A mixed set of signals.</h2>
          <p>The score is a ranking signal produced by the current model. It does not establish whether this image is real or AI-generated, and it should not be interpreted as a calibrated probability.</p>
          <div className="limits-box"><strong>Keep these limits in view</strong><ul><li>Genuine photographs can receive high ranking scores.</li><li>Unseen generators and image processing can change model behavior.</li><li>Use provenance and independent evidence before drawing conclusions.</li></ul></div>
        </section>
        <Footer />
      </main>
    </>
  )
}