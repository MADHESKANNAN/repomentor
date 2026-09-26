import { useState } from 'react'

function App() {
  const [repoUrl, setRepoUrl] = useState('')

  return (
    <div style={{ padding: '40px', fontFamily: 'Arial' }}>
      <h1>RepoMentor</h1>
      <p>AI that understands any GitHub repo</p>
      <input
        type="text"
        placeholder="Paste GitHub repo link"
        value={repoUrl}
        onChange={(e) => setRepoUrl(e.target.value)}
        style={{ padding: '8px', width: '300px' }}
      />
      <button style={{ padding: '8px 16px', marginLeft: '8px' }}>
        Analyze
      </button>
    </div>
  )
}

export default App