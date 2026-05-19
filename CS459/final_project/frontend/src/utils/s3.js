import { S3Client, PutObjectCommand, GetObjectCommand } from '@aws-sdk/client-s3'
import { fetchAuthSession } from 'aws-amplify/auth'

const REGION = import.meta.env.VITE_AWS_REGION
const BUCKET = import.meta.env.VITE_S3_BUCKET

async function getClient() {
  const session = await fetchAuthSession()
  return new S3Client({
    region: REGION,
    credentials: session.credentials,
  })
}

export async function uploadToS3(userId, key, ciphertextBuffer) {
  const client = await getClient()
  await client.send(new PutObjectCommand({
    Bucket: BUCKET,
    Key: `${userId}/${key}`,
    Body: new Uint8Array(ciphertextBuffer),
    ContentType: 'application/octet-stream',
  }))
}

export async function downloadFromS3(userId, key) {
  const client = await getClient()
  const res = await client.send(new GetObjectCommand({
    Bucket: BUCKET,
    Key: `${userId}/${key}`,
  }))
  return new Response(res.Body).arrayBuffer()
}
