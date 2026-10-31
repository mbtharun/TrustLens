function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`
}

export default function FileMetadata({ file, dimensions, uploadedAt }) {
  const rows = [
    ['Filename', file.name],
    ['Format', file.type.split('/')[1]?.toUpperCase() || 'Unknown'],
    ['File size', formatBytes(file.size)],
    ['Dimensions', dimensions || 'Unavailable'],
    ['Analyzed', uploadedAt ? new Date(uploadedAt).toLocaleString() : 'Just now'],
  ]
  return (
    <section className="metadata-card">
      <p className="eyebrow">04 / FILE DETAILS</p>
      <h2 className="serif-heading section-heading">About the file</h2>
      <dl className="metadata-list">
        {rows.map(([label, value]) => (
          <div className="metadata-row" key={label}>
            <dt>{label}</dt><dd>{value}</dd>
          </div>
        ))}
      </dl>
      <p className="muted tiny">Metadata is read from the uploaded file in your browser. It does not verify the image's provenance.</p>
    </section>
  )
}