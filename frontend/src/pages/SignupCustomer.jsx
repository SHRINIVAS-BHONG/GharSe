import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { api, apiErrorMessage } from '../api/client';
import { useAuth } from '../context/AuthContext';

export default function SignupCustomer() {
  const [form, setForm] = useState({ name: '', email: '', password: '', locality: '', foodPreferences: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  function update(field, value) {
    setForm((f) => ({ ...f, [field]: value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    setLoading(true);

    let approximateLocation = null;
    if (navigator.geolocation) {
      try {
        const pos = await new Promise((resolve, reject) => {
          navigator.geolocation.getCurrentPosition(resolve, reject, { timeout: 5000 });
        });
        approximateLocation = { lat: pos.coords.latitude, lng: pos.coords.longitude };
      } catch (err) {
        console.warn('Geolocation failed or denied', err);
      }
    }

    try {
      const { data } = await api.post('/auth/register', {
        name: form.name,
        email: form.email,
        password: form.password,
        role: 'customer',
        locality: form.locality,
        foodPreferences: form.foodPreferences ? form.foodPreferences.split(',').map((s) => s.trim()) : [],
        approximateLocation
      });
      navigate(`/verify-email?email=${encodeURIComponent(data.email || form.email)}`);
    } catch (err) {
      setError(apiErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-md mx-auto px-5 py-16">
      <h1 className="font-display text-3xl mb-2">Join GharSe</h1>
      <p className="text-clay mb-6">Discover home-cooked meals from cooks near you.</p>
      <form onSubmit={handleSubmit} className="space-y-4">
        <Field label="Name" value={form.name} onChange={(v) => update('name', v)} required />
        <Field label="Email" type="email" value={form.email} onChange={(v) => update('email', v)} required />
        <Field label="Password" type="password" value={form.password} onChange={(v) => update('password', v)} required />
        <Field label="Locality" value={form.locality} onChange={(v) => update('locality', v)} placeholder="e.g. Sector 14, Rewari" />
        <Field
          label="Food preferences (optional)"
          value={form.foodPreferences}
          onChange={(v) => update('foodPreferences', v)}
          placeholder="e.g. vegetarian, spicy"
        />
        {error && <p className="text-red-700 text-sm">{error}</p>}
        <button
          disabled={loading}
          className="w-full py-3 rounded-full bg-marigold text-ink font-medium hover:bg-marigold-dark hover:text-ivory transition disabled:opacity-60"
        >
          {loading ? 'Creating account...' : 'Create account'}
        </button>
      </form>
      <p className="text-sm text-clay mt-5">
        Already have an account? <Link to="/login" className="text-marigold-dark font-medium">Log in</Link>
      </p>
    </div>
  );
}

function Field({ label, value, onChange, type = 'text', required, placeholder }) {
  return (
    <div>
      <label className="block text-sm text-clay mb-1">{label}</label>
      <input
        type={type}
        className="w-full border border-marigold-light/60 rounded-lg px-3 py-2 focus-ring"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        required={required}
        placeholder={placeholder}
      />
    </div>
  );
}
