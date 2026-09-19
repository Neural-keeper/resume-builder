import { useEffect, useMemo, useState } from 'react'
import {
  ArrowUpRight,
  BriefcaseBusiness,
  Check,
  ChevronRight,
  CircleHelp,
  Download,
  FileText,
  LayoutDashboard,
  Link as LinkIcon,
  LoaderCircle,
  LockKeyhole,
  Plus,
  Save,
  Settings2,
  Sparkles,
  Trash2,
  UserRound,
  X,
} from 'lucide-react'
import { supabase } from './lib/supabase'
import './styles.css'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const DEV_TOKEN = 'local-development-token'

const emptyDocument = {
  profile: { name: '', email: '', title: '', phone: '', location: '', links: {} },
  summaries: {},
  education: [],
  experiences: [],
  certifications: [],
  projects: [],
  skills: {},
}

const blankExperience = () => ({
  id: `exp_${Date.now()}`,
  company: '',
  role: '',
  dates: '',
  location: '',
  tags: [],
  bullets: [''],
})

function App() {
  const [document, setDocument] = useState(emptyDocument)
  const [view, setView] = useState('overview')
  const [token, setToken] = useState(localStorage.getItem('resume_token') || DEV_TOKEN)
  const [session, setSession] = useState(null)
  const [authReady, setAuthReady] = useState(!supabase)
  const [targetTitle, setTargetTitle] = useState('')
  const [selectedIds, setSelectedIds] = useState([])
  const [status, setStatus] = useState({ type: 'idle', message: '' })
  const [loading, setLoading] = useState(false)
  const [showConnection, setShowConnection] = useState(false)

  const experiences = document.experiences || []
  const selectedExperiences = useMemo(
    () => experiences.filter((experience) => selectedIds.includes(experience.id)),
    [experiences, selectedIds],
  )

  useEffect(() => {
    if (!supabase) {
      loadMaster()
      return undefined
    }

    let active = true
    supabase.auth.getSession().then(({ data }) => {
      if (!active) return
      setSession(data.session)
      setAuthReady(true)
      if (data.session) loadMaster(data.session.access_token)
    })
    const { data: listener } = supabase.auth.onAuthStateChange((_event, nextSession) => {
      setSession(nextSession)
      setAuthReady(true)
      if (nextSession) loadMaster(nextSession.access_token)
    })
    return () => {
      active = false
      listener.subscription.unsubscribe()
    }
  }, [])

  async function request(path, options = {}, accessToken = session?.access_token || token) {
    const response = await fetch(`${API_URL}${path}`, {
      ...options,
      headers: {
        Authorization: `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
        ...(options.headers || {}),
      },
    })
    if (!response.ok) throw new Error((await response.json().catch(() => ({}))).detail || `Request failed (${response.status})`)
    return response
  }

  async function loadMaster(accessToken) {
    setLoading(true)
    try {
      const response = await request('/api/v1/me/master', {}, accessToken)
      const loaded = await response.json()
      setDocument({ ...emptyDocument, ...loaded, profile: { ...emptyDocument.profile, ...(loaded.profile || {}) } })
      setStatus({ type: 'success', message: 'Master resume loaded' })
    } catch (error) {
      setStatus({ type: 'error', message: error.message || 'Could not reach the API' })
    } finally {
      setLoading(false)
    }
  }

  async function saveMaster() {
    setLoading(true)
    try {
      await request('/api/v1/me/master', { method: 'PUT', body: JSON.stringify(document) })
      localStorage.setItem('resume_token', token)
      setStatus({ type: 'success', message: 'Changes saved' })
    } catch (error) {
      setStatus({ type: 'error', message: error.message || 'Could not save changes' })
    } finally {
      setLoading(false)
    }
  }

  async function signInWithGoogle() {
    if (!supabase) return
    const { error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: { redirectTo: window.location.origin },
    })
    if (error) setStatus({ type: 'error', message: error.message })
  }

  async function signOut() {
    await supabase?.auth.signOut()
    setSession(null)
    setDocument(emptyDocument)
  }

  async function buildResume() {
    setLoading(true)
    try {
      const response = await request('/api/v1/me/build', {
        method: 'POST',
        body: JSON.stringify({ target_title: targetTitle, selected_exp_ids: selectedIds }),
      })
      const blob = await response.blob()
      const url = URL.createObjectURL(blob)
      const link = window.document.createElement('a')
      link.href = url
      link.download = `${(targetTitle || 'resume').replace(/\s+/g, '_')}.pdf`
      link.click()
      URL.revokeObjectURL(url)
      setStatus({ type: 'success', message: 'PDF ready to download' })
    } catch (error) {
      setStatus({ type: 'error', message: error.message || 'Could not build PDF' })
    } finally {
      setLoading(false)
    }
  }

  function updateProfile(field, value) {
    setDocument((current) => ({ ...current, profile: { ...current.profile, [field]: value } }))
  }

  function updateExperience(id, field, value) {
    setDocument((current) => ({
      ...current,
      experiences: current.experiences.map((experience) => experience.id === id ? { ...experience, [field]: value } : experience),
    }))
  }

  function addExperience() {
    const experience = blankExperience()
    setDocument((current) => ({ ...current, experiences: [...current.experiences, experience] }))
    setSelectedIds((current) => [...current, experience.id])
  }

  function removeExperience(id) {
    setDocument((current) => ({ ...current, experiences: current.experiences.filter((experience) => experience.id !== id) }))
    setSelectedIds((current) => current.filter((selectedId) => selectedId !== id))
  }

  function toggleExperience(id) {
    setSelectedIds((current) => current.includes(id) ? current.filter((selectedId) => selectedId !== id) : [...current, id])
  }

  const navItems = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard },
    { id: 'profile', label: 'Master profile', icon: UserRound },
    { id: 'experience', label: 'Experience', icon: BriefcaseBusiness },
    { id: 'builder', label: 'Resume builder', icon: FileText },
  ]

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand"><span className="brand-mark"><Sparkles size={17} /></span><span>Resume<br /><strong>Studio</strong></span></div>
        <div className="workspace-label">WORKSPACE</div>
        <nav>
          {navItems.map(({ id, label, icon: Icon }) => <button key={id} className={`nav-item ${view === id ? 'active' : ''}`} onClick={() => setView(id)}><Icon size={18} /><span>{label}</span>{view === id && <ChevronRight size={15} className="nav-arrow" />}</button>)}
        </nav>
        <div className="sidebar-bottom">
          <button className="nav-item" onClick={() => setShowConnection(true)}><Settings2 size={18} /><span>Connection</span></button>
          <div className="sync-card"><span className="status-dot" /> <span>Local workspace</span><CircleHelp size={15} /></div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar"><div><p className="eyebrow">Resume workspace</p><h1>{view === 'builder' ? 'Shape your next opportunity.' : view === 'profile' ? 'Your professional foundation.' : view === 'experience' ? 'The work behind the story.' : 'A sharper resume, less repetition.'}</h1></div><div className="top-actions"><span className={`save-state ${status.type}`}><span className="status-dot" />{status.message || 'Ready to edit'}</span>{supabase && !session ? <button className="button button-orange" onClick={signInWithGoogle}>Sign in with Google</button> : <><button className="icon-button" title="Connection settings" onClick={() => setShowConnection(true)}><LockKeyhole size={17} /></button><button className="button button-dark" onClick={saveMaster} disabled={loading}><Save size={16} />Save changes</button></>}</div></header>

        {status.type === 'error' && <div className="alert error">{status.message}</div>}
        {status.type === 'success' && <div className="alert success"><Check size={15} />{status.message}</div>}

        {!authReady ? <div className="auth-wait"><LoaderCircle size={22} className="spin" /><p>Checking your workspace...</p></div> : supabase && !session ? <AuthGate signInWithGoogle={signInWithGoogle} /> : view === 'overview' && <Overview document={document} experiences={experiences} selectedIds={selectedIds} setView={setView} />}
        {authReady && (!supabase || session) && view === 'profile' && <Profile document={document} updateProfile={updateProfile} />}
        {authReady && (!supabase || session) && view === 'experience' && <ExperienceList experiences={experiences} updateExperience={updateExperience} addExperience={addExperience} removeExperience={removeExperience} />}
        {authReady && (!supabase || session) && view === 'builder' && <Builder targetTitle={targetTitle} setTargetTitle={setTargetTitle} experiences={experiences} selectedIds={selectedIds} toggleExperience={toggleExperience} selectedExperiences={selectedExperiences} buildResume={buildResume} />}
      </main>

      {showConnection && <Connection token={token} setToken={setToken} apiUrl={API_URL} session={session} onSignIn={signInWithGoogle} onSignOut={signOut} onClose={() => setShowConnection(false)} onReload={loadMaster} />}
      {loading && <div className="loading-indicator"><LoaderCircle size={16} className="spin" /> Working</div>}
    </div>
  )
}

function AuthGate({ signInWithGoogle }) {
  return <section className="auth-gate"><span className="brand-mark"><Sparkles size={17} /></span><span className="kicker">PRIVATE WORKSPACE</span><h2>Your resume, in one place.</h2><p>Sign in to securely load your master resume and build targeted versions.</p><button className="button button-orange" onClick={signInWithGoogle}><LockKeyhole size={16} />Continue with Google</button></section>
}

function Overview({ document, experiences, selectedIds, setView }) {
  const profile = document.profile || {}
  return <section className="page-grid">
    <div className="hero-panel"><div className="hero-copy"><span className="kicker">MASTER RESUME</span><h2>{profile.name || 'Your story starts here.'}</h2><p>{profile.title || 'Build a strong source of truth, then tailor it in a few clicks.'}</p><button className="button button-orange" onClick={() => setView('profile')}>Edit master profile <ArrowUpRight size={16} /></button></div><div className="hero-lines"><span /><span /><span /></div></div>
    <div className="stats-row"><Stat label="Experiences" value={experiences.length} detail="Reusable entries" /><Stat label="Selected" value={selectedIds.length} detail="For current build" /><Stat label="Projects" value={(document.projects || []).length} detail="In your library" /></div>
    <div className="section-heading"><div><span className="kicker">QUICK START</span><h3>Keep momentum</h3></div><button className="text-button" onClick={() => setView('builder')}>Open builder <ArrowUpRight size={15} /></button></div>
    <div className="action-grid"><ActionCard number="01" title="Polish your profile" text="Make your name, title, and contact details ready for any application." icon={UserRound} onClick={() => setView('profile')} /><ActionCard number="02" title="Curate experience" text="Keep one rich library of work, then select only what matters for a role." icon={BriefcaseBusiness} onClick={() => setView('experience')} /><ActionCard number="03" title="Build a version" text="Choose your strongest entries and export a clean Typst PDF." icon={FileText} onClick={() => setView('builder')} /></div>
  </section>
}

function Stat({ label, value, detail }) { return <div className="stat"><strong>{value}</strong><span>{label}</span><small>{detail}</small></div> }
function ActionCard({ number, title, text, icon: Icon, onClick }) { return <button className="action-card" onClick={onClick}><span className="card-number">{number}</span><span className="action-icon"><Icon size={20} /></span><strong>{title}</strong><p>{text}</p><span className="card-link">Open <ArrowUpRight size={14} /></span></button> }

function Profile({ document, updateProfile }) {
  const profile = document.profile || {}
  return <section className="content-section"><div className="section-heading"><div><span className="kicker">MASTER RESUME / 01</span><h2>Profile details</h2><p className="section-note">This information anchors every version you export.</p></div></div><div className="form-card"><div className="form-grid"><Field label="Full name" value={profile.name} onChange={(value) => updateProfile('name', value)} placeholder="Jordan Lee" /><Field label="Professional title" value={profile.title} onChange={(value) => updateProfile('title', value)} placeholder="Product designer" /><Field label="Email" value={profile.email} onChange={(value) => updateProfile('email', value)} placeholder="jordan@example.com" /><Field label="Phone" value={profile.phone} onChange={(value) => updateProfile('phone', value)} placeholder="(555) 014-2024" /><Field label="Location" value={profile.location} onChange={(value) => updateProfile('location', value)} placeholder="New York, NY" /><Field label="Portfolio or LinkedIn" value={profile.links?.linkedin || ''} onChange={(value) => updateProfile('links', { ...(profile.links || {}), linkedin: value })} placeholder="linkedin.com/in/jordan" /></div></div></section>
}

function Field({ label, value, onChange, placeholder }) { return <label className="field"><span>{label}</span><input value={value || ''} onChange={(event) => onChange(event.target.value)} placeholder={placeholder} /></label> }

function ExperienceList({ experiences, updateExperience, addExperience, removeExperience }) {
  return <section className="content-section"><div className="section-heading"><div><span className="kicker">MASTER RESUME / 02</span><h2>Experience library</h2><p className="section-note">Capture the full version once. Tailor it later.</p></div><button className="button button-orange" onClick={addExperience}><Plus size={16} />Add experience</button></div><div className="experience-stack">{experiences.length === 0 ? <div className="empty-state"><BriefcaseBusiness size={26} /><h3>Your library is ready for its first story.</h3><p>Add a role, project, or meaningful chapter of work.</p></div> : experiences.map((experience, index) => <ExperienceCard key={experience.id} experience={experience} index={index} updateExperience={updateExperience} removeExperience={removeExperience} />)}</div></section>
}

function ExperienceCard({ experience, index, updateExperience, removeExperience }) {
  return <article className="experience-card"><div className="experience-index">0{index + 1}</div><div className="experience-fields"><div className="experience-head"><div><input className="title-input" value={experience.role || ''} onChange={(event) => updateExperience(experience.id, 'role', event.target.value)} placeholder="Role or title" /><input className="company-input" value={experience.company || ''} onChange={(event) => updateExperience(experience.id, 'company', event.target.value)} placeholder="Company" /></div><button className="icon-button danger" title="Delete experience" onClick={() => removeExperience(experience.id)}><Trash2 size={16} /></button></div><div className="mini-grid"><Field label="Dates" value={experience.dates} onChange={(value) => updateExperience(experience.id, 'dates', value)} placeholder="2022 - Present" /><Field label="Location" value={experience.location} onChange={(value) => updateExperience(experience.id, 'location', value)} placeholder="Remote" /></div><label className="field"><span>Impact bullets <small>one per line</small></span><textarea value={(experience.bullets || []).join('\n')} onChange={(event) => updateExperience(experience.id, 'bullets', event.target.value.split('\n'))} placeholder="Describe the outcome, not just the task." /></label></div></article>
}

function Builder({ targetTitle, setTargetTitle, experiences, selectedIds, toggleExperience, selectedExperiences, buildResume }) {
  return <section className="builder-layout"><div className="builder-controls"><div className="section-heading compact"><div><span className="kicker">TARGETED RESUME / 03</span><h2>Choose your angle</h2><p className="section-note">A focused resume beats a crowded one.</p></div></div><label className="field"><span>Target role or version title</span><input value={targetTitle} onChange={(event) => setTargetTitle(event.target.value)} placeholder="Senior product designer" /></label><div className="select-heading"><span>Include in this version</span><small>{selectedIds.length} selected</small></div><div className="select-list">{experiences.length === 0 ? <p className="muted">Add experience entries to start building.</p> : experiences.map((experience) => <label className={`select-experience ${selectedIds.includes(experience.id) ? 'selected' : ''}`} key={experience.id}><input type="checkbox" checked={selectedIds.includes(experience.id)} onChange={() => toggleExperience(experience.id)} /><span className="checkbox-mark"><Check size={13} /></span><span><strong>{experience.role || 'Untitled role'}</strong><small>{experience.company || 'Company pending'}</small></span></label>)}</div><button className="button button-orange full" onClick={buildResume} disabled={selectedExperiences.length === 0}><Download size={16} />Export PDF</button></div><div className="preview-wrap"><div className="preview-label"><span>LIVE PREVIEW</span><span>{selectedExperiences.length} entries</span></div><div className="resume-preview"><div className="resume-header"><h2>{targetTitle || documentTitle(selectedExperiences) || 'Your Name'}</h2><p>Curated resume draft</p><div className="resume-rule" /></div>{selectedExperiences.length === 0 ? <div className="preview-empty"><FileText size={28} /><p>Select experience on the left to see your draft take shape.</p></div> : <div>{selectedExperiences.map((experience) => <div className="preview-experience" key={experience.id}><div><strong>{experience.role || 'Untitled role'}</strong><span>{experience.company || 'Company'}</span></div><time>{experience.dates}</time><ul>{(experience.bullets || []).filter(Boolean).map((bullet, index) => <li key={index}>{bullet}</li>)}</ul></div>)}</div>}</div></div></section>
}

function documentTitle(experiences) { return experiences[0]?.role || '' }

function Connection({ token, setToken, apiUrl, session, onSignIn, onSignOut, onClose, onReload }) { return <div className="modal-backdrop" onMouseDown={onClose}><div className="connection-modal" onMouseDown={(event) => event.stopPropagation()}><div className="modal-top"><div><span className="kicker">WORKSPACE SETTINGS</span><h2>Connection</h2></div><button className="icon-button" onClick={onClose}><X size={17} /></button></div><p className="section-note">The browser starts OAuth. The API validates the resulting session before returning your data.</p><label className="field"><span>API URL</span><input value={apiUrl} readOnly /></label>{session ? <div className="signed-in-state"><Check size={16} /><span>Signed in as {session.user?.email || 'Google user'}</span></div> : <><label className="field"><span>Development bearer token</span><input value={token} onChange={(event) => setToken(event.target.value)} type="password" /></label><p className="section-note">Use the local token only when Supabase OAuth is not configured.</p></>}<div className="modal-actions"><button className="text-button" onClick={onClose}>Close</button>{session ? <button className="button button-dark" onClick={onSignOut}>Sign out</button> : <><button className="text-button" onClick={() => { localStorage.setItem('resume_token', token); onReload(); onClose() }}>Reconnect local</button><button className="button button-dark" onClick={onSignIn}><LockKeyhole size={15} />Google sign in</button></>}</div></div></div> }

window.document.title = 'Resume Studio'

import { createRoot } from 'react-dom/client'
createRoot(window.document.getElementById('root')).render(<App />)
