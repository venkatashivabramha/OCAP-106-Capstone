import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { sendOTP, verifyOTP } from '../services/api';
import '../styles/Login.css';

interface LoginProps {
  onLogin: (userData: any) => void;
}

function Login({ onLogin }: LoginProps) {
  const navigate = useNavigate();
  const [step, setStep] = useState<'phone' | 'otp'>('phone');
  const [phoneNumber, setPhoneNumber] = useState('');
  const [otpCode, setOTPCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [simulationMode, setSimulationMode] = useState(false);

  const handleSendOTP = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setMessage('');
    setLoading(true);

    try {
      // Auto-add +91 if not present
      let formattedPhone = phoneNumber.trim();
      if (!formattedPhone.startsWith('+')) {
        formattedPhone = '+91' + formattedPhone.replace(/^\+?91?/, '');
      }
      
      const response = await sendOTP(formattedPhone);
      setPhoneNumber(formattedPhone);
      setMessage(response.message || 'OTP sent successfully!');
      setSimulationMode(response.simulation || false);
      
      if (response.simulation) {
        setMessage('🔧 Simulation Mode: Use OTP 123456');
      }
      
      setStep('otp');
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to send OTP');
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOTP = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await verifyOTP(phoneNumber, otpCode);
      
      // Save tokens and user data
      localStorage.setItem('access_token', response.access_token);
      localStorage.setItem('refresh_token', response.refresh_token);
      
      const userData = {
        id: response.user_id,
        username: response.username,
        phone_number: response.phone_number,
      };
      
      localStorage.setItem('user', JSON.stringify(userData));
      
      setMessage('✅ Login successful!');
      
      // Pass user data to parent (AuthContext)
      onLogin(userData);
      
      // Redirect based on user status
      setTimeout(() => {
        if (response.is_new_user) {
          navigate('/profile-setup');
        } else {
          navigate('/chats');
        }
      }, 1000);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Invalid OTP');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <h1>🤟 ISL Chat</h1>
          <p>Indian Sign Language Chat</p>
        </div>

        {step === 'phone' && (
          <form onSubmit={handleSendOTP} className="login-form">
            <h2>Enter Your Mobile Number</h2>
            <p className="subtitle">We'll send you an OTP to verify</p>
            
            <div className="input-group">
              <input
                type="tel"
                placeholder="9876543210 or +919876543210"
                value={phoneNumber}
                onChange={(e) => setPhoneNumber(e.target.value)}
                required
                minLength={10}
                title="Enter Indian mobile number (with or without +91)"
              />
            </div>

            {error && <div className="error-message">{error}</div>}
            {message && <div className="success-message">{message}</div>}
            
            <button type="submit" disabled={loading} className="btn-primary">
              {loading ? 'Sending...' : 'Send OTP'}
            </button>

            <div className="demo-note">
              <strong>🔧 Simulation Mode</strong><br/>
              Firebase credentials not configured yet.<br/>
              Use OTP: <code>123456</code> for testing
            </div>
          </form>
        )}

        {step === 'otp' && (
          <form onSubmit={handleVerifyOTP} className="login-form">
            <h2>Enter OTP</h2>
            <p className="subtitle">Sent to {phoneNumber}</p>
            
            <div className="input-group">
              <input
                type="text"
                placeholder="Enter 6-digit OTP"
                value={otpCode}
                onChange={(e) => setOTPCode(e.target.value)}
                required
                maxLength={6}
                pattern="[0-9]{6}"
                autoFocus
              />
            </div>

            {error && <div className="error-message">{error}</div>}
            {message && <div className="success-message">{message}</div>}
            
            <button type="submit" disabled={loading} className="btn-primary">
              {loading ? 'Verifying...' : 'Verify & Login'}
            </button>

            <button
              type="button"
              onClick={() => {
                setStep('phone');
                setOTPCode('');
                setError('');
                setMessage('');
              }}
              className="btn-secondary"
            >
              Change Number
            </button>

            {simulationMode && (
              <div className="demo-note">
                🔧 Simulation Mode: Use OTP <code>123456</code>
              </div>
            )}
          </form>
        )}
      </div>
    </div>
  );
}

export default Login;
