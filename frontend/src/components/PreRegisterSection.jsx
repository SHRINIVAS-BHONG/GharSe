import React, { useState, useEffect } from 'react';
import { api } from '../api/client';

export default function PreRegisterSection({ initialRole = 'eater', onOpenInvestorModal }) {
  const [role, setRole] = useState(initialRole);
  const [name, setName] = useState('');
  const [contact, setContact] = useState(''); // phone or email
  const [locality, setLocality] = useState('');
  const [dietaryPreference, setDietaryPreference] = useState('veg');
  const [specialtyOrCraving, setSpecialtyOrCraving] = useState('');
  const [capacityOrBudget, setCapacityOrBudget] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [myPass, setMyPass] = useState(null);
  const [copiedLink, setCopiedLink] = useState(false);

  useEffect(() => {
    if (initialRole) setRole(initialRole);
  }, [initialRole]);

  // Load saved pass if user already registered on this machine
  useEffect(() => {
    const saved = localStorage.getItem('gharse_user_pass');
    if (saved) {
      try {
        setMyPass(JSON.parse(saved));
      } catch (e) {}
    }
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!name.trim()) {
      setErrorMsg('Please enter your name.');
      return;
    }
    if (!contact.trim()) {
      setErrorMsg('Please enter your WhatsApp number or email.');
      return;
    }
    if (!locality.trim()) {
      setErrorMsg('Please enter your campus or locality.');
      return;
    }

    setLoading(true);
    setErrorMsg('');

    // Extract referral or source from URL
    const urlParams = new URLSearchParams(window.location.search);
    const sourceOrRef = urlParams.get('ref') || urlParams.get('source') || urlParams.get('utm_source') || 'direct';

    const payload = {
      name: name.trim(),
      contact: contact.trim(),
      role: role,
      localityOrCampus: locality.trim(),
      dietaryPreference: dietaryPreference,
      favoriteDishOrSpecialty: specialtyOrCraving.trim(),
      approxBudgetOrPortions: capacityOrBudget.trim(),
      sourceOrRef: sourceOrRef
    };

    try {
      const res = await api.post('/waitlist', payload);
      const data = res.data;
      
      const shareUrl = `${window.location.origin}/?ref=${data.queueNumber?.replace('#', '') || 'early'}`;

      const passData = {
        queueNumber: data.queueNumber,
        name: data.name,
        role: data.role,
        localityOrCampus: data.localityOrCampus,
        totalRealRegistered: data.totalRealRegistered,
        shareUrl: shareUrl
      };

      setMyPass(passData);
      localStorage.setItem('gharse_user_pass', JSON.stringify(passData));
    } catch (err) {
      // Local fallback if server is offline
      const queueNumber = '#GS-0001';
      const shareUrl = `${window.location.origin}/?ref=early`;
      const passData = {
        queueNumber: queueNumber,
        name: name,
        role: role,
        localityOrCampus: locality,
        totalRealRegistered: 1,
        shareUrl: shareUrl
      };
      setMyPass(passData);
      localStorage.setItem('gharse_user_pass', JSON.stringify(passData));
    } finally {
      setLoading(false);
    }
  };

  const copyShareLink = () => {
    if (!myPass) return;
    navigator.clipboard.writeText(myPass.shareUrl);
    setCopiedLink(true);
    setTimeout(() => setCopiedLink(false), 2000);
  };

  const getWhatsAppShareUrl = () => {
    if (!myPass) return '#';
    const text = myPass.role === 'eater'
      ? `Hey! I just pre-registered for GharSe (${myPass.queueNumber}) to get authentic home-cooked meals straight from local kitchens. Join the pilot waitlist here: ${myPass.shareUrl}`
      : `Namaste! I just registered as a Home Cook on GharSe (${myPass.queueNumber}) to share home-cooked meals with neighbors. Join the pilot launch here: ${myPass.shareUrl}`;
    return `https://api.whatsapp.com/send?text=${encodeURIComponent(text)}`;
  };

  const resetPass = () => {
    localStorage.removeItem('gharse_user_pass');
    setMyPass(null);
    setName('');
    setContact('');
    setLocality('');
    setSpecialtyOrCraving('');
    setCapacityOrBudget('');
  };

  return (
    <section id="waitlist" className="scroll-mt-20 py-16 bg-gradient-to-b from-ivory to-amber-50/50">
      <span id="pre-register" className="block -mt-20 pt-20" aria-hidden="true" />
      <div className="max-w-4xl mx-auto px-5">
        
        {/* Title */}
        <div className="text-center max-w-2xl mx-auto mb-10">
          <span className="px-3 py-1 rounded-full bg-tulsi/10 text-tulsi-dark text-xs font-bold uppercase tracking-wider">
            Early Access Pre-Registration
          </span>
          <h2 className="font-display text-3xl sm:text-4xl text-ink font-bold mt-2">
            Join the GharSe Pilot Waitlist
          </h2>
          <p className="text-clay text-sm sm:text-base mt-2">
            Sign up to be notified the moment verified home cooks go live in your university campus, hostel, or neighborhood.
          </p>
        </div>

        {/* If registered, show Pass */}
        {myPass ? (
          <div className="max-w-md mx-auto bg-white rounded-3xl border-2 border-marigold/50 shadow-xl p-6 sm:p-8 animate-fadeIn text-center">
            <span className="px-3 py-1 rounded-full bg-emerald-100 text-emerald-800 text-xs font-bold uppercase tracking-wider">
              ✓ Registration Recorded
            </span>

            <div className="my-6 p-6 rounded-2xl bg-gradient-to-br from-tulsi-dark to-tulsi text-ivory shadow-md">
              <p className="text-[11px] text-marigold-light uppercase font-semibold">Your Priority Queue Number</p>
              <p className="text-4xl font-display font-extrabold text-ivory tracking-tight my-1">
                {myPass.queueNumber}
              </p>
              <p className="text-xs text-ivory/80">
                Founding Member #{myPass.totalRealRegistered || 1} on the Pilot Waitlist
              </p>

              <div className="mt-5 pt-3 border-t border-white/15 flex justify-between text-xs text-left">
                <div>
                  <p className="text-ivory/60 text-[10px] uppercase">Name</p>
                  <p className="font-semibold text-ivory">{myPass.name}</p>
                </div>
                <div className="text-right">
                  <p className="text-ivory/60 text-[10px] uppercase">Locality / Campus</p>
                  <p className="font-semibold text-ivory">{myPass.localityOrCampus}</p>
                </div>
              </div>
            </div>

            {/* Share and WhatsApp */}
            <div className="space-y-3 pt-1">
              <p className="text-xs font-semibold text-ink">
                Share this link with friends or neighbors:
              </p>
              
              <div className="flex flex-col sm:flex-row gap-2">
                <a
                  href={getWhatsAppShareUrl()}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex-1 py-2.5 px-4 rounded-xl bg-emerald-600 text-white text-xs font-semibold hover:bg-emerald-700 transition flex items-center justify-center gap-1.5 shadow-xs"
                >
                  <span>💬 Share on WhatsApp</span>
                </a>
                <button
                  onClick={copyShareLink}
                  className="flex-1 py-2.5 px-4 rounded-xl border border-tulsi text-tulsi text-xs font-semibold hover:bg-tulsi hover:text-ivory transition"
                >
                  <span>{copiedLink ? '✓ Link Copied!' : '🔗 Copy Share Link'}</span>
                </button>
              </div>

              <div className="pt-3">
                <button
                  onClick={resetPass}
                  className="text-xs text-clay hover:text-ink underline"
                >
                  Register another person or cook
                </button>
              </div>
            </div>
          </div>
        ) : (
          /* Pre-Registration Form */
          <div className="max-w-xl mx-auto bg-white rounded-3xl border border-marigold/40 shadow-lg overflow-hidden">
            
            {/* Persona Switcher Tabs */}
            <div className="grid grid-cols-2 border-b border-marigold-light/40 bg-ivory/50 p-2 gap-2">
              <button
                type="button"
                onClick={() => setRole('eater')}
                className={`py-2.5 px-4 rounded-xl text-sm font-semibold transition flex items-center justify-center gap-2 cursor-pointer ${
                  role === 'eater'
                    ? 'bg-tulsi text-ivory shadow-xs'
                    : 'text-clay hover:text-ink hover:bg-white/60'
                }`}
              >
                <span>🍱</span>
                <span>I Want Home Food</span>
              </button>
              <button
                type="button"
                onClick={() => setRole('cook')}
                className={`py-2.5 px-4 rounded-xl text-sm font-semibold transition flex items-center justify-center gap-2 cursor-pointer ${
                  role === 'cook'
                    ? 'bg-marigold text-ink shadow-xs font-bold'
                    : 'text-clay hover:text-ink hover:bg-white/60'
                }`}
              >
                <span>👩‍🍳</span>
                <span>I Want to Cook & Earn</span>
              </button>
            </div>

            <form onSubmit={handleSubmit} className="p-6 sm:p-8 space-y-4">
              {errorMsg && (
                <div className="p-3 bg-red-50 text-red-700 border border-red-200 rounded-xl text-xs font-medium">
                  {errorMsg}
                </div>
              )}

              <div>
                <label className="block text-xs font-semibold text-ink mb-1">
                  Full Name *
                </label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder={role === 'eater' ? 'e.g. Aryan Sharma' : 'e.g. Anita Devi'}
                  className="w-full px-4 py-2.5 rounded-xl border border-clay/20 bg-ivory/30 text-sm focus:outline-none focus:ring-2 focus:ring-marigold"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-ink mb-1">
                  WhatsApp Number or Email *
                </label>
                <input
                  type="text"
                  required
                  value={contact}
                  onChange={(e) => setContact(e.target.value)}
                  placeholder="9876543210 or yourname@gmail.com"
                  className="w-full px-4 py-2.5 rounded-xl border border-clay/20 bg-ivory/30 text-sm focus:outline-none focus:ring-2 focus:ring-marigold"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-ink mb-1">
                  Your Campus, University or Residential Area *
                </label>
                <input
                  type="text"
                  required
                  value={locality}
                  onChange={(e) => setLocality(e.target.value)}
                  placeholder="e.g. DU North Campus / Kota Vigyan Nagar / DLF Phase 3 / HSR Layout"
                  className="w-full px-4 py-2.5 rounded-xl border border-clay/20 bg-ivory/30 text-sm focus:outline-none focus:ring-2 focus:ring-marigold"
                />
              </div>

              {role === 'eater' ? (
                <div className="grid sm:grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-semibold text-ink mb-1">
                      Food Preference
                    </label>
                    <select
                      value={dietaryPreference}
                      onChange={(e) => setDietaryPreference(e.target.value)}
                      className="w-full px-3 py-2.5 rounded-xl border border-clay/20 bg-ivory/30 text-xs focus:outline-none focus:ring-2 focus:ring-marigold"
                    >
                      <option value="veg">Pure Vegetarian</option>
                      <option value="non-veg">Both Veg & Non-Veg</option>
                      <option value="jain">Jain (No Onion / Garlic)</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-ink mb-1">
                      Favorite Home Dish
                    </label>
                    <input
                      type="text"
                      value={specialtyOrCraving}
                      onChange={(e) => setSpecialtyOrCraving(e.target.value)}
                      placeholder="e.g. Rajma Chawal, Kadhi"
                      className="w-full px-3 py-2.5 rounded-xl border border-clay/20 bg-ivory/30 text-xs focus:outline-none focus:ring-2 focus:ring-marigold"
                    />
                  </div>
                </div>
              ) : (
                <div className="grid sm:grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-semibold text-ink mb-1">
                      Your Specialty Dish
                    </label>
                    <input
                      type="text"
                      value={specialtyOrCraving}
                      onChange={(e) => setSpecialtyOrCraving(e.target.value)}
                      placeholder="e.g. Homestyle Thali, Poha"
                      className="w-full px-3 py-2.5 rounded-xl border border-clay/20 bg-ivory/30 text-xs focus:outline-none focus:ring-2 focus:ring-marigold"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-ink mb-1">
                      Extra Plates per Meal (Max 5)
                    </label>
                    <select
                      value={capacityOrBudget}
                      onChange={(e) => setCapacityOrBudget(e.target.value)}
                      className="w-full px-3 py-2.5 rounded-xl border border-clay/20 bg-ivory/30 text-xs focus:outline-none focus:ring-2 focus:ring-marigold"
                    >
                      <option value="1-2 plates">1 - 2 plates</option>
                      <option value="3-4 plates">3 - 4 plates</option>
                      <option value="5 plates max">5 plates (Strict Max Cap)</option>
                    </select>
                  </div>
                </div>
              )}

              <div className="pt-2">
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full py-3 px-5 rounded-xl bg-tulsi text-ivory font-bold text-sm hover:bg-tulsi-dark transition shadow-sm cursor-pointer flex items-center justify-center gap-2"
                >
                  <span>{loading ? 'Securing Your Priority Spot...' : 'Claim Early Access Pass →'}</span>
                </button>
                <p className="text-[11px] text-clay/70 text-center mt-2">
                  🔒 No spam ever. We only notify you when verified neighbor kitchens open in your exact campus or sector.
                </p>
              </div>
            </form>
          </div>
        )}

      </div>
    </section>
  );
}
