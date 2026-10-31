export default function Disclaimer({ compact = false }) {
  return (
    <aside className={`disclaimer ${compact ? 'disclaimer-compact' : ''}`} id="notice">
      <span className="disclaimer-symbol" aria-hidden="true">!</span>
      <div>
        <strong>Read this as a ranking, not a verdict.</strong>
        <p>TrustLens can incorrectly score genuine photographs as AI-generated and can miss AI-generated images. A high score is a reason to look closer, not proof of an image's origin.</p>
      </div>
    </aside>
  )
}