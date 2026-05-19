import { useEffect } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Authenticator } from '@aws-amplify/ui-react'
import { fetchUserAttributes } from 'aws-amplify/auth'
import { registerUser } from './utils/db'
import Dashboard from './pages/Dashboard'
import Upload from './pages/Upload'

function AuthenticatedApp({ user, signOut }) {
  useEffect(() => {
    async function register() {
      const attrs = await fetchUserAttributes()
      await registerUser(attrs.email, user.userId)
    }
    register()
  }, [user.userId])

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard user={user} signOut={signOut} />} />
        <Route path="/upload" element={<Upload />} />
      </Routes>
    </BrowserRouter>
  )
}

export default function App() {
  return (
    <Authenticator>
      {({ signOut, user }) => <AuthenticatedApp user={user} signOut={signOut} />}
    </Authenticator>
  )
}
