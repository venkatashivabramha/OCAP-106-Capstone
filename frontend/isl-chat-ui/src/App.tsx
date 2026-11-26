import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Login from './pages/Login';
import ProfileSetup from './pages/ProfileSetup';
import ChatList from './pages/ChatList';
import ChatWindow from './pages/ChatWindow';
import CreateGroup from './pages/CreateGroup';
import './App.css';

function AppRoutes() {
  const { isAuthenticated, loading, login, logout } = useAuth();

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center', 
        height: '100vh',
        fontSize: '20px'
      }}>
        Loading...
      </div>
    );
  }

  return (
    <Routes>
      <Route 
        path="/login" 
        element={
          isAuthenticated ? 
          <Navigate to="/chats" replace /> : 
          <Login onLogin={(userData) => {
            login(userData);
            // Handle new user redirect in Login component
          }} />
        } 
      />
      <Route 
        path="/profile-setup" 
        element={
          isAuthenticated ? 
          <ProfileSetup /> : 
          <Navigate to="/login" replace />
        } 
      />
      <Route 
        path="/chats" 
        element={
          isAuthenticated ? 
          <ChatList onLogout={logout} /> : 
          <Navigate to="/login" replace />
        } 
      />
      <Route 
        path="/chat/:conversationId" 
        element={
          isAuthenticated ? 
          <ChatWindow /> : 
          <Navigate to="/login" replace />
        } 
      />
      <Route 
        path="/create-group" 
        element={
          isAuthenticated ? 
          <CreateGroup /> : 
          <Navigate to="/login" replace />
        } 
      />
      <Route path="/" element={<Navigate to="/chats" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <div className="App">
          <AppRoutes />
        </div>
      </AuthProvider>
    </Router>
  );
}

export default App;
