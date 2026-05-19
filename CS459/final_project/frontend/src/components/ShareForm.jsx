import { useState } from 'react'
import { lookupUserByEmail, shareFile } from '../utils/db'

export default function ShareForm({ file, ownerUserId }) {
  const [email, setEmail] = useState('')
  const [status, setStatus] = useState('')

  async function handleShare(e) {
    e.preventDefault()
    setStatus('Looking up user...')

    const recipient = await lookupUserByEmail(email.trim().toLowerCase())
    if (!recipient) {
      setStatus('User not found — they must log in at least once first.')
      return
    }
    if (recipient.userId === ownerUserId) {
      setStatus('That is you.')
      return
    }

    setStatus('Sharing...')
    await shareFile(recipient.userId, ownerUserId, file.s3Key, file.filename, file.exportedKey, file.iv)
    setStatus(`Shared with ${email}`)
    setEmail('')
  }

  return (
    <form onSubmit={handleShare} style={{ display: 'inline-flex', gap: '0.5rem', marginTop: '0.25rem' }}>
      <input
        type="email"
        placeholder="Recipient email"
        value={email}
        onChange={e => setEmail(e.target.value)}
        required
      />
      <button type="submit">Share</button>
      {status && <span>{status}</span>}
    </form>
  )
}
