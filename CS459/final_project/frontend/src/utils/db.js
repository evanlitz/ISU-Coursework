import { DynamoDBClient } from '@aws-sdk/client-dynamodb'
import { DynamoDBDocumentClient, PutCommand, GetCommand, QueryCommand } from '@aws-sdk/lib-dynamodb'
import { fetchAuthSession } from 'aws-amplify/auth'

const REGION = import.meta.env.VITE_AWS_REGION

async function getClient() {
  const session = await fetchAuthSession()
  const dynamo = new DynamoDBClient({
    region: REGION,
    credentials: session.credentials,
  })
  return DynamoDBDocumentClient.from(dynamo)
}

export async function saveFileMetadata(userId, s3Key, filename, exportedKey, iv) {
  const db = await getClient()
  await db.send(new PutCommand({
    TableName: 'FileMetadata',
    Item: { userId, s3Key, filename, exportedKey, iv, sharedWith: [] },
  }))
}

export async function listUserFiles(userId) {
  const db = await getClient()
  const res = await db.send(new QueryCommand({
    TableName: 'FileMetadata',
    KeyConditionExpression: 'userId = :uid',
    ExpressionAttributeValues: { ':uid': userId },
  }))
  return res.Items ?? []
}

export async function registerUser(email, userId) {
  const db = await getClient()
  await db.send(new PutCommand({
    TableName: 'Users',
    Item: { email, userId },
  }))
}

export async function lookupUserByEmail(email) {
  const db = await getClient()
  const res = await db.send(new GetCommand({
    TableName: 'Users',
    Key: { email },
  }))
  return res.Item ?? null
}

export async function shareFile(recipientId, ownerUserId, s3Key, filename, exportedKey, iv) {
  const db = await getClient()
  await db.send(new PutCommand({
    TableName: 'SharedFiles',
    Item: { recipientId, s3Key, ownerUserId, filename, exportedKey, iv },
  }))
}

export async function listSharedWithMe(userId) {
  const db = await getClient()
  const res = await db.send(new QueryCommand({
    TableName: 'SharedFiles',
    KeyConditionExpression: 'recipientId = :uid',
    ExpressionAttributeValues: { ':uid': userId },
  }))
  return res.Items ?? []
}
