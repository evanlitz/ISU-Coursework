import { decryptFile } from '../utils/crypto'
import { downloadFromS3 } from '../utils/s3'

export default function DownloadButton({ s3Key, exportedKey, iv, filename, userId }) {
  async function handleDownload() {
    const ciphertext = await downloadFromS3(userId, s3Key)
    const ivBytes = Uint8Array.from(atob(iv), c => c.charCodeAt(0))
    const plaintext = await decryptFile(ciphertext, exportedKey, ivBytes)

    const url = URL.createObjectURL(new Blob([plaintext]))
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    a.click()
    URL.revokeObjectURL(url)
  }

  return <button onClick={handleDownload}>Download</button>
}
