export default function EvidencePanel({ result }) {
  return (
    <section className="content-section">
      <p className="eyebrow">03 / SIGNAL SUMMARY</p>
      <h2 className="serif-heading section-heading">What informed the assessment</h2>
      <div className="single-signal">
        <div className="signal-title">
          <strong>Overall ranking signal</strong>
          <span>{result.probability_ai.toFixed(3)}</span>
        </div>
        <div className="score-track"><span style={{ width: `${result.probability_ai * 100}%` }} /></div>
      </div>
      <p className="muted small signal-caveat">This is one composite model score. The current API does not return separate measurements for texture, frequency patterns or boundary coherence, so those indicators are not reported individually.</p>
    </section>
  )
}