import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { api, apiErrorMessage } from '../api/client';

export default function ForgotPassword() {
  const [step, setStep] = useState(1); // 1: email, 2: code & new password
  const [email, setEmail] = useState('');
  const [code, setCode] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  async function handleSendEmail(e) {
    e.preventDefault();
    setError('');
    setMessage('');
    setLoading(true);
    try {
      const { data } = await api.post('/auth/forgot-password/send-email', { email });
      setMessage(data.message || 'Reset code sent successfully.');
      setStep(2);
    } catch (err) {
      setError(apiErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  async function handleResetPassword(e) {
    e.preventDefault();
    setError('');
    setMessage('');
    setLoading(true);
    try {
      const { data } = await api.post('/auth/forgot-password/reset', { email, code, newPassword });
      setMessage(data.message || 'Password reset successfully.');
      setTimeout(() => navigate('/login'), 2000);
    } catch (err) {
      setError(apiErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-md mx-auto px-5 py-16">
      <h1 className="font-display text-3xl mb-6">Reset Password</h1>
      
      {step === 1 && (
        <form onSubmit={handleSendEmail} className="space-y-4">
          <p className="text-sm text-clay mb-4">Enter your registered email address to receive a reset code.</p>
          <div>
            <label className="block text-sm text-clay mb-1">Email address</label>
            <input
              type="email"
              className="w-full border border-marigold-light/60 rounded-lg px-3 py-2 focus-ring"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          {error && <p className="text-red-700 text-sm">{error}</p>}
          {message && <p className="text-tulsi-dark text-sm">{message}</p>}
          <button
            disabled={loading}
            className="w-full py-3 rounded-full bg-tulsi text-ivory font-medium hover:bg-tulsi-dark transition disabled:opacity-60"
          >
            {loading ? 'Sending...' : 'Send Reset Code'}
          </button>
        </form>
      )}

      {step === 2 && (
        <form onSubmit={handleResetPassword} className="space-y-4">
          <p className="text-sm text-clay mb-4">Enter the code sent to {email} and choose a new password.</p>
          <div>
            <label className="block text-sm text-clay mb-1">Reset Code</label>
            <input
              type="text"
              className="w-full border border-marigold-light/60 rounded-lg px-3 py-2 focus-ring"
              value={code}
              onChange={(e) => setCode(e.target.value)}
              required
              maxLength={6}
              placeholder="123456"
            />
          </div>
          <div>
            <label className="block text-sm text-clay mb-1">New Password</label>
            <input
              type="password"
              className="w-full border border-marigold-light/60 rounded-lg px-3 py-2 focus-ring"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              required
            />
          </div>
          {error && <p className="text-red-700 text-sm">{error}</p>}
          {message && <p className="text-tulsi-dark text-sm">{message}</p>}
          <button
            disabled={loading}
            className="w-full py-3 rounded-full bg-tulsi text-ivory font-medium hover:bg-tulsi-dark transition disabled:opacity-60"
          >
            {loading ? 'Resetting...' : 'Reset Password'}
          </button>
        </form>
      )}

      <p className="text-sm text-clay mt-5">
        Remembered your password?{' '}
        <Link to="/login" className="text-marigold-dark font-medium">
          Log in
        </Link>
      </p>
    </div>
  );
}
