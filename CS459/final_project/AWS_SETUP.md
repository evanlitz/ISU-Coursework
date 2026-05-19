# AWS Backend Setup — Step by Step

## Prerequisites
- AWS account with console access
- AWS CLI installed (`aws --version`)
- You are in the `frontend/` directory for any npm commands

---

## Step 1: Create a Cognito User Pool

1. Go to **AWS Console → Cognito → Create user pool**
2. **Sign-in options**: check **Email**
3. **Password policy**: leave defaults (or relax for dev)
4. **MFA**: No MFA (keep it simple for now)
5. **User account recovery**: Email only
6. **Required attributes**: just `email`
7. **Email delivery**: Send email with Cognito (free tier, no SES needed)
8. **App client**:
   - Add an app client — call it `frontend`
   - Auth flows: check **ALLOW_USER_SRP_AUTH** and **ALLOW_REFRESH_TOKEN_AUTH**
   - No client secret (browser apps can't keep secrets)
9. Click **Create user pool**

**Grab these two values and put them in `src/main.jsx`:**

```
userPoolId:       us-east-1_XXXXXXXXX   (shown on the User Pool overview page)
userPoolClientId: XXXXXXXXXXXXXXXXX     (shown under App clients)
```

Replace the placeholders in `frontend/src/main.jsx`:

```js
Amplify.configure({
  Auth: {
    Cognito: {
      userPoolId: 'us-east-1_XXXXXXXXX',
      userPoolClientId: 'XXXXXXXXXXXXXXXXX',
    },
  },
})
```

**Test it**: run `npm run dev`, the Cognito sign-up/sign-in UI should now fully work.

---

## Step 2: Create an S3 Bucket

1. Go to **AWS Console → S3 → Create bucket**
2. **Bucket name**: something like `cs459-encrypted-files-<yourname>`
3. **Region**: same region as your Cognito pool (e.g. `us-east-1`)
4. **Block all public access**: leave all four checkboxes ON — bucket stays private
5. **Versioning**: off for now
6. Click **Create bucket**

### Add a CORS policy (needed for browser uploads)

In your bucket → **Permissions → CORS** → paste:

```json
[
  {
    "AllowedHeaders": ["*"],
    "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
    "AllowedOrigins": ["http://localhost:5173"],
    "ExposeHeaders": ["ETag"]
  }
]
```

> Update `AllowedOrigins` to your production domain before deploying.

---

## Step 3: Create a DynamoDB Table

1. Go to **AWS Console → DynamoDB → Create table**
2. **Table name**: `FileMetadata`
3. **Partition key**: `userId` (String)
4. **Sort key**: `s3Key` (String)
5. Settings: leave as default (on-demand capacity)
6. Click **Create table**

Each item will store:

| Attribute   | Type   | Example                          |
|-------------|--------|----------------------------------|
| `userId`    | String | Cognito sub (unique user ID)     |
| `s3Key`     | String | `1234567890_report.pdf`          |
| `filename`  | String | `report.pdf`                     |
| `exportedKey` | String | base64 AES key                 |
| `iv`        | String | base64 IV                        |
| `sharedWith` | List  | `["user2@email.com"]`            |

---

## Step 4: Create an IAM Role for Authenticated Users

This lets logged-in Cognito users hit S3 and DynamoDB from the browser.

### 4a. Create an Identity Pool

1. Go to **Cognito → Identity pools → Create identity pool**
2. **Authenticated access**: select your User Pool + App Client ID from Step 1
3. **IAM roles**: let Cognito create new roles (it will make `Cognito_<name>Auth_Role`)
4. Click **Create**

**Save the Identity Pool ID** — looks like `us-east-1:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

### 4b. Edit the Authenticated IAM Role

1. Go to **IAM → Roles** → find `Cognito_<name>Auth_Role`
2. Click **Add permissions → Create inline policy**
3. Paste this JSON (replace `BUCKET_NAME` and `ACCOUNT_ID`):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:PutObject", "s3:GetObject", "s3:DeleteObject"],
      "Resource": "arn:aws:s3:::BUCKET_NAME/${cognito-identity.amazonaws.com:sub}/*"
    },
    {
      "Effect": "Allow",
      "Action": ["dynamodb:PutItem", "dynamodb:GetItem", "dynamodb:Query", "dynamodb:DeleteItem"],
      "Resource": "arn:aws:dynamodb:us-east-1:ACCOUNT_ID:table/FileMetadata"
    }
  ]
}
```

> The `${cognito-identity.amazonaws.com:sub}` variable means each user can only touch their own S3 prefix — a key access control feature.

---

## Step 5: Wire the Identity Pool into the Frontend

Update `frontend/src/main.jsx`:

```js
Amplify.configure({
  Auth: {
    Cognito: {
      userPoolId: 'us-east-1_XXXXXXXXX',
      userPoolClientId: 'XXXXXXXXXXXXXXXXX',
      identityPoolId: 'us-east-1:XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX',
    },
  },
})
```

---

## Step 6: Install the AWS SDK and Wire `s3.js`

```bash
npm install @aws-sdk/client-s3 @aws-sdk/credential-providers
```

Replace `src/utils/s3.js` with real calls:

```js
import { S3Client, PutObjectCommand, GetObjectCommand } from '@aws-sdk/client-s3'
import { fromCognitoIdentityPool } from '@aws-sdk/credential-providers'
import { fetchAuthSession } from 'aws-amplify/auth'

const REGION = 'us-east-1'
const BUCKET = 'cs459-encrypted-files-<yourname>'
const IDENTITY_POOL_ID = 'us-east-1:XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX'

async function getClient() {
  const session = await fetchAuthSession()
  const credentials = fromCognitoIdentityPool({
    clientConfig: { region: REGION },
    identityPoolId: IDENTITY_POOL_ID,
    logins: {
      [`cognito-idp.${REGION}.amazonaws.com/${session.userSub}`]: session.tokens.idToken.toString(),
    },
  })
  return new S3Client({ region: REGION, credentials })
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
  return res.Body.transformToArrayBuffer()
}
```

---

## Step 7: Wire `FileMetadata` in DynamoDB

```bash
npm install @aws-sdk/client-dynamodb @aws-sdk/lib-dynamodb
```

Create `src/utils/db.js`:

```js
import { DynamoDBClient } from '@aws-sdk/client-dynamodb'
import { DynamoDBDocumentClient, PutCommand, QueryCommand } from '@aws-sdk/lib-dynamodb'

const client = new DynamoDBClient({ region: 'us-east-1' })
const db = DynamoDBDocumentClient.from(client)

export async function saveFileMetadata(userId, item) {
  await db.send(new PutCommand({
    TableName: 'FileMetadata',
    Item: { userId, ...item },
  }))
}

export async function listUserFiles(userId) {
  const res = await db.send(new QueryCommand({
    TableName: 'FileMetadata',
    KeyConditionExpression: 'userId = :uid',
    ExpressionAttributeValues: { ':uid': userId },
  }))
  return res.Items
}
```

Then in `UploadForm.jsx`, replace the `console.log` with:

```js
import { saveFileMetadata } from '../utils/db'
// after upload:
await saveFileMetadata(user.userId, { s3Key, exportedKey, iv: btoa(...), filename: file.name, sharedWith: [] })
```

And in `FileList.jsx`, replace `MOCK_FILES` with a `useEffect` that calls `listUserFiles(user.userId)`.

---

## Checklist

- [ ] Step 1 — Cognito User Pool created, IDs in `main.jsx`, login works
- [ ] Step 2 — S3 bucket created, CORS set
- [ ] Step 3 — DynamoDB `FileMetadata` table created
- [ ] Step 4 — Identity Pool + IAM role with scoped S3/DynamoDB permissions
- [ ] Step 5 — Identity Pool ID added to Amplify config
- [ ] Step 6 — `s3.js` wired with real SDK calls, upload/download works
- [ ] Step 7 — `db.js` created, FileList pulls real data, UploadForm saves metadata
