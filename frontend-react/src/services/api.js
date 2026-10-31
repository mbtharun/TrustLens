const API_BASE = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '')

export async function analyzeImage(file) {
  const form = new FormData()
  form.append('file', file)

  let response
  try {
    response = await fetch(`${API_BASE}/analyze`, {
      method: 'POST',
      body: form,
    })
  } catch {
    throw new Error('Could not reach the analysis server. Check that FastAPI is running.')
  }

  const contentType = response.headers.get('content-type') || ''
  const data = contentType.includes('application/json')
    ? await response.json()
    : {}

  if (!response.ok) {
    throw new Error(data.detail || `Analysis failed (${response.status}).`)
  }

  if (typeof data.probability_ai !== 'number' || !Number.isFinite(data.probability_ai)) {
    throw new Error('The API response did not contain a valid probability_ai score.')
  }

  return {
    probability_ai: Math.min(1, Math.max(0, data.probability_ai)),
    model: data.model || 'Model information not supplied',
    note: data.note || 'This is a model ranking signal, not a definitive authenticity verdict.',
  }
}