import React, { useState, useEffect } from 'react';
import { api } from '../api/client';

export default function InvestorProofModal({ isOpen, onClose }) {
  const [stats, setStats] = useState({
    totalRegistrations: 0,
    totalClicks: 0,
    conversionRate: '0.0%',
    eatersCount: 0,
    cooksCount: 0,
    recentEntries: []
  });
  const [loading, setLoading] = useState(false);
  const [serverOnline, setServerOnline] = useState(true);

  const fetchRealStats = async () => {
    setLoading(true);
    try {
      const res = await api.get('/waitlist/stats');
      if (res.data) {
        setStats(res.data);
        setServerOnline(true);
      }
    } catch (err) {
      setServerOnline(false);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchRealStats();
    }
  }, [isOpen]);

  const downloadRegistrationsCsv = () => {
    window.open(`${api.defaults.baseURL}/waitlist/download-csv`, '_blank');
  };

  const downloadClicksCsv = () => {
    window.open(`${api.defaults.baseURL}/waitlist/download-clicks-csv`, '_blank');
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-ink/70 backdrop-blur-sm animate-fadeIn">
      <div 
        className="bg-ivory border border-marigold/40 rounded-2xl w-full max-w-2xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden relative"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header Bar */}
        <div className="bg-gradient-to-r from-tulsi-dark to-ink text-ivory px-6 py-4 flex items-center justify-between border-b border-marigold/30">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-marigold/20 border border-marigold/40 flex items-center justify-center text-marigold text-lg font-bold">
              📁
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-lg font-display font-bold text-ivory">Real Server Tracking & CSV Proof</h3>
                <span className={`px-2 py-0.5 text-[10px] font-bold uppercase rounded-full border ${
                  serverOnline 
                    ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40' 
                    : 'bg-amber-500/20 text-amber-300 border-amber-500/40'
                }`}>
                  {serverOnline ? '● Local Server Active' : '○ Offline'}
                </span>
              </div>
              <p className="text-xs text-ivory/80 mt-0.5">
                Authentic data stored in server CSV files. Zero mock numbers.
              </p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="w-8 h-8 rounded-full bg-white/10 hover:bg-white/20 text-ivory/80 hover:text-ivory flex items-center justify-center text-sm transition"
            aria-label="Close modal"
          >
            ✕
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 overflow-y-auto space-y-6">
          
          {/* Key Real Metrics Cards */}
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-white p-4 rounded-xl border border-marigold-light/60 shadow-xs text-center">
              <p className="text-[11px] text-clay uppercase font-bold tracking-wider">Link Clicks / Visits</p>
              <p className="text-2xl sm:text-3xl font-display font-bold text-ink mt-1">
                {stats.totalClicks}
              </p>
              <p className="text-[10px] text-clay/70 mt-0.5">tracked via link</p>
            </div>

            <div className="bg-white p-4 rounded-xl border border-marigold-light/60 shadow-xs text-center">
              <p className="text-[11px] text-clay uppercase font-bold tracking-wider">Real Signups</p>
              <p className="text-2xl sm:text-3xl font-display font-bold text-tulsi-dark mt-1">
                {stats.totalRegistrations}
              </p>
              <p className="text-[10px] text-emerald-700 font-semibold mt-0.5">
                {stats.eatersCount} eaters • {stats.cooksCount} cooks
              </p>
            </div>

            <div className="bg-white p-4 rounded-xl border border-marigold-light/60 shadow-xs text-center">
              <p className="text-[11px] text-clay uppercase font-bold tracking-wider">Conversion</p>
              <p className="text-2xl sm:text-3xl font-display font-bold text-marigold-dark mt-1">
                {stats.conversionRate}
              </p>
              <p className="text-[10px] text-clay/70 mt-0.5">clicks to signups</p>
            </div>
          </div>

          {/* Direct CSV Download Buttons (The evidence for investors!) */}
          <div className="bg-white p-4 rounded-xl border border-marigold/30 space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-ink">
                  Server CSV Files (On Your Computer)
                </h4>
                <p className="text-xs text-clay">
                  Every user submission is instantly appended to <code className="bg-slate-100 px-1.5 py-0.5 rounded text-tulsi font-semibold">backend/data/registrations.csv</code>
                </p>
              </div>
            </div>

            <div className="grid sm:grid-cols-2 gap-3 pt-1">
              <button
                type="button"
                onClick={downloadRegistrationsCsv}
                disabled={stats.totalRegistrations === 0}
                className={`py-2.5 px-4 rounded-xl text-xs font-bold flex items-center justify-center gap-2 transition ${
                  stats.totalRegistrations > 0 
                    ? 'bg-tulsi text-ivory hover:bg-tulsi-dark shadow-xs' 
                    : 'bg-slate-100 text-slate-400 border border-slate-200 cursor-not-allowed'
                }`}
              >
                <span>📥 Download Registrations CSV ({stats.totalRegistrations})</span>
              </button>

              <button
                type="button"
                onClick={downloadClicksCsv}
                disabled={stats.totalClicks === 0}
                className={`py-2.5 px-4 rounded-xl text-xs font-bold flex items-center justify-center gap-2 transition ${
                  stats.totalClicks > 0 
                    ? 'bg-marigold text-ink hover:bg-marigold-dark hover:text-white shadow-xs' 
                    : 'bg-slate-100 text-slate-400 border border-slate-200 cursor-not-allowed'
                }`}
              >
                <span>📊 Download Link Clicks CSV ({stats.totalClicks})</span>
              </button>
            </div>
          </div>

          {/* Real Registrations Table */}
          <div className="bg-white p-4 rounded-xl border border-marigold-light/50">
            <div className="flex justify-between items-center mb-2">
              <h4 className="text-xs font-bold uppercase tracking-wider text-ink">
                Recent Server Entries
              </h4>
              <button
                onClick={fetchRealStats}
                className="text-[11px] text-tulsi hover:underline font-semibold"
              >
                {loading ? 'Refreshing...' : '↻ Refresh Data'}
              </button>
            </div>

            {stats.recentEntries && stats.recentEntries.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-marigold-light/40 text-clay font-semibold">
                      <th className="pb-2">ID</th>
                      <th className="pb-2">Name</th>
                      <th className="pb-2">Role</th>
                      <th className="pb-2">Locality</th>
                      <th className="pb-2">Contact</th>
                      <th className="pb-2">Source</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-marigold-light/20">
                    {stats.recentEntries.map((item, i) => (
                      <tr key={i} className="hover:bg-ivory/50">
                        <td className="py-2 font-mono font-bold text-tulsi-dark">{item.id}</td>
                        <td className="py-2 font-medium text-ink">{item.name}</td>
                        <td className="py-2">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                            item.role === 'cook' ? 'bg-amber-100 text-amber-900' : 'bg-tulsi/10 text-tulsi-dark'
                          }`}>
                            {item.role}
                          </span>
                        </td>
                        <td className="py-2 text-clay">{item.locality}</td>
                        <td className="py-2 text-clay font-mono">{item.contact}</td>
                        <td className="py-2 text-clay/70">{item.source || 'direct'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="text-center py-6 text-xs text-clay bg-ivory/40 rounded-lg border border-dashed border-marigold-light/60">
                <p className="font-semibold text-ink">No pre-registrations in server CSV yet.</p>
                <p className="text-[11px] text-clay/70 mt-1">
                  Fill out the form below or share your link to start collecting real customer data!
                </p>
              </div>
            )}
          </div>

          {/* Shareable Link Tips */}
          <div className="bg-amber-50/60 p-4 rounded-xl border border-marigold-light/40 text-xs text-clay space-y-1.5">
            <p className="font-bold text-ink text-xs">🔗 How to track link clicks from Netlify / WhatsApp / Posters:</p>
            <p>Add a source tag to your link so the server CSV automatically tracks where each click and registration came from:</p>
            <div className="font-mono bg-white p-2 rounded border border-marigold-light/40 text-[11px] text-ink select-all break-all">
              {window.location.origin}/?source=whatsapp_group
            </div>
            <p className="text-[10px] text-clay/70">
              When anyone opens the link, the server automatically appends a row to <code className="font-semibold">link_clicks.csv</code>!
            </p>
          </div>

        </div>

        {/* Modal Footer */}
        <div className="bg-white border-t border-marigold-light/40 px-6 py-3 flex items-center justify-between">
          <span className="text-[11px] text-clay">
            Directly synced with local server CSV files
          </span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-full border border-clay/30 text-clay hover:text-ink text-xs font-medium transition"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
