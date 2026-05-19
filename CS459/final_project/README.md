# CS459 Final Project — Encrypted S3 File Storage

A secure, encrypted file storage system built on AWS. Files are encrypted client-side with AES-GCM before upload so plaintext data never reaches the cloud. Users authenticate via AWS Cognito, files are stored in S3, and metadata (including encryption keys) is stored in DynamoDB. Users can share files with other registered users.

---

## Architecture Overview

```
Browser (React App)
  │
  ├── AWS Cognito (User Pool + Identity Pool)
  │     └── Authenticates users, issues temporary AWS credentials
  │
  ├── Amazon S3
  │     └── Stores encrypted file ciphertext (never plaintext)
  │
  └── Amazon DynamoDB
        ├── FileMetadata   — encryption keys + file info per user
        ├── SharedFiles    — records of files shared between users
        └── Users          — maps email → Cognito identity ID
```

---

## Security Design

- **Client-side encryption**: Files are encrypted in the browser using the Web Crypto API (AES-GCM, 256-bit key) before being sent to S3. The S3 layer never holds plaintext.
- **Per-file keys**: Each file gets its own randomly generated AES key and IV, stored in DynamoDB tied to the owner's identity.
- **Authentication**: AWS Cognito User Pool handles sign-up, sign-in, email verification, and session management.
- **Authorization**: An IAM role scoped to authenticated Cognito users controls S3 and DynamoDB access. Application-level checks via DynamoDB enforce file sharing permissions.
- **Key storage**: Encryption keys are stored in DynamoDB and are only accessible to authenticated users via the IAM role.

---

## AWS Services Used

| Service | Purpose |
|---|---|
| Cognito User Pool | User sign-up, sign-in, email verification |
| Cognito Identity Pool | Issues temporary IAM credentials to authenticated users |
| S3 | Encrypted file storage |
| DynamoDB | File metadata, encryption keys, user registry, sharing records |
| IAM | Role-based access control for S3 and DynamoDB |

---

## AWS Setup

### 1. Cognito User Pool

- **Sign-in method**: Email
- **MFA**: Disabled
- **Self-registration**: Enabled
- **App client type**: Single-page application (SPA) — no client secret
- **Required attributes**: Email only

Values needed in `.env`:
```
VITE_USER_POOL_ID=us-east-2_XXXXXXXXX
VITE_USER_POOL_CLIENT_ID=XXXXXXXXXXXXXXXXXXXXXXXXXX
```

---

### 2. Cognito Identity Pool

- **Authenticated provider**: linked to the User Pool + App Client above
- **Basic (classic) flow**: Disabled
- **Role**: auto-created authenticated IAM role (edited below)

Values needed in `.env`:
```
VITE_IDENTITY_POOL_ID=us-east-2:XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
```

---

### 3. S3 Bucket

- **Bucket name**: `cs459-encrypted-files-elitzer`
- **Region**: `us-east-2`
- **Public access**: fully blocked
- **Versioning**: disabled
- **Encryption**: SSE-S3 (server-side, in addition to client-side)
- **Object ownership**: ACLs disabled

**CORS policy** (required for browser uploads):
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

Files are stored at path: `{cognitoIdentityId}/{timestamp}_{filename}`

---

### 4. DynamoDB Tables

#### `FileMetadata`
Stores encryption metadata for each uploaded file.

| Attribute | Type | Note |
|---|---|---|
| `userId` | String (PK) | Cognito identity ID of owner |
| `s3Key` | String (SK) | S3 object key (timestamp + filename) |
| `filename` | String | Original filename |
| `exportedKey` | String | Base64-encoded AES-256 key |
| `iv` | String | Base64-encoded AES-GCM IV |
| `sharedWith` | List | Reserved (sharing handled via SharedFiles table) |

#### `Users`
Registry of all users who have logged in. Used to look up recipients when sharing.

| Attribute | Type | Note |
|---|---|---|
| `email` | String (PK) | User's email address |
| `userId` | String | Cognito identity ID |

> Written automatically on every login.

#### `SharedFiles`
Records files that have been shared from one user to another.

| Attribute | Type | Note |
|---|---|---|
| `recipientId` | String (PK) | Cognito identity ID of recipient |
| `s3Key` | String (SK) | S3 object key of the shared file |
| `ownerUserId` | String | Identity ID of the file owner (used to build S3 path) |
| `filename` | String | Display name |
| `exportedKey` | String | Base64 AES key |
| `iv` | String | Base64 IV |

---

### 5. IAM Role

The Cognito Identity Pool auto-creates an authenticated role (`Cognito_cs459identitypoolAuth_Role`). The following inline policy was added to it:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:PutObject", "s3:GetObject", "s3:DeleteObject"],
      "Resource": "arn:aws:s3:::cs459-encrypted-files-elitzer/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:PutItem",
        "dynamodb:GetItem",
        "dynamodb:Query",
        "dynamodb:DeleteItem"
      ],
      "Resource": [
        "arn:aws:dynamodb:us-east-2:865268032810:table/FileMetadata",
        "arn:aws:dynamodb:us-east-2:865268032810:table/SharedFiles",
        "arn:aws:dynamodb:us-east-2:865268032810:table/Users"
      ]
    }
  ]
}
```

---

## Frontend

Built with React + Vite. Key dependencies:

| Package | Purpose |
|---|---|
| `aws-amplify` | Cognito auth integration |
| `@aws-amplify/ui-react` | Pre-built sign-in/sign-up UI |
| `@aws-sdk/client-s3` | S3 upload/download |
| `@aws-sdk/client-dynamodb` | DynamoDB reads/writes |
| `@aws-sdk/lib-dynamodb` | DynamoDB document client (cleaner API) |
| `react-router-dom` | Client-side routing |

### File Structure

```
frontend/src/
  utils/
    crypto.js        — AES-GCM encrypt/decrypt via Web Crypto API
    s3.js            — S3 upload/download using SDK + Cognito credentials
    db.js            — DynamoDB helpers (files, users, sharing)
  components/
    UploadForm.jsx   — File picker, encrypts locally, uploads to S3, saves metadata
    FileList.jsx     — Lists own files and files shared with the user
    DownloadButton.jsx — Fetches from S3, decrypts, triggers browser download
    ShareForm.jsx    — Email input to share a file with another registered user
  pages/
    Dashboard.jsx    — Main view with file list
    Upload.jsx       — Upload page
  App.jsx            — Authenticator wrapper + router + user registration on login
  main.jsx           — Amplify config entry point
```

### Encryption Flow

**Upload:**
1. User picks a file
2. Browser generates a random AES-256-GCM key and 12-byte IV
3. File is encrypted in-browser using the Web Crypto API
4. Ciphertext is uploaded to S3
5. Key, IV, and filename are saved to DynamoDB `FileMetadata`

**Download:**
1. Fetch ciphertext from S3
2. Fetch encryption key + IV from DynamoDB
3. Decrypt in-browser using Web Crypto API
4. Trigger browser file download with plaintext

---

## Environment Variables

All AWS resource identifiers are stored in `frontend/.env` (not committed to git):

```
VITE_USER_POOL_ID=
VITE_USER_POOL_CLIENT_ID=
VITE_IDENTITY_POOL_ID=
VITE_AWS_REGION=
VITE_S3_BUCKET=
```

---

## Running Locally

```bash
cd frontend
npm install
npm run dev
```

App runs at `http://localhost:5173`.

Requires a `.env` file in `frontend/` with the values above filled in.
