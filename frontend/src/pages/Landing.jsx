import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import CookEarningsCalculator from '../components/CookEarningsCalculator';
import PreRegisterSection from '../components/PreRegisterSection';
import { api } from '../api/client';

const SAMPLE_DISHES = [
  {
    id: 1,
    name: 'Maa ke Haath ka Slow-Cooked Rajma Chawal',
    cook: "Anita Sharma",
    locality: "Sector 14 / DU North Campus",
    distance: "350m away",
    price: 80,
    portionsLeft: 4,
    mealType: 'lunch',
    dietary: 'veg',
    readyTime: '1:15 PM',
    rating: 4.9,
    ingredients: "Jammu Rajma, Basmati Rice, Desi Ghee, Fresh Tomatoes, Ginger, Cumin",
    oilType: "Pure Desi Ghee & Mustard Oil",
    quote: "Reminded me of Sunday lunches back home in Chandigarh.",
    tag: "Homestyle Daily"
  },
  {
    id: 2,
    name: 'Desi Ghee Phulka Thali + Aloo Gobhi & Curd',
    cook: "Rekha Devi",
    locality: "Model Town / Vigyan Nagar",
    distance: "500m away",
    price: 85,
    portionsLeft: 3,
    mealType: 'lunch',
    dietary: 'veg',
    readyTime: '1:30 PM',
    rating: 4.8,
    ingredients: "Fresh Wheat Phulkas (4 pcs), Seasonal Gobhi Matar, Tadka Dal, Fresh Dahi",
    oilType: "Cold-Pressed Mustard Oil",
    quote: "Hot soft rotis. Light on stomach, no heavy restaurant oil at all.",
    tag: "Fresh Lunch"
  },
  {
    id: 3,
    name: 'Slow-Simmered Punjabi Kadhi Pakoda + Chawal',
    cook: "Sunita Agarwal",
    locality: "Kamla Nagar / Kota Hub",
    distance: "280m away",
    price: 75,
    portionsLeft: 6,
    mealType: 'lunch',
    dietary: 'veg',
    readyTime: '1:00 PM',
    rating: 4.9,
    ingredients: "Tangy Buttermilk Kadhi, Soft Methi Pakodas, Jeera Rice",
    oilType: "Mustard Oil & Methi Tadka",
    quote: "The pakodas melt in your mouth. Best kadhi since moving away from home.",
    tag: "Student Favorite"
  },
  {
    id: 4,
    name: 'Homestyle Chicken Curry + Steamed Rice & Roti',
    cook: "Kavita Singh",
    locality: "DLF Phase 3 / Gurgaon",
    distance: "600m away",
    price: 130,
    portionsLeft: 4,
    mealType: 'dinner',
    dietary: 'non-veg',
    readyTime: '8:00 PM',
    rating: 4.9,
    ingredients: "Tender Chicken, Whole Spices, Onion-Tomato Homestyle Gravy, Steamed Rice",
    oilType: "Traditional Kachi Ghani Oil",
    quote: "Not oily red restaurant gravy. Pure home chicken recipe!",
    tag: "Dinner Special"
  },
  {
    id: 5,
    name: 'Paneer Bhurji with 3 Parathas & Mint Chutney',
    cook: "Pooja Verma",
    locality: "HSR Layout / Koramangala",
    distance: "420m away",
    price: 95,
    portionsLeft: 5,
    mealType: 'dinner',
    dietary: 'veg',
    readyTime: '8:15 PM',
    rating: 4.8,
    ingredients: "Fresh Paneer, Green Capsicum, Onions, Whole Wheat Parathas, Mint",
    oilType: "Amul Butter & Ghee",
    quote: "Perfect post-workout dinner. Healthy and super filling.",
    tag: "High Protein"
  },
  {
    id: 6,
    name: 'Indori Poha with Roasted Peanuts & Masala Chai',
    cook: "Suman Yadav",
    locality: "Civil Lines / University Area",
    distance: "250m away",
    price: 45,
    portionsLeft: 8,
    mealType: 'breakfast',
    dietary: 'veg',
    readyTime: '8:30 AM',
    rating: 5.0,
    ingredients: "Poha, Crunchy Peanuts, Curry Leaves, Mustard Seeds, Lemon, Ratlami Sev",
    oilType: "Groundnut Oil",
    quote: "Hot poha with actual masala chai. Solved my morning breakfast nightmare.",
    tag: "Breakfast"
  }
];

export default function Landing({ onOpenInvestorModal, scrollToWaitlist }) {
  const [selectedFilter, setSelectedFilter] = useState('all');
  const [activeWorkflowTab, setActiveWorkflowTab] = useState('eater');
  const [openFaq, setOpenFaq] = useState(null);
  const [realStats, setRealStats] = useState({ totalRegistrations: 0, totalClicks: 0 });
  const location = useLocation();

  // Track link click and visit in server CSV on page load
  useEffect(() => {
    const trackVisit = async () => {
      try {
        const params = new URLSearchParams(window.location.search);
        const source = params.get('source') || params.get('utm_source') || (window.location.hostname.includes('netlify') ? 'netlify_link' : 'direct');
        const referralCode = params.get('ref') || '';
        await api.post('/waitlist/track-click', {
          source: source,
          referralCode: referralCode,
          pageUrl: window.location.href
        });
      } catch (err) {
        // quiet ignore if backend not currently reachable
      }
    };

    const fetchCounts = async () => {
      try {
        const res = await api.get('/waitlist/stats');
        if (res.data) {
          setRealStats({
            totalRegistrations: res.data.totalRegistrations || 0,
            totalClicks: res.data.totalClicks || 0
          });
        }
      } catch (err) {}
    };

    trackVisit();
    fetchCounts();
  }, []);

  // Smooth scroll to waitlist if requested
  useEffect(() => {
    if (scrollToWaitlist || location.hash === '#waitlist' || location.hash === '#pre-register') {
      setTimeout(() => {
        const el = document.getElementById('waitlist');
        if (el) el.scrollIntoView({ behavior: 'smooth' });
      }, 150);
    }
  }, [scrollToWaitlist, location]);

  const filteredDishes = SAMPLE_DISHES.filter((d) => {
    if (selectedFilter === 'all') return true;
    if (selectedFilter === 'lunch') return d.mealType === 'lunch';
    if (selectedFilter === 'dinner') return d.mealType === 'dinner';
    if (selectedFilter === 'breakfast') return d.mealType === 'breakfast';
    if (selectedFilter === 'veg') return d.dietary === 'veg';
    if (selectedFilter === 'non-veg') return d.dietary === 'non-veg';
    return true;
  });

  const faqs = [
    {
      q: "What makes GharSe different from Zomato, Swiggy, or cloud kitchens?",
      a: "Commercial delivery apps connect you to restaurants that cook in heavy commercial batches using palm oil, soda, and heavy preservatives, with bills reaching ₹350–₹450. GharSe connects you with verified neighborhood home cooks (mothers and homemakers) who prepare wholesome daily meals for their own family and share up to 5 extra portions with students and professionals nearby at honest prices (₹45 to ₹130 depending on snacks, lunch, or dinner). We strictly cap at 5 plates so it never turns into a poor mess."
    },
    {
      q: "How does hygiene and food safety work for home cooks?",
      a: "Every home cook undergoes kitchen verification before listing. Because cooks prepare food for their own children and family from the very same pot, there is zero incentive to cut corners with recycled oil or chemicals."
    },
    {
      q: "How does delivery and pickup work in a hyperlocal radius?",
      a: "GharSe operates within a 500m to 1km micro-radius around university campuses and hostels. You can walk 2 minutes to pick up food hot off the stove, or opt for a 5-minute doorstep drop by a local runner."
    },
    {
      q: "I am a home cook. How do I start cooking on GharSe?",
      a: "You don't need a commercial kitchen or upfront capital. Whenever you prepare lunch or dinner for your family, decide how many extra plates you want to share. We provide food-grade packaging containers and connect you with hungry neighbors."
    },
    {
      q: "Where does pre-registration data get stored?",
      a: "All pre-registrations and link clicks from this page are saved directly into real CSV files on the server (registrations.csv and link_clicks.csv), giving verifiable evidence of student and cook demand."
    }
  ];

  return (
    <div className="bg-ivory text-ink font-body">
      {/* 2. HERO SECTION */}
      <section className="relative overflow-hidden pt-12 pb-16 md:py-20 border-b border-marigold-light/30 bg-gradient-to-b from-white/70 to-ivory">
        <div className="absolute top-10 left-1/2 -translate-x-1/2 w-[700px] h-[450px] bg-marigold/10 rounded-full blur-3xl pointer-events-none -z-10" />
        
        <div className="max-w-6xl mx-auto px-5 grid lg:grid-cols-12 gap-12 items-center">
          
          {/* Left Column: Clear Value Prop */}
          <div className="lg:col-span-7 space-y-6 text-center lg:text-left">
            
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-tulsi/10 border border-tulsi/30 text-tulsi-dark text-xs font-bold uppercase tracking-wider">
              <span className="w-2 h-2 rounded-full bg-emerald-600 animate-pulse" />
              <span>Real Home Kitchens • Not Commercial Restaurants</span>
            </div>

            <h1 className="font-display text-4xl sm:text-5xl lg:text-6xl text-ink font-bold leading-[1.15] tracking-tight">
              Ghar Ka Khana, Made by Neighbors Next Door.
            </h1>

            {/* The 5-Second Clarity Paragraph */}
            <p className="text-base sm:text-lg text-clay/90 max-w-xl mx-auto lg:mx-0 leading-relaxed font-normal">
              Not commercial cloud kitchens. Not oily restaurant delivery. Verified home cooks (mothers & homemakers) cooking wholesome meals for their families every day—and sharing <strong>strictly up to 5 extra fresh portions</strong> with students and professionals nearby at honest daily prices (<strong>₹45 to ₹130</strong> for snacks, lunch & dinner). Never bulk mess cooking.
            </p>

            {/* Quick Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-3.5 justify-center lg:justify-start pt-2">
              <a
                href="#waitlist"
                className="px-7 py-3.5 rounded-full bg-gradient-to-r from-marigold to-marigold-dark text-ink font-bold text-sm sm:text-base hover:opacity-95 shadow-md transition flex items-center justify-center gap-2 cursor-pointer"
              >
                <span>Pre-Register on Waitlist</span>
                <span>→</span>
              </a>

              <a
                href="#whats-cooking"
                className="px-6 py-3.5 rounded-full border-2 border-tulsi text-tulsi font-semibold text-sm hover:bg-tulsi hover:text-ivory transition flex items-center justify-center gap-2 cursor-pointer"
              >
                <span>Explore Daily Menu (₹45–₹130)</span>
              </a>
            </div>

            {/* Real Counter status */}
            <div className="pt-3 flex items-center justify-center lg:justify-start gap-3 text-xs text-clay">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 inline-block" />
              <span>
                {realStats.totalRegistrations > 0 
                  ? `${realStats.totalRegistrations} early members registered for pilot launch` 
                  : 'Be among the first to pre-register for the pilot launch'}
              </span>
            </div>
          </div>

          {/* Right Column: Live Neighbor Food Preview Card */}
          <div className="lg:col-span-5">
            <div className="relative max-w-md mx-auto">
              
              <div className="bg-white rounded-3xl border-2 border-marigold/40 p-6 shadow-xl relative overflow-hidden">
                <div className="flex items-center justify-between text-xs text-clay mb-3 pb-2 border-b border-marigold-light/30">
                  <div className="flex items-center gap-1.5 font-semibold text-tulsi-dark">
                    <span className="text-base">📍</span>
                    <span>Anita's Kitchen • 350m away</span>
                  </div>
                  <span className="bg-amber-100 text-amber-900 font-bold px-2 py-0.5 rounded text-[11px]">
                    4 portions left
                  </span>
                </div>

                <div>
                  <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded">
                    Pure Veg • Desi Ghee
                  </span>
                  <h3 className="font-display text-2xl font-bold text-ink mt-1">
                    Slow-Cooked Rajma Chawal
                  </h3>
                  <p className="text-xs text-clay mt-1">
                    Made with Jammu rajma, fresh tomato-ginger gravy, basmati rice & cold-pressed mustard oil.
                  </p>
                </div>

                <div className="mt-5 p-3.5 bg-ivory/80 rounded-2xl border border-marigold-light/50 flex items-center justify-between">
                  <div>
                    <span className="text-[11px] text-clay block">Meal Price</span>
                    <span className="text-2xl font-display font-extrabold text-tulsi-dark">₹80</span>
                    <span className="text-[10px] text-clay/70 ml-1">all inclusive</span>
                  </div>
                  <div className="text-right">
                    <span className="text-[11px] text-clay block">Ready for Lunch at</span>
                    <span className="text-sm font-bold text-ink">1:15 PM Today</span>
                    <span className="text-[10px] text-emerald-600 block font-semibold">Walkable pickup / 5m drop</span>
                  </div>
                </div>

                <div className="mt-4 pt-3 border-t border-marigold-light/30 flex items-start gap-2 text-xs text-clay italic">
                  <span className="text-marigold text-base">“</span>
                  <span>Tasted just like home food in hostel. Zero heavy restaurant soda or excess oil.</span>
                </div>

                <a
                  href="#waitlist"
                  className="mt-4 w-full py-3 rounded-xl bg-tulsi text-ivory text-xs font-semibold hover:bg-tulsi-dark transition flex items-center justify-center gap-2 cursor-pointer block text-center"
                >
                  <span>Pre-Register to Order from Neighbors</span>
                </a>
              </div>

            </div>
          </div>

        </div>
      </section>

      {/* 3. "THE BIG IDEA" — CRYSTAL CLEAR CLARITY SECTION */}
      <section id="the-idea" className="py-16 md:py-20 bg-white border-b border-marigold-light/30">
        <div className="max-w-6xl mx-auto px-5">
          
          <div className="text-center max-w-3xl mx-auto mb-14">
            <span className="px-3.5 py-1 rounded-full bg-marigold/15 text-marigold-dark text-xs font-bold uppercase tracking-wider">
              The Reality Check
            </span>
            <h2 className="font-display text-3xl sm:text-4xl text-ink font-bold mt-3 leading-tight">
              Why You Miss Home Food Every Single Day
            </h2>
            <p className="text-clay text-base mt-2">
              Eating every day away from home is currently a choice between expensive oily restaurants and unhygienic, monotonous hostel tiffins. Here is why GharSe exists:
            </p>
          </div>

          {/* 3-Way Comparative Grid */}
          <div className="grid md:grid-cols-3 gap-6">
            
            {/* 1. Commercial Apps */}
            <div className="bg-red-50/40 rounded-2xl border border-red-200/70 p-6 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-4">
                  <span className="w-8 h-8 rounded-full bg-red-100 text-red-700 flex items-center justify-center font-bold text-sm">
                    ✕
                  </span>
                  <span className="text-xs font-bold text-red-700 uppercase tracking-wider">
                    Commercial Food Apps
                  </span>
                </div>
                <h3 className="font-display text-xl font-bold text-ink mb-2">
                  Restaurant Delivery
                </h3>
                <ul className="space-y-2.5 text-xs text-clay mt-4">
                  <li className="flex items-start gap-2">
                    <span className="text-red-500 font-bold">•</span>
                    <span><strong>₹350–₹450 bill:</strong> Excessive delivery fees, surge pricing, GST & packaging.</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-red-500 font-bold">•</span>
                    <span><strong>Excess palm oil & soda:</strong> Leaves you lethargic and upsets everyday digestion.</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-red-500 font-bold">•</span>
                    <span><strong>45+ min transit:</strong> Arrives lukewarm in single-use plastic boxes.</span>
                  </li>
                </ul>
              </div>
              <div className="mt-6 pt-3 border-t border-red-200 text-xs font-semibold text-red-700 text-center">
                Unviable for daily meals
              </div>
            </div>

            {/* 2. Hostel Mess / Local Tiffins */}
            <div className="bg-amber-50/50 rounded-2xl border border-amber-200/70 p-6 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-4">
                  <span className="w-8 h-8 rounded-full bg-amber-100 text-amber-800 flex items-center justify-center font-bold text-sm">
                    △
                  </span>
                  <span className="text-xs font-bold text-amber-800 uppercase tracking-wider">
                    Hostel Mess / Local Tiffin
                  </span>
                </div>
                <h3 className="font-display text-xl font-bold text-ink mb-2">
                  Institutional Tiffin
                </h3>
                <ul className="space-y-2.5 text-xs text-clay mt-4">
                  <li className="flex items-start gap-2">
                    <span className="text-amber-600 font-bold">•</span>
                    <span><strong>Watery dal & repetitive menus:</strong> Monotonous food that makes you skip meals.</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-amber-600 font-bold">•</span>
                    <span><strong>Zero hygiene visibility:</strong> Questionable water filtration and cheap cooking oil.</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-amber-600 font-bold">•</span>
                    <span><strong>Monthly lock-in:</strong> Pay upfront; lose money if you eat elsewhere.</span>
                  </li>
                </ul>
              </div>
              <div className="mt-6 pt-3 border-t border-amber-200 text-xs font-semibold text-amber-800 text-center">
                Low satisfaction & daily complaints
              </div>
            </div>

            {/* 3. GharSe Hyperlocal Solution */}
            <div className="bg-gradient-to-b from-tulsi/10 to-ivory rounded-2xl border-2 border-tulsi p-6 flex flex-col justify-between shadow-md relative">
              <div className="absolute -top-3.5 right-6 bg-tulsi text-ivory text-[11px] font-bold px-3 py-0.5 rounded-full uppercase tracking-wider">
                GharSe Solution
              </div>
              <div>
                <div className="flex items-center justify-between mb-4">
                  <span className="w-8 h-8 rounded-full bg-tulsi text-ivory flex items-center justify-center font-bold text-sm">
                    ✓
                  </span>
                  <span className="text-xs font-bold text-tulsi-dark uppercase tracking-wider">
                    Hyperlocal Home Cook
                  </span>
                </div>
                <h3 className="font-display text-xl font-bold text-tulsi-dark mb-2">
                  Ghar Ka Asli Khana
                </h3>
                <ul className="space-y-2.5 text-xs text-ink mt-4 font-medium">
                  <li className="flex items-start gap-2">
                    <span className="text-emerald-700 font-bold">✓</span>
                    <span><strong>₹45 to ₹130 honest prices:</strong> From ₹45 snacks/breakfast to ₹75–₹85 daily lunch/dinner thalis and ₹130 specials.</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-emerald-700 font-bold">✓</span>
                    <span><strong>Pure home ingredients:</strong> Prepared in family kitchens in small 2 to 5 portion batches (strict max 5 cap, never poor mess cooking).</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-emerald-700 font-bold">✓</span>
                    <span><strong>500m walking radius:</strong> Walk 2 minutes to pick up or get quick local drop.</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-emerald-700 font-bold">✓</span>
                    <span><strong>Order day-by-day:</strong> No contracts. Order only when you want.</span>
                  </li>
                </ul>
              </div>
              <div className="mt-6 pt-3 border-t border-tulsi/30 text-xs font-bold text-tulsi-dark text-center">
                Healthy, authentic & guilt-free
              </div>
            </div>

          </div>

        </div>
      </section>

      {/* 4. SAMPLE MENU */}
      <section id="whats-cooking" className="py-16 md:py-20 bg-ivory border-b border-marigold-light/30">
        <div className="max-w-6xl mx-auto px-5">
          
          <div className="flex flex-col md:flex-row md:items-end justify-between mb-8 gap-4">
            <div>
              <span className="px-3 py-1 rounded-full bg-tulsi/10 text-tulsi-dark text-xs font-bold uppercase tracking-wider">
                Hyperlocal Daily Menus
              </span>
              <h2 className="font-display text-3xl sm:text-4xl text-ink font-bold mt-2">
                Sample Everyday Home Menus
              </h2>
              <p className="text-clay text-sm mt-1">
                Real food from neighbor kitchens within walking distance.
              </p>
            </div>

            {/* Filter Buttons */}
            <div className="flex flex-wrap gap-2 text-xs">
              {[
                { id: 'all', label: 'All Dishes' },
                { id: 'lunch', label: 'Lunch' },
                { id: 'dinner', label: 'Dinner' },
                { id: 'breakfast', label: 'Breakfast' },
                { id: 'veg', label: 'Pure Veg' },
                { id: 'non-veg', label: 'Non-Veg' },
              ].map((f) => (
                <button
                  key={f.id}
                  onClick={() => setSelectedFilter(f.id)}
                  className={`px-3 py-1.5 rounded-full font-semibold transition cursor-pointer ${
                    selectedFilter === f.id
                      ? 'bg-tulsi text-ivory shadow-xs'
                      : 'bg-white border border-marigold-light/60 text-clay hover:text-ink'
                  }`}
                >
                  {f.label}
                </button>
              ))}
            </div>
          </div>

          {/* Dish Cards Grid */}
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredDishes.map((dish) => (
              <div
                key={dish.id}
                className="bg-white rounded-2xl border border-marigold-light/60 p-5 shadow-xs hover:shadow-md transition flex flex-col justify-between"
              >
                <div>
                  <div className="flex justify-between items-center text-xs mb-3">
                    <span className="text-[11px] font-semibold text-tulsi-dark bg-tulsi/10 px-2 py-0.5 rounded-full">
                      📍 {dish.locality} ({dish.distance})
                    </span>
                    <span className="text-[11px] font-bold text-marigold-dark">
                      {dish.tag}
                    </span>
                  </div>

                  <h3 className="font-display text-xl font-bold text-ink">
                    {dish.name}
                  </h3>
                  <p className="text-xs text-clay/80 mt-1">
                    By <strong>{dish.cook}</strong> • ★ {dish.rating}
                  </p>

                  <div className="my-3 p-2.5 rounded-xl bg-ivory/60 border border-marigold-light/30 text-[11px] space-y-1 text-clay">
                    <div><strong>Key Ingredients:</strong> {dish.ingredients}</div>
                    <div><strong>Prepared With:</strong> {dish.oilType}</div>
                  </div>

                  <p className="text-xs text-clay italic border-l-2 border-marigold pl-2 py-0.5 my-2">
                    "{dish.quote}"
                  </p>
                </div>

                <div className="pt-3 border-t border-marigold-light/30 mt-3">
                  <div className="flex justify-between items-center mb-3">
                    <div>
                      <span className="text-xl font-display font-extrabold text-tulsi-dark">₹{dish.price}</span>
                      <span className="text-[11px] text-clay/70 ml-1">/ plate</span>
                    </div>
                    <div className="text-right">
                      <span className="text-xs font-bold text-amber-700 bg-amber-50 px-2 py-0.5 rounded">
                        {dish.portionsLeft} portions left
                      </span>
                      <span className="text-[10px] text-clay block mt-0.5">Ready: {dish.readyTime}</span>
                    </div>
                  </div>

                  <a
                    href="#waitlist"
                    className="w-full py-2.5 rounded-xl bg-marigold text-ink text-xs font-bold hover:bg-marigold-dark hover:text-white transition flex items-center justify-center gap-1.5"
                  >
                    <span>Pre-Register to Order</span>
                  </a>
                </div>
              </div>
            ))}
          </div>

        </div>
      </section>

      {/* 5. "HOW IT WORKS" */}
      <section id="how-it-works" className="py-16 md:py-20 bg-white border-b border-marigold-light/30">
        <div className="max-w-6xl mx-auto px-5">
          
          <div className="text-center max-w-2xl mx-auto mb-10">
            <span className="px-3.5 py-1 rounded-full bg-tulsi/10 text-tulsi-dark text-xs font-bold uppercase tracking-wider">
              Hyperlocal Marketplace
            </span>
            <h2 className="font-display text-3xl sm:text-4xl text-ink font-bold mt-2">
              How GharSe Works
            </h2>
            <p className="text-clay text-sm mt-2">
              Simple, hyper-local, and honest.
            </p>

            <div className="inline-flex p-1 bg-ivory border border-marigold-light/50 rounded-full mt-6">
              <button
                onClick={() => setActiveWorkflowTab('eater')}
                className={`px-5 py-2 rounded-full text-xs sm:text-sm font-semibold transition cursor-pointer ${
                  activeWorkflowTab === 'eater'
                    ? 'bg-tulsi text-ivory shadow-xs'
                    : 'text-clay hover:text-ink'
                }`}
              >
                🍱 For Food Cravers (Students & Pros)
              </button>
              <button
                onClick={() => setActiveWorkflowTab('cook')}
                className={`px-5 py-2 rounded-full text-xs sm:text-sm font-semibold transition cursor-pointer ${
                  activeWorkflowTab === 'cook'
                    ? 'bg-marigold text-ink shadow-xs font-bold'
                    : 'text-clay hover:text-ink'
                }`}
              >
                👩‍🍳 For Home Cooks (Moms & Homemakers)
              </button>
            </div>
          </div>

          {activeWorkflowTab === 'eater' ? (
            <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6 animate-fadeIn">
              <div className="p-6 rounded-2xl bg-ivory/60 border border-marigold-light/50">
                <span className="text-3xl block mb-2">📍</span>
                <h3 className="font-display text-lg font-bold text-ink">1. Discover Local Cooks</h3>
                <p className="text-xs text-clay mt-2">
                  See what verified neighbors in your 500m radius are cooking for lunch or dinner today.
                </p>
              </div>

              <div className="p-6 rounded-2xl bg-ivory/60 border border-marigold-light/50">
                <span className="text-3xl block mb-2">🍲</span>
                <h3 className="font-display text-lg font-bold text-ink">2. Reserve Your Plate</h3>
                <p className="text-xs text-clay mt-2">
                  Cooks make small family batches (strictly capped at max 5 plates per meal). Reserve in advance.
                </p>
              </div>

              <div className="p-6 rounded-2xl bg-ivory/60 border border-marigold-light/50">
                <span className="text-3xl block mb-2">🚶</span>
                <h3 className="font-display text-lg font-bold text-ink">3. Walk or 5-Min Drop</h3>
                <p className="text-xs text-clay mt-2">
                  Walk 2 minutes to pick it up warm, or get a quick drop-off at your hostel gate.
                </p>
              </div>

              <div className="p-6 rounded-2xl bg-ivory/60 border border-marigold-light/50">
                <span className="text-3xl block mb-2">❤️</span>
                <h3 className="font-display text-lg font-bold text-ink">4. Eat Pure Home Food</h3>
                <p className="text-xs text-clay mt-2">
                  Wholesome, healthy meals that don't upset your stomach before study or work.
                </p>
              </div>
            </div>
          ) : (
            <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6 animate-fadeIn">
              <div className="p-6 rounded-2xl bg-ivory/60 border border-marigold-light/50">
                <span className="text-3xl block mb-2">🍳</span>
                <h3 className="font-display text-lg font-bold text-ink">1. Cook Family Lunch</h3>
                <p className="text-xs text-clay mt-2">
                  Cook the exact meal you are already making for your family. No separate menu.
                </p>
              </div>

              <div className="p-6 rounded-2xl bg-ivory/60 border border-marigold-light/50">
                <span className="text-3xl block mb-2">📱</span>
                <h3 className="font-display text-lg font-bold text-ink">2. List Extra Portions</h3>
                <p className="text-xs text-clay mt-2">
                  Specify how many extra plates you can prepare (strictly up to 5 plates per meal at your price).
                </p>
              </div>

              <div className="p-6 rounded-2xl bg-ivory/60 border border-marigold-light/50">
                <span className="text-3xl block mb-2">📦</span>
                <h3 className="font-display text-lg font-bold text-ink">3. Hand Over at Door</h3>
                <p className="text-xs text-clay mt-2">
                  Pack using food-grade containers provided by GharSe. Customers or runners pick up at your door.
                </p>
              </div>

              <div className="p-6 rounded-2xl bg-ivory/60 border border-marigold-light/50">
                <span className="text-3xl block mb-2">💰</span>
                <h3 className="font-display text-lg font-bold text-ink">4. Daily UPI Earnings</h3>
                <p className="text-xs text-clay mt-2">
                  Receive earnings daily. Earn ₹15,000–₹30,000/month with zero commercial rent.
                </p>
              </div>
            </div>
          )}

        </div>
      </section>

      {/* 6. COOK CALCULATOR */}
      <section id="for-cooks" className="py-16 md:py-20 bg-gradient-to-b from-white to-ivory border-b border-marigold-light/30">
        <div className="max-w-6xl mx-auto px-5">
          <CookEarningsCalculator 
            onSelectCookRole={() => {
              const el = document.getElementById('waitlist');
              if (el) el.scrollIntoView({ behavior: 'smooth' });
            }} 
          />
        </div>
      </section>

      {/* 7. PRE-REGISTRATION SECTION (#waitlist) */}
      <PreRegisterSection onOpenInvestorModal={onOpenInvestorModal} />

      {/* 8. FAQ SECTION */}
      <section className="py-16 md:py-20 bg-white border-b border-marigold-light/30">
        <div className="max-w-4xl mx-auto px-5">
          <div className="text-center mb-10">
            <span className="px-3.5 py-1 rounded-full bg-marigold/15 text-marigold-dark text-xs font-bold uppercase tracking-wider">
              FAQ
            </span>
            <h2 className="font-display text-3xl font-bold text-ink mt-2">
              Frequently Asked Questions
            </h2>
          </div>

          <div className="space-y-3">
            {faqs.map((faq, idx) => {
              const isOpen = openFaq === idx;
              return (
                <div
                  key={idx}
                  className="rounded-2xl border border-marigold-light/50 bg-ivory/40 overflow-hidden transition"
                >
                  <button
                    onClick={() => setOpenFaq(isOpen ? null : idx)}
                    className="w-full text-left p-4 sm:p-5 flex justify-between items-center gap-4 cursor-pointer"
                  >
                    <span className="font-semibold text-sm sm:text-base text-ink">{faq.q}</span>
                    <span className="text-lg font-bold text-marigold-dark">
                      {isOpen ? '−' : '+'}
                    </span>
                  </button>
                  {isOpen && (
                    <div className="px-4 pb-5 sm:px-5 text-xs sm:text-sm text-clay leading-relaxed border-t border-marigold-light/30 pt-3">
                      {faq.a}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </section>

    </div>
  );
}
