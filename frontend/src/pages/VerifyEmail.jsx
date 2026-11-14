import { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { api, apiErrorMessage } from '../api/client';
import { useAuth } from '../context/AuthContext';

export default function VerifyEmail() {
  const [searchParams] = useSearchParams();
  const initialCode = searchParams.get('code') || '';
  const [code, setCode] = useState(initialCode);
  const [serverOtp, setServerOtp] = useState('');
  const [error, setError] = useState('');
  const [message, setMessage] = useState(initialCode ? 'Verification code received and pre-filled!' : '');
  const [loading, setLoading] = useState(false);
  const [resending, setResending] = useState(false);
  
  const navigate = useNavigate();
  const { login } = useAuth();
  
  const email = searchParams.get('email');

  useEffect(() => {
    if (!email) {
      navigate('/login');
      return;
    }

    // Attempt to fetch active OTP if not already in input
    if (!initialCode) {
      api.get(`/auth/get-otp?email=${encodeURIComponent(email)}`)
        .then((res) => {
          if (res.data?.code) {
            setServerOtp(res.data.code);
          }
        })
        .catch(() => {});
    }
  }, [email, initialCode, navigate]);

  async function handleVerify(e) {
    e.preventDefault();
    setError('');
    setMessage('');
    setLoading(true);

    try {
      const { data } = await api.post('/auth/verify-email', { email, code });
      login(data.token, data.user, data.sellerProfile);
      if (data.user.role === 'seller') navigate('/seller/dashboard');
      else if (data.user.role === 'admin') navigate('/admin');
      else navigate('/browse');
    } catch (err) {
      setError(apiErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  async function handleResend() {
    setError('');
    setMessage('');
    setResending(true);
    
    try {
      const { data } = await api.post('/auth/resend-verification', { email });
      if (data.code) {
        setCode(data.code);
        setServerOtp(data.code);
        setMessage(`New code generated: ${data.code} (auto-filled below)`);
      } else {
        setMessage(data.message || 'Verification code resent successfully.');
      }
    } catch (err) {
      setError(apiErrorMessage(err));
    } finally {
      setResending(false);
    }
  }

  return (
    <div className="max-w-md mx-auto px-5 py-16">
      <h1 className="font-display text-3xl mb-2">Verify Your Email</h1>
      <p className="text-clay mb-6">
        We sent a 6-digit verification code to <strong>{email}</strong>.
      </p>
      
      <form onSubmit={handleVerify} className="space-y-4">
        <div>
          <label className="block text-sm text-clay mb-1">Verification Code</label>
          <input
            type="text"
            className="w-full border border-marigold-light/60 rounded-lg px-3 py-2 focus-ring text-center tracking-widest text-lg font-mono"
            value={code}
            onChange={(e) => setCode(e.target.value)}
            required
            maxLength={6}
            placeholder="123456"
          />
        </div>

        {serverOtp && !code && (
          <div className="p-3 bg-amber-50/90 border border-amber-200 rounded-xl text-xs text-amber-900 flex items-center justify-between">
            <span>Direct OTP preview: <strong className="font-mono text-sm tracking-wider text-tulsi-dark">{serverOtp}</strong></span>
            <button
              type="button"
              onClick={() => setCode(serverOtp)}
              className="px-2.5 py-1 bg-marigold rounded-full font-semibold text-ink hover:bg-marigold-dark transition text-xs cursor-pointer"
            >
              Fill Code
            </button>
          </div>
        )}
        
        {error && <p className="text-red-700 text-sm">{error}</p>}
        {message && <p className="text-tulsi-dark text-sm">{message}</p>}
        
        <button
          disabled={loading}
          className="w-full py-3 rounded-full bg-marigold text-ink font-medium hover:bg-marigold-dark transition disabled:opacity-60"
        >
          {loading ? 'Verifying...' : 'Verify Email'}
        </button>
      </form>

      <div className="mt-6 text-center">
        <p className="text-sm text-clay">
          Didn't receive the code?{' '}
          <button 
            onClick={handleResend}
            disabled={resending}
            className="text-marigold-dark font-medium hover:underline disabled:opacity-50"
          >
            {resending ? 'Sending...' : 'Resend Code'}
          </button>
        </p>
      </div>
    </div>
  );
}
