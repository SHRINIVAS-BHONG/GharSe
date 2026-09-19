import React, { useState } from 'react';

export default function CookEarningsCalculator({ onSelectCookRole }) {
  const [platesPerMeal, setPlatesPerMeal] = useState(4);
  const [mealsPerDay, setMealsPerDay] = useState(1); // 1 (Lunch or Dinner) or 2 (Both)
  const [pricePerPlate, setPricePerPlate] = useState(85);
  const [daysPerWeek, setDaysPerWeek] = useState(6);

  const totalPlatesPerDay = platesPerMeal * mealsPerDay;
  const monthlyPlates = Math.round(totalPlatesPerDay * daysPerWeek * 4.3);
  const grossMonthly = monthlyPlates * pricePerPlate;
  const estimatedIngredientCost = Math.round(grossMonthly * 0.40);
  const platformFee = Math.round(grossMonthly * 0.10);
  const netMonthlyProfit = grossMonthly - estimatedIngredientCost - platformFee;

  return (
    <div className="bg-white rounded-2xl border border-marigold/30 shadow-md p-6 sm:p-8 max-w-4xl mx-auto">
      <div className="text-center max-w-2xl mx-auto mb-8">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-100 text-emerald-900 text-xs font-bold uppercase tracking-wider mb-2">
          <span>🛡️ Strict Quality Rule: Max 5 Plates per Meal</span>
        </div>
        <h3 className="font-display text-3xl text-ink font-bold">
          Turn Daily Family Cooking Into Dignified Income
        </h3>
        <p className="text-clay text-sm mt-2">
          We strictly cap cooks at a <strong>maximum of 5 extra plates</strong> per meal. This ensures your food never becomes a cheap, bulk hostel mess, but always remains genuine Maa ke haath ka khana cooked from the family pot.
        </p>
      </div>

      <div className="grid md:grid-cols-12 gap-8 items-center">
        {/* Sliders Column */}
        <div className="md:col-span-7 space-y-6">
          
          {/* Slider 1: Plates (Strictly 1 to 5 max) */}
          <div>
            <div className="flex justify-between items-center mb-2">
              <label className="text-sm font-semibold text-ink">
                Extra plates cooked per meal (Max 5):
              </label>
              <span className="text-sm font-bold text-tulsi-dark bg-tulsi/10 px-3 py-0.5 rounded-full">
                {platesPerMeal} plates / meal
              </span>
            </div>
            <input
              type="range"
              min="1"
              max="5"
              step="1"
              value={platesPerMeal}
              onChange={(e) => setPlatesPerMeal(Number(e.target.value))}
              className="w-full accent-marigold cursor-pointer h-2 bg-slate-100 rounded-lg"
            />
            <div className="flex justify-between text-[11px] text-clay/80 mt-1 font-medium">
              <span>1 plate (Just 1 extra)</span>
              <span>3 plates (Comfortable)</span>
              <span className="text-emerald-700 font-bold">5 plates (Strict Max Cap)</span>
            </div>
          </div>

          {/* Meals per day (Lunch only vs Lunch + Dinner) */}
          <div>
            <div className="flex justify-between items-center mb-2">
              <label className="text-sm font-semibold text-ink">
                Meals you want to share:
              </label>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => setMealsPerDay(1)}
                  className={`px-3 py-1 rounded-lg text-xs font-bold transition cursor-pointer ${
                    mealsPerDay === 1
                      ? 'bg-tulsi text-ivory'
                      : 'bg-slate-100 text-clay hover:text-ink'
                  }`}
                >
                  Lunch Only (1 meal)
                </button>
                <button
                  type="button"
                  onClick={() => setMealsPerDay(2)}
                  className={`px-3 py-1 rounded-lg text-xs font-bold transition cursor-pointer ${
                    mealsPerDay === 2
                      ? 'bg-tulsi text-ivory'
                      : 'bg-slate-100 text-clay hover:text-ink'
                  }`}
                >
                  Lunch + Dinner (2 meals)
                </button>
              </div>
            </div>
          </div>

          {/* Slider 2: Price per Plate */}
          <div>
            <div className="flex justify-between items-center mb-2">
              <label className="text-sm font-semibold text-ink">
                Your price per thali / meal:
              </label>
              <span className="text-sm font-bold text-marigold-dark bg-marigold/10 px-3 py-0.5 rounded-full">
                ₹{pricePerPlate} / thali
              </span>
            </div>
            <input
              type="range"
              min="45"
              max="130"
              step="5"
              value={pricePerPlate}
              onChange={(e) => setPricePerPlate(Number(e.target.value))}
              className="w-full accent-marigold cursor-pointer h-2 bg-slate-100 rounded-lg"
            />
            <div className="flex justify-between text-[11px] text-clay/70 mt-1">
              <span>₹45 (Breakfast & Snacks)</span>
              <span>₹85 (Daily Lunch / Dinner)</span>
              <span>₹130 (Special / Non-Veg)</span>
            </div>
          </div>

          {/* Slider 3: Days per week */}
          <div>
            <div className="flex justify-between items-center mb-2">
              <label className="text-sm font-semibold text-ink">
                Cooking days per week:
              </label>
              <span className="text-sm font-bold text-ink bg-slate-100 px-3 py-0.5 rounded-full">
                {daysPerWeek} days / week
              </span>
            </div>
            <input
              type="range"
              min="3"
              max="7"
              step="1"
              value={daysPerWeek}
              onChange={(e) => setDaysPerWeek(Number(e.target.value))}
              className="w-full accent-marigold cursor-pointer h-2 bg-slate-100 rounded-lg"
            />
            <div className="flex justify-between text-[11px] text-clay/70 mt-1">
              <span>3 days (Part-time)</span>
              <span>5 days (Mon–Fri)</span>
              <span>7 days (Daily)</span>
            </div>
          </div>

          {/* Quality Cap highlight */}
          <div className="p-3 bg-emerald-50 rounded-xl border border-emerald-200 text-xs text-emerald-900 leading-relaxed">
            <strong>Why we cap at 5 plates:</strong> Cooking 20+ plates requires commercial burners and bulk prep, turning food into a tasteless mess. By cooking only 2 to 5 extra plates, you maintain 100% pure family quality.
          </div>
        </div>

        {/* Projected Earnings Summary Card */}
        <div className="md:col-span-5 bg-gradient-to-br from-ivory to-amber-50/60 p-6 rounded-2xl border border-marigold/40 text-center shadow-sm">
          <p className="text-xs font-semibold uppercase tracking-wider text-clay">
            Estimated Monthly Pocket Earnings
          </p>
          <div className="my-4">
            <span className="text-4xl sm:text-5xl font-display font-extrabold text-tulsi-dark">
              ₹{netMonthlyProfit.toLocaleString()}
            </span>
            <span className="text-xs text-clay block mt-1 font-medium">
              extra savings from what you already cook
            </span>
          </div>

          <div className="bg-white/80 rounded-xl p-3.5 space-y-2 text-xs text-left border border-marigold-light/40 my-4">
            <div className="flex justify-between text-clay">
              <span>Extra Meals Shared:</span>
              <span className="font-semibold text-ink">{monthlyPlates} plates / mo</span>
            </div>
            <div className="flex justify-between text-clay">
              <span>Gross Customer Revenue:</span>
              <span className="font-semibold text-ink">₹{grossMonthly.toLocaleString()}</span>
            </div>
            <div className="flex justify-between text-clay">
              <span>Est. Ingredients (~40%):</span>
              <span className="font-semibold text-clay">- ₹{estimatedIngredientCost.toLocaleString()}</span>
            </div>
            <div className="flex justify-between text-clay">
              <span>Platform Fee (10%):</span>
              <span className="font-semibold text-clay">- ₹{platformFee.toLocaleString()}</span>
            </div>
            <div className="border-t border-marigold-light/30 pt-1.5 flex justify-between font-bold text-tulsi-dark">
              <span>Your Pure Take-Home:</span>
              <span>₹{netMonthlyProfit.toLocaleString()}</span>
            </div>
          </div>

          <button
            onClick={() => {
              if (onSelectCookRole) onSelectCookRole();
              const el = document.getElementById('waitlist');
              if (el) el.scrollIntoView({ behavior: 'smooth' });
            }}
            className="w-full py-3 px-5 rounded-full bg-tulsi text-ivory text-sm font-semibold hover:bg-tulsi-dark transition shadow-md flex items-center justify-center gap-2 group cursor-pointer"
          >
            <span>Pre-Register as Home Cook (Max 5 Plates)</span>
            <span className="group-hover:translate-x-1 transition-transform">→</span>
          </button>
        </div>
      </div>
    </div>
  );
}
