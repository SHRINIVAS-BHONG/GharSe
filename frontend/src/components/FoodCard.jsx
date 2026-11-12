import { Link } from 'react-router-dom';
import { imageUrl } from '../api/client';

const MEAL_LABEL = { breakfast: 'Breakfast', lunch: 'Lunch', dinner: 'Dinner', snacks: 'Snacks' };

export default function FoodCard({ listing }) {
  const soldOut = listing.status === 'soldout' || listing.remainingQuantity <= 0;
  const sellerName = listing.sellerId?.userId?.name;
  const sellerLocality = listing.sellerId?.userId?.locality;
  const rating = listing.sellerId?.rating;
  const isVeg = listing.dietaryType === 'veg';

  return (
    <Link
      to={`/food/${listing._id}`}
      className="block group bg-white rounded-2xl overflow-hidden border border-marigold-light/50 hover:shadow-lg hover:-translate-y-1 transition-all duration-300"
    >
      <div className="h-44 bg-marigold-light/20 relative flex items-center justify-center overflow-hidden">
        {listing.image ? (
          <img
            src={imageUrl(listing.image)}
            alt={listing.name}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500 ease-out"
            loading="lazy"
          />
        ) : (
          <span className="font-display text-4xl text-marigold-dark/40">{listing.name?.[0]}</span>
        )}
        {soldOut && (
          <div className="absolute inset-0 bg-ink/70 flex items-center justify-center backdrop-blur-xs">
            <span className="text-ivory font-display text-lg font-bold">Sold out</span>
          </div>
        )}
        {/* Meal Type Badge */}
        <span className="absolute top-2.5 left-2.5 bg-white/95 backdrop-blur-sm text-[11px] font-semibold px-2.5 py-0.5 rounded-full text-clay shadow-xs">
          {MEAL_LABEL[listing.mealType] || 'Meal'}
        </span>

        {/* Veg / Non-Veg Indicator */}
        <span className="absolute top-2.5 right-2.5 bg-white/95 backdrop-blur-sm px-2 py-0.5 rounded-full flex items-center gap-1 shadow-xs">
          <span className={`w-2 h-2 rounded-full ${isVeg ? 'bg-emerald-600' : 'bg-red-600'}`} />
          <span className={`text-[10px] font-bold ${isVeg ? 'text-emerald-800' : 'text-red-800'}`}>
            {isVeg ? 'Veg' : 'Non-Veg'}
          </span>
        </span>

        {/* Ready time chip */}
        <span className="absolute bottom-2 left-2.5 bg-black/50 backdrop-blur-sm text-white text-[10px] font-medium px-2 py-0.5 rounded">
          ⏱ Ready {listing.readyTime}
        </span>
      </div>

      <div className="p-3.5 flex flex-col justify-between">
        <div>
          <h3 className="font-display text-base font-bold text-ink leading-snug group-hover:text-tulsi-dark transition-colors line-clamp-1">
            {listing.name}
          </h3>
          <p className="text-xs text-clay mt-0.5 flex items-center justify-between">
            <span>By <strong className="text-ink/80">{sellerName || 'Local Cook'}</strong></span>
            {rating > 0 && (
              <span className="text-amber-700 font-bold bg-amber-50 px-1.5 py-0.2 rounded border border-amber-200/50">
                ★ {rating}
              </span>
            )}
          </p>
          {sellerLocality && (
            <p className="text-[11px] text-clay/80 mt-1 line-clamp-1">
              📍 {sellerLocality}
            </p>
          )}
        </div>

        <div className="pt-2 border-t border-marigold-light/30 mt-2.5 flex items-center justify-between">
          <div>
            <span className="text-lg font-display font-extrabold text-tulsi-dark">₹{listing.price}</span>
            <span className="text-[10px] text-clay/70 ml-0.5">/ plate</span>
          </div>
          <span className="text-[11px] font-semibold text-amber-700 bg-amber-50 px-2 py-0.5 rounded-full">
            {soldOut ? 'Sold out' : `${listing.remainingQuantity} left`}
          </span>
        </div>
      </div>
    </Link>
  );
}
