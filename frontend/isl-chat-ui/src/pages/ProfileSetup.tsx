import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import '../styles/ProfileSetup.css';

function ProfileSetup() {
  const { updateUserProfile } = useAuth();
  const navigate = useNavigate();
  const [displayName, setDisplayName] = useState('');
  const [bio, setBio] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    if (!displayName.trim()) {
      setError('Display name is required');
      setLoading(false);
      return;
    }

    try {
      await updateUserProfile(displayName, bio);
      navigate('/chats');
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  const handleSkip = () => {
    navigate('/chats');
  };

  return (
    <div className="profile-setup-container">
      <div className="profile-setup-card">
        <div className="profile-setup-header">
          <h1>✨ Welcome to ISL Chat!</h1>
          <p>Let's set up your profile</p>
        </div>

        <form onSubmit={handleSubmit} className="profile-setup-form">
          <div className="input-group">
            <label htmlFor="displayName">Display Name *</label>
            <input
              id="displayName"
              type="text"
              placeholder="Your name"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              required
              maxLength={50}
              autoFocus
            />
          </div>

          <div className="input-group">
            <label htmlFor="bio">Bio (Optional)</label>
            <textarea
              id="bio"
              placeholder="Tell us about yourself"
              value={bio}
              onChange={(e) => setBio(e.target.value)}
              maxLength={200}
              rows={3}
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <button type="submit" disabled={loading} className="btn-primary">
            {loading ? 'Saving...' : 'Complete Setup'}
          </button>

          <button
            type="button"
            onClick={handleSkip}
            className="btn-secondary"
            disabled={loading}
          >
            Skip for Now
          </button>
        </form>
      </div>
    </div>
  );
}

export default ProfileSetup;
