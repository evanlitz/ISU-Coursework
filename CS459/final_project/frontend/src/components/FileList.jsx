import { useEffect, useState } from 'react'
import { useAuthenticator } from '@aws-amplify/ui-react'
import { listUserFiles, listSharedWithMe } from '../utils/db'
import DownloadButton from './DownloadButton'
import ShareForm from './ShareForm'

export default function FileList({ refreshTrigger }) {
  const { user } = useAuthenticator()
  const [ownFiles, setOwnFiles] = useState([])
  const [sharedFiles, setSharedFiles] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function load() {
      setLoading(true)
      const [own, shared] = await Promise.all([
        listUserFiles(user.userId),
        listSharedWithMe(user.userId),
      ])
      setOwnFiles(own)
      setSharedFiles(shared)
      setLoading(false)
    }
    load()
  }, [user.userId, refreshTrigger])

  if (loading) return <p>Loading files...</p>

  return (
    <div>
      <h2>Your Files</h2>
      {ownFiles.length === 0 ? (
        <p>No files uploaded yet.</p>
      ) : (
        <ul>
          {ownFiles.map(f => (
            <li key={f.s3Key} style={{ marginBottom: '1rem' }}>
              <strong>{f.filename}</strong>
              {' — '}
              <DownloadButton s3Key={f.s3Key} exportedKey={f.exportedKey} iv={f.iv} filename={f.filename} userId={user.userId} />
              <br />
              <ShareForm file={f} ownerUserId={user.userId} />
            </li>
          ))}
        </ul>
      )}

      <h2>Shared with You</h2>
      {sharedFiles.length === 0 ? (
        <p>Nothing shared with you yet.</p>
      ) : (
        <ul>
          {sharedFiles.map(f => (
            <li key={f.s3Key}>
              <strong>{f.filename}</strong>
              {' — '}
              <DownloadButton s3Key={f.s3Key} exportedKey={f.exportedKey} iv={f.iv} filename={f.filename} userId={f.ownerUserId} />
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
