import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Navbar from '../components/Navbar.jsx'
import Footer from '../components/Footer.jsx'
import ImageUploader from '../components/ImageUploader.jsx'
import Disclaimer from '../components/Disclaimer.jsx'
import { analyzeImage } from '../services/api.js'
import { saveAnalysis } from '../services/analysisStore.js'

export default function Home() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleAnalyze(file) {
    setLoading(true)
    setError('')
    try {
      const result = await analyzeImage(file)
      const metadata = { name: file.name, type: file.type, size: file.size, uploadedAt: new Date().toISOString() }
      await saveAnalysis(file, result, metadata)
      navigate('/results', { state: { result, metadata } })
    } catch (err) {
      setError(err.message || 'Something went wrong while analyzing the image.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <Navbar />
      <main className="shell">
        <section className="hero">
          <p className="eyebrow">IMAGE FORENSICS / RESEARCH PROJECT</p>
          <h1 className="serif-heading">Look closer.<br />Question what you see.</h1>
          <p className="hero-copy">Analyze images for patterns associated with AI-generated content using machine learning and visual forensics.</p>
        </section>

        <section className="investigation-grid">
          <ImageUploader onAnalyze={handleAnalyze} loading={loading} error={error} />
          <aside className="context-panel">
            <p className="eyebrow">A NOTE ON INTERPRETATION</p>
            <h2 className="serif-heading">Evidence needs context.</h2>
            <p>Image detectors can respond to patterns that are not unique to generated images. Compression, resizing, editing and unfamiliar cameras can all affect a score.</p>
            <ul className="plain-list">
              <li>Use the highest-quality original available.</li>
              <li>Consider the image's source and surrounding context.</li>
              <li>Read the ranking score as one signal, not a conclusion.</li>
            </ul>
          </aside>
        </section>

        <section className="how-section" id="how-it-works">
          <div className="section-heading-row">
            <div><p className="eyebrow">THE PROCESS</p><h2 className="serif-heading">How it works</h2></div>
            <span className="micro-label">THREE STEPS</span>
          </div>
          <div className="steps-grid">
            <article><span className="step-number">01</span><h3>Provide an image</h3><p>Upload an image you have permission to analyze. The available image is passed to the model for assessment.</p></article>
            <article><span className="step-number">02</span><h3>Examine the signal</h3><p>The model compares learned visual representations and returns a single ranking score.</p></article>
            <article><span className="step-number">03</span><h3>Put findings in context</h3><p>Consider the score alongside provenance, source information and other independent evidence.</p></article>
          </div>
        </section>

        <section className="principles-grid" id="research">
          <article className="principle">
            <p className="eyebrow">EVALUATION / MODEL SCOPE</p>
            <h2 className="serif-heading">Signals, not certainty.</h2>
            <p>Detection is an evolving research problem. The model can rank images differently from the generators and photographs it encountered during training.</p>
            <p>Independent evaluation found a substantial false-positive rate on genuine photographs. TrustLens therefore presents a ranking signal rather than an authenticity verdict.</p>
          </article>
          <article className="principle principle-note">
            <p className="eyebrow">PRIVACY / DATA HANDLING</p>
            <h2 className="serif-heading">Handle every image with care.</h2>
            <p>Only upload images you have permission to analyze. Avoid submitting private, confidential or sensitive images.</p>
            <p className="note-inset">Just exploring?<br />Use non-sensitive sample images and interpret every result cautiously.</p>
          </article>
        </section>
        <Disclaimer compact />
        <Footer />
      </main>
    </>
  )
}