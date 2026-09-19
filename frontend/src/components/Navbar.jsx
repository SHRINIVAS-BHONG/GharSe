import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Navbar({ onOpenInvestorModal }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  function handleLogout() {
    logout();
    navigate('/');
  }

  const isHome = location.pathname === '/';

  const scrollToAnchor = (id) => {
    setMobileMenuOpen(false);
    if (!isHome) {
      navigate(`/#${id}`);
      return;
    }
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <div className="sticky top-0 z-50 w-full shadow-xs">
      
      {/* 1. TOP ANNOUNCEMENT STRIP (Unified inside sticky container, never overlaps) */}
      <div className="bg-gradient-to-r from-tulsi-dark via-tulsi to-clay text-ivory text-xs py-1.5 px-4 text-center border-b border-marigold/20">
        <div className="max-w-6xl mx-auto flex items-center justify-center gap-2 flex-wrap text-[11px] sm:text-xs">
          <span className="bg-marigold text-ink text-[10px] font-extrabold uppercase px-2 py-0.5 rounded-full">
            Pilot Launch
          </span>
          <span className="font-medium text-ivory/90">
            Pre-registration is live for university campuses & local neighborhoods.
          </span>
          <button
            type="button"
            onClick={() => scrollToAnchor('waitlist')}
            className="underline text-marigold-light font-bold hover:text-white transition ml-1 cursor-pointer"
          >
            Claim Early Access Pass →
          </button>
        </div>
      </div>

      {/* 2. MAIN NAVBAR */}
      <header className="bg-ivory/95 backdrop-blur-md border-b border-marigold-light/50 h-16 flex items-center">
        <div className="max-w-6xl mx-auto px-5 w-full flex items-center justify-between">
          
          {/* Brand Logo */}
          <Link to="/" className="flex items-center gap-2.5 group">
            <span className="font-display text-2xl font-bold text-tulsi-dark tracking-tight group-hover:text-marigold transition">
              GharSe
            </span>
            <span className="hidden sm:inline-flex items-center gap-1 text-[10px] font-semibold uppercase tracking-wider text-emerald-800 bg-emerald-100/70 px-2 py-0.5 rounded-full border border-emerald-300/60">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-600 animate-pulse" />
              Home Food
            </span>
          </Link>

          {/* Desktop Navigation Links */}
          <nav className="hidden md:flex items-center gap-6 text-sm font-medium">
            {!user && (
              <>
                <button
                  type="button"
                  onClick={() => scrollToAnchor('the-idea')}
                  className="text-clay hover:text-ink transition cursor-pointer"
                >
                  The Idea
                </button>

                <button
                  type="button"
                  onClick={() => scrollToAnchor('whats-cooking')}
                  className="text-clay hover:text-ink transition cursor-pointer"
                >
                  Menu
                </button>

                <button
                  type="button"
                  onClick={() => scrollToAnchor('how-it-works')}
                  className="text-clay hover:text-ink transition cursor-pointer"
                >
                  How It Works
                </button>

                <button
                  type="button"
                  onClick={() => scrollToAnchor('for-cooks')}
                  className="text-clay hover:text-ink transition cursor-pointer"
                >
                  For Cooks
                </button>

                <Link 
                  to="/browse" 
                  className="text-clay hover:text-ink transition"
                >
                  Browse
                </Link>
              </>
            )}

            {user && user.role === 'customer' && (
              <>
                <Link to="/browse" className="text-clay hover:text-ink">Find food</Link>
                <Link to="/orders" className="text-clay hover:text-ink">My orders</Link>
              </>
            )}

            {user && user.role === 'seller' && (
              <>
                <Link to="/seller/dashboard" className="text-clay hover:text-ink">Dashboard</Link>
                <Link to="/seller/orders" className="text-clay hover:text-ink">Orders</Link>
              </>
            )}

            {user && user.role === 'admin' && (
              <Link to="/admin" className="text-clay hover:text-ink">Admin</Link>
            )}
          </nav>

          {/* Right Actions */}
          <div className="hidden md:flex items-center gap-3.5">
            {!user ? (
              <>
                <button
                  type="button"
                  onClick={() => scrollToAnchor('waitlist')}
                  className="px-4 py-2 rounded-full bg-marigold text-ink font-bold text-xs hover:bg-marigold-dark hover:text-white transition shadow-xs cursor-pointer"
                >
                  Join Waitlist
                </button>

                <Link 
                  to="/login" 
                  className="text-xs text-clay hover:text-ink font-medium ml-1 transition"
                >
                  Log in
                </Link>
              </>
            ) : (
              <div className="flex items-center gap-3 text-xs">
                <span className="text-clay font-medium">Hi, {user.name?.split(' ')[0] || ''}</span>
                <button 
                  onClick={handleLogout} 
                  className="px-3 py-1.5 rounded-full border border-tulsi text-tulsi hover:bg-tulsi hover:text-ivory transition"
                >
                  Log out
                </button>
              </div>
            )}
          </div>

          {/* Mobile hamburger button */}
          <div className="flex items-center gap-2.5 md:hidden">
            <button
              type="button"
              onClick={() => scrollToAnchor('waitlist')}
              className="px-3.5 py-1.5 rounded-full bg-marigold text-ink text-xs font-bold shadow-2xs"
            >
              Waitlist
            </button>

            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-1.5 rounded-lg text-clay hover:text-ink focus:outline-none text-lg"
              aria-label="Toggle Menu"
            >
              {mobileMenuOpen ? '✕' : '☰'}
            </button>
          </div>

        </div>
      </header>

      {/* Mobile dropdown menu */}
      {mobileMenuOpen && (
        <div className="md:hidden bg-ivory/98 backdrop-blur-md border-b border-marigold-light/40 px-5 py-4 space-y-2.5 text-sm animate-fadeIn shadow-md">
          <button
            onClick={() => scrollToAnchor('the-idea')}
            className="block w-full text-left text-clay hover:text-ink py-1 font-medium"
          >
            The Idea
          </button>
          <button
            onClick={() => scrollToAnchor('whats-cooking')}
            className="block w-full text-left text-clay hover:text-ink py-1 font-medium"
          >
            Menu
          </button>
          <button
            onClick={() => scrollToAnchor('how-it-works')}
            className="block w-full text-left text-clay hover:text-ink py-1 font-medium"
          >
            How It Works
          </button>
          <button
            onClick={() => scrollToAnchor('for-cooks')}
            className="block w-full text-left text-clay hover:text-ink py-1 font-medium"
          >
            For Cooks
          </button>
          <Link
            to="/browse"
            onClick={() => setMobileMenuOpen(false)}
            className="block text-clay hover:text-ink py-1 font-medium"
          >
            Browse
          </Link>
          
          <div className="pt-3 border-t border-marigold-light/40 flex items-center justify-between gap-3">
            <button
              onClick={() => scrollToAnchor('waitlist')}
              className="flex-1 py-2 rounded-full bg-marigold text-ink font-bold text-xs text-center"
            >
              Join Waitlist
            </button>
            <Link
              to="/login"
              onClick={() => setMobileMenuOpen(false)}
              className="px-4 py-2 rounded-full border border-clay/30 text-clay text-xs font-medium text-center"
            >
              Log in
            </Link>
          </div>
        </div>
      )}

    </div>
  );
}
