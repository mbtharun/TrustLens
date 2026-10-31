import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Home from './pages/Home.jsx'
import Results from './pages/Results.jsx'

function NotFound() {
  return (
    <main className="shell not-found">
      <p className="eyebrow">TRUSTLENS / 404</p>
      <h1 className="serif-heading">This page isn't here.</h1>
      <a className="text-link" href="/">Return to TrustLens home →</a>
    </main>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/results" element={<Results />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  )
}