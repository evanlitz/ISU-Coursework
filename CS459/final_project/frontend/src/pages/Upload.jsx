import { Link } from 'react-router-dom'
import UploadForm from '../components/UploadForm'

export default function Upload() {
  return (
    <main style={{ padding: '2rem' }}>
      <h1>Upload File</h1>
      <Link to="/">&larr; Back to files</Link>
      <div style={{ marginTop: '1rem' }}>
        <UploadForm />
      </div>
    </main>
  )
}
