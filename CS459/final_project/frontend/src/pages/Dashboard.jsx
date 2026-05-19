import { useState } from 'react'
import { Link } from 'react-router-dom'
import FileList from '../components/FileList'

export default function Dashboard({ user, signOut }) {
  const [refresh, setRefresh] = useState(0)

  return (
    <main style={{ padding: '2rem' }}>
      <h1>Encrypted File Storage</h1>
      <p>Signed in as: <strong>{user?.username}</strong></p>
      <nav style={{ marginBottom: '1rem' }}>
        <Link to="/upload">Upload a file</Link>
        {' | '}
        <button onClick={signOut}>Sign out</button>
      </nav>
      <FileList refreshTrigger={refresh} />
    </main>
  )
}
