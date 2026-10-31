import { Link, NavLink } from 'react-router-dom'

export default function Navbar() {
  return (
    <header className="site-nav">
      <div className="nav-inner">
        <Link to="/" className="brand" aria-label="TrustLens home">
          <span className="brand-mark" aria-hidden="true"><span /></span>
          <span>TrustLens</span>
        </Link>
        <nav className="nav-links" aria-label="Main navigation">
          <NavLink to="/" end>Home</NavLink>
          <a href="/#how-it-works">How it works</a>
          <a href="/#research">Research</a>
          <a href="https://github.com/" target="_blank" rel="noreferrer">GitHub</a>
        </nav>
        <a className="nav-icon" href="/docs" title="API documentation" aria-label="API documentation">↗</a>
      </div>
    </header>
  )
}