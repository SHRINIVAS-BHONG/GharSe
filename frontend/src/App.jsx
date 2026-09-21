import React, { useState, useEffect } from 'react';
import { Routes, Route, useLocation } from 'react-router-dom';
import Navbar from './components/Navbar';
import ProtectedRoute from './components/ProtectedRoute';
import InvestorProofModal from './components/InvestorProofModal';

import Landing from './pages/Landing';
import Login from './pages/Login';
import SignupCustomer from './pages/SignupCustomer';
import SignupSeller from './pages/SignupSeller';
import VerifyEmail from './pages/VerifyEmail';
import ForgotPassword from './pages/ForgotPassword';
import Browse from './pages/Browse';
import FoodDetail from './pages/FoodDetail';
import OrderHistory from './pages/OrderHistory';
import OrderTracking from './pages/OrderTracking';
import SellerProfilePage from './pages/SellerProfilePage';
import SellerDashboard from './pages/SellerDashboard';
import SellerAddFood from './pages/SellerAddFood';
import SellerOrders from './pages/SellerOrders';
import AdminDashboard from './pages/AdminDashboard';

export default function App() {
  const [investorModalOpen, setInvestorModalOpen] = useState(false);
  const location = useLocation();

  // Auto-open investor modal if query has ?investor=true or hash is #investor
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    if (params.get('investor') === 'true' || location.hash === '#investor') {
      setInvestorModalOpen(true);
    }
  }, [location]);

  return (
    <div className="min-h-screen flex flex-col bg-ivory text-ink">
      <Navbar onOpenInvestorModal={() => setInvestorModalOpen(true)} />
      
      {/* Global Investor Evidence Modal */}
      <InvestorProofModal 
        isOpen={investorModalOpen} 
        onClose={() => setInvestorModalOpen(false)} 
      />

      <main className="flex-1">
        <Routes>
          <Route 
            path="/" 
            element={<Landing onOpenInvestorModal={() => setInvestorModalOpen(true)} />} 
          />
          <Route 
            path="/pre-register" 
            element={<Landing scrollToWaitlist={true} onOpenInvestorModal={() => setInvestorModalOpen(true)} />} 
          />
          <Route 
            path="/waitlist" 
            element={<Landing scrollToWaitlist={true} onOpenInvestorModal={() => setInvestorModalOpen(true)} />} 
          />

          <Route path="/login" element={<Login />} />
          <Route path="/signup/customer" element={<SignupCustomer />} />
          <Route path="/signup/seller" element={<SignupSeller />} />
          <Route path="/verify-email" element={<VerifyEmail />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/browse" element={<Browse />} />
          <Route path="/food/:id" element={<FoodDetail />} />
          <Route path="/sellers/:id" element={<SellerProfilePage />} />

          <Route path="/orders" element={<ProtectedRoute role="customer"><OrderHistory /></ProtectedRoute>} />
          <Route path="/orders/:id" element={<ProtectedRoute><OrderTracking /></ProtectedRoute>} />

          <Route path="/seller/dashboard" element={<ProtectedRoute role="seller"><SellerDashboard /></ProtectedRoute>} />
          <Route path="/seller/add-food" element={<ProtectedRoute role="seller"><SellerAddFood /></ProtectedRoute>} />
          <Route path="/seller/orders" element={<ProtectedRoute role="seller"><SellerOrders /></ProtectedRoute>} />

          <Route path="/admin" element={<ProtectedRoute role="admin"><AdminDashboard /></ProtectedRoute>} />

          <Route path="*" element={<NotFound />} />
        </Routes>
      </main>

      <footer className="border-t border-marigold-light/40 py-10 bg-white/60 text-xs text-clay">
        <div className="max-w-6xl mx-auto px-5 grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="md:col-span-2 space-y-3">
            <span className="font-display text-2xl font-bold text-tulsi-dark">GharSe</span>
            <p className="text-xs text-clay/90 max-w-sm">
              A hyperlocal community marketplace connecting verified home cooks with students and working professionals craving honest, authentic home food.
            </p>
            <p className="text-[11px] text-clay/70">
              © {new Date().getFullYear()} GharSe Technologies Inc. All rights reserved.
            </p>
          </div>

          <div>
            <p className="font-bold text-ink uppercase tracking-wider text-[11px] mb-3">Quick Navigation</p>
            <ul className="space-y-2 text-xs">
              <li><a href="/#the-idea" className="hover:text-marigold-dark transition">The Big Idea</a></li>
              <li><a href="/#whats-cooking" className="hover:text-marigold-dark transition">Sample Daily Menu</a></li>
              <li><a href="/#how-it-works" className="hover:text-marigold-dark transition">How It Works</a></li>
              <li><a href="/#for-cooks" className="hover:text-marigold-dark transition">Cook Earnings Calculator</a></li>
              <li><a href="/#waitlist" className="hover:text-marigold-dark font-semibold text-tulsi">Join Early Access Waitlist</a></li>
            </ul>
          </div>

          <div>
            <p className="font-bold text-ink uppercase tracking-wider text-[11px] mb-3">Investors & Partners</p>
            <ul className="space-y-2 text-xs">
              <li>
                <button 
                  onClick={() => setInvestorModalOpen(true)}
                  className="hover:text-tulsi font-semibold text-left flex items-center gap-1"
                >
                  <span>📊 Live Investor Evidence Hub</span>
                </button>
              </li>
              <li>
                <a href="mailto:investors@gharse.in" className="hover:text-marigold-dark transition">
                  Request Investor Pitch Deck
                </a>
              </li>
              <li>
                <a href="mailto:founders@gharse.in" className="hover:text-marigold-dark transition">
                  Partner with Pilot Campus
                </a>
              </li>
              <li>
                <span className="inline-block mt-2 px-2 py-0.5 rounded text-[10px] bg-emerald-100 text-emerald-800 font-semibold">
                  Seed Round Raising
                </span>
              </li>
            </ul>
          </div>
        </div>
      </footer>
    </div>
  );
}

function NotFound() {
  return (
    <div className="max-w-2xl mx-auto px-5 py-20 text-center text-clay">
      <h2 className="text-3xl font-display font-bold text-ink mb-2">404 — Page Not Found</h2>
      <p className="text-sm mb-6">The page you are looking for does not exist or has moved.</p>
      <a 
        href="/" 
        className="px-6 py-2.5 rounded-full bg-tulsi text-ivory text-xs font-semibold hover:bg-tulsi-dark transition"
      >
        Return to Home Page
      </a>
    </div>
  );
}
