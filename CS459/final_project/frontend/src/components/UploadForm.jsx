import { useState } from 'react'
import { encryptFile } from '../utils/crypto'
import { uploadToS3 } from '../utils/s3'
import { saveFileMetadata } from '../utils/db'
import { useAuthenticator } from '@aws-amplify/ui-react'

export default function UploadForm({ onUploadComplete }) {
  const { user } = useAuthenticator()
  const [status, setStatus] = useState('')

  async function handleUpload(e) {
    e.preventDefault()
    const file = e.target.file.files[0]
    if (!file) return

    setStatus('Encrypting...')
    const { ciphertext, exportedKey, iv } = await encryptFile(file)

    const s3Key = `${Date.now()}_${file.name}`
    const userId = user.userId
    const ivB64 = btoa(String.fromCharCode(...iv))

    setStatus('Uploading...')
    await uploadToS3(userId, s3Key, ciphertext)

    setStatus('Saving metadata...')
    await saveFileMetadata(userId, s3Key, file.name, exportedKey, ivB64)

    setStatus(`Done! Uploaded "${file.name}"`)
    e.target.reset()
    if (onUploadComplete) onUploadComplete()
  }

  return (
    <form onSubmit={handleUpload}>
      <h2>Upload File</h2>
      <input type="file" name="file" required />
      <button type="submit">Encrypt &amp; Upload</button>
      {status && <p>{status}</p>}
    </form>
  )
}
