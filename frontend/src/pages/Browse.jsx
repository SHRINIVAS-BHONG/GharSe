import { useEffect, useState } from 'react';
import { api } from '../api/client';
import FoodCard from '../components/FoodCard';
import { useAuth } from '../context/AuthContext';

const DEFAULT_LOCATION = {
  name: 'Sohna Road, Gurgaon',
  lat: 28.4112,
  lng: 77.0435
};

const PRESET_LOCATIONS = [
  { name: 'Sohna Road, Gurgaon', lat: 28.4112, lng: 77.0435 },
  { name: 'Sohna Town, Gurgaon', lat: 28.2486, lng: 77.0673 },
  { name: 'Cyber City / DLF, Gurgaon', lat: 28.4986, lng: 77.0878 },
  { name: 'Sector 14, Old Gurgaon', lat: 28.4732, lng: 77.0437 },
  { name: 'South Delhi (Saket / GK)', lat: 28.5245, lng: 77.2066 },
  { name: 'Central Delhi (Connaught Pl)', lat: 28.6304, lng: 77.2177 },
  { name: 'Indiranagar, Bengaluru', lat: 12.9719, lng: 77.6412 },
  { name: 'Koramangala, Bengaluru', lat: 12.9345, lng: 77.6265 },
  { name: 'Bandra West, Mumbai', lat: 19.0596, lng: 72.8295 },
  { name: 'Kothrud, Pune', lat: 18.5074, lng: 73.8077 },
  { name: 'Gachibowli, Hyderabad', lat: 17.4401, lng: 78.3489 },
  { name: 'T. Nagar, Chennai', lat: 13.0418, lng: 80.2341 },
  { name: 'Salt Lake, Kolkata', lat: 22.5868, lng: 88.4178 },
  { name: 'Malviya Nagar, Jaipur', lat: 26.8530, lng: 75.8050 },
  { name: 'Gomti Nagar, Lucknow', lat: 26.8500, lng: 80.9900 },
  { name: 'Navrangpura, Ahmedabad', lat: 23.0360, lng: 72.5600 }
];

export default function Browse() {
  const { user } = useAuth();
  const [listings, setListings] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // Default to 10 km nearby radius and sorted by nearest!
  const [filters, setFilters] = useState({
    mealType: '',
    dietaryType: '',
    pickup: false,
    delivery: false,
    maxPrice: '',
    maxDistanceKm: '10',
    sort: 'nearest'
  });

  const [selectedLoc, setSelectedLoc] = useState(() => {
    if (user?.approximateLocation?.lat) {
      return {
        name: user.locality || 'My Account Location',
        lat: user.approximateLocation.lat,
        lng: user.approximateLocation.lng
      };
    }
    return DEFAULT_LOCATION;
  });

  // Try fetching live browser geolocation if available
  useEffect(() => {
    if (!user?.approximateLocation && navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          setSelectedLoc({
            name: 'Current Live Location',
            lat: pos.coords.latitude,
            lng: pos.coords.longitude
          });
        },
        () => console.warn('Geolocation prompt dismissed; defaulting to Sohna Road, Gurgaon.'),
        { timeout: 7000 }
      );
    }
  }, [user]);

  const detectGpsLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          setSelectedLoc({
            name: 'Current Live Location',
            lat: pos.coords.latitude,
            lng: pos.coords.longitude
          });
        },
        () => alert('Location access was denied or unavailable in this browser.')
      );
    } else {
      alert('Geolocation is not supported in this browser.');
    }
  };

  useEffect(() => {
    let cancelled = false;
    setLoading(true);

    const params = { sort: filters.sort, limit: 150 };
    if (filters.mealType) params.mealType = filters.mealType;
    if (filters.dietaryType) params.dietaryType = filters.dietaryType;
    if (filters.pickup) params.pickup = 'true';
    if (filters.delivery) params.delivery = 'true';
    if (filters.maxPrice) params.maxPrice = filters.maxPrice;

    // Apply strict 10km (or user selected) radius filtering
    if (filters.maxDistanceKm && filters.maxDistanceKm !== 'all') {
      params.maxDistanceKm = filters.maxDistanceKm;
    }

    const loc = selectedLoc || DEFAULT_LOCATION;
    if (loc?.lat) {
      params.lat = loc.lat;
      params.lng = loc.lng;
    }

    api.get('/foods', { params }).then(({ data }) => {
      if (!cancelled) {
        setListings(data.listings || []);
        setLoading(false);
      }
    }).catch(() => {
      if (!cancelled) setLoading(false);
    });

    return () => { cancelled = true; };
  }, [filters, selectedLoc]);

  function update(field, value) {
    setFilters((f) => ({ ...f, [field]: value }));
  }

  return (
    <div className="max-w-6xl mx-auto px-5 py-8">
      {/* Title */}
      <h1 className="font-display text-3xl mb-1 text-ink font-bold">Available near you</h1>
      <p className="text-clay mb-5">Today's fresh home-cooked menus from neighbor kitchens.</p>

      {/* Hyperlocal Location & 10 km Radius Control Banner */}
      <div className="bg-white border border-marigold-light/80 rounded-2xl p-4 mb-6 flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-xs">
        <div className="flex items-center gap-3">
          <span className="w-9 h-9 rounded-full bg-tulsi/10 text-tulsi-dark flex items-center justify-center font-bold text-base shrink-0">
            📍
          </span>
          <div>
            <div className="text-[11px] text-clay uppercase font-bold tracking-wider">
              Showing kitchens near:
            </div>
            <div className="flex flex-wrap items-center gap-2 mt-0.5">
              <select
                value={selectedLoc.name}
                onChange={(e) => {
                  const found = PRESET_LOCATIONS.find((p) => p.name === e.target.value);
                  if (found) setSelectedLoc(found);
                }}
                className="bg-ivory border border-marigold-light font-bold text-ink rounded-lg px-2.5 py-1 text-sm cursor-pointer shadow-xs focus:ring-2 focus:ring-tulsi/30"
              >
                {selectedLoc.name === 'Current Live Location' && (
                  <option value="Current Live Location">🎯 Current Live Location</option>
                )}
                {PRESET_LOCATIONS.map((p) => (
                  <option key={p.name} value={p.name}>
                    {p.name}
                  </option>
                ))}
              </select>

              <button
                type="button"
                onClick={detectGpsLocation}
                className="text-xs bg-tulsi/10 text-tulsi-dark font-semibold px-2.5 py-1 rounded-lg hover:bg-tulsi hover:text-white transition flex items-center gap-1 cursor-pointer"
              >
                🎯 Use My GPS
              </button>
            </div>
          </div>
        </div>

        {/* Distance Range Filter Badge */}
        <div className="flex items-center gap-2 bg-ivory/80 px-3 py-1.5 rounded-xl border border-marigold-light/40 self-start md:self-auto">
          <span className="text-xs text-clay font-medium">Distance:</span>
          <select
            value={filters.maxDistanceKm}
            onChange={(e) => update('maxDistanceKm', e.target.value)}
            className="bg-white border border-marigold-light/80 rounded-lg px-2.5 py-1 text-xs font-bold text-tulsi-dark shadow-xs cursor-pointer focus:ring-2 focus:ring-tulsi/30"
          >
            <option value="5">Within 5 km</option>
            <option value="10">Within 10 km (Nearby Only)</option>
            <option value="15">Within 15 km</option>
            <option value="25">Within 25 km</option>
            <option value="all">All India (View All)</option>
          </select>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="flex flex-wrap gap-3 mb-6 items-center">
        <select
          value={filters.mealType}
          onChange={(e) => update('mealType', e.target.value)}
          className="border border-marigold-light/60 rounded-full px-3 py-1.5 text-sm bg-white"
        >
          <option value="">All meals</option>
          <option value="breakfast">Breakfast</option>
          <option value="lunch">Lunch</option>
          <option value="dinner">Dinner</option>
          <option value="snacks">Snacks</option>
        </select>

        <select
          value={filters.dietaryType}
          onChange={(e) => update('dietaryType', e.target.value)}
          className="border border-marigold-light/60 rounded-full px-3 py-1.5 text-sm bg-white"
        >
          <option value="">Veg &amp; non-veg</option>
          <option value="veg">Vegetarian</option>
          <option value="non-veg">Non-vegetarian</option>
        </select>

        <input
          type="number"
          placeholder="Max price"
          value={filters.maxPrice}
          onChange={(e) => update('maxPrice', e.target.value)}
          className="border border-marigold-light/60 rounded-full px-3 py-1.5 text-sm w-28 bg-white"
        />

        <label className="flex items-center gap-1.5 text-sm cursor-pointer select-none">
          <input
            type="checkbox"
            checked={filters.pickup}
            onChange={(e) => update('pickup', e.target.checked)}
          />
          <span>Pickup</span>
        </label>

        <label className="flex items-center gap-1.5 text-sm cursor-pointer select-none">
          <input
            type="checkbox"
            checked={filters.delivery}
            onChange={(e) => update('delivery', e.target.checked)}
          />
          <span>Delivery</span>
        </label>

        <select
          value={filters.sort}
          onChange={(e) => update('sort', e.target.value)}
          className="border border-marigold-light/60 rounded-full px-3 py-1.5 text-sm ml-auto bg-white"
        >
          <option value="nearest">Nearest to me</option>
          <option value="recent">Recently added</option>
          <option value="price_low">Lowest price</option>
          <option value="rating">Highest rated</option>
        </select>
      </div>

      {/* Loading state */}
      {loading && <p className="text-clay py-8 text-center">Loading neighbor menus within range...</p>}

      {/* Empty State */}
      {!loading && listings.length === 0 && (
        <div className="text-center py-12 bg-white rounded-2xl border border-marigold-light/40 p-8 my-4 shadow-xs">
          <div className="text-4xl mb-3">🍲</div>
          <p className="font-display text-lg text-ink font-bold mb-1">
            No dishes found within {filters.maxDistanceKm} km of {selectedLoc.name}
          </p>
          <p className="text-sm text-clay mb-4">
            Try expanding your search radius to discover kitchens slightly further out.
          </p>
          <button
            onClick={() => update('maxDistanceKm', '25')}
            className="px-5 py-2.5 rounded-full bg-marigold text-ink text-xs font-bold hover:bg-marigold-dark hover:text-white transition shadow-xs cursor-pointer"
          >
            Expand Radius to 25 km
          </button>
        </div>
      )}

      {/* Listings Grid */}
      <div className="grid sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-5">
        {listings.map((l) => (
          <FoodCard key={l._id} listing={l} />
        ))}
      </div>
    </div>
  );
}
