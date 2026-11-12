import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api, apiErrorMessage } from '../api/client';
import StatusStepper from '../components/StatusStepper';

const CANCEL_REASONS = [
  'Ordered by mistake',
  'Change of plans / eating elsewhere',
  'Need to change delivery address or phone',
  'Taking longer than expected',
  'Other',
];

export default function OrderTracking() {
  const { id } = useParams();
  const [order, setOrder] = useState(null);
  const [error, setError] = useState('');
  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState('');
  const [reviewSubmitted, setReviewSubmitted] = useState(false);
  const [reviewError, setReviewError] = useState('');
  const [complaintOpen, setComplaintOpen] = useState(false);
  const [complaintCategory, setComplaintCategory] = useState('food_quality');
  const [complaintDesc, setComplaintDesc] = useState('');
  const [complaintSubmitted, setComplaintSubmitted] = useState(false);
  const [complaintError, setComplaintError] = useState('');

  // Cancellation state
  const [cancelModalOpen, setCancelModalOpen] = useState(false);
  const [cancelReason, setCancelReason] = useState(CANCEL_REASONS[0]);
  const [customCancelReason, setCustomCancelReason] = useState('');
  const [cancelling, setCancelling] = useState(false);
  const [cancelError, setCancelError] = useState('');

  function load() {
    api.get(`/orders/${id}`).then(({ data }) => setOrder(data.order)).catch((err) => setError(apiErrorMessage(err)));
  }

  useEffect(() => { load(); }, [id]);

  if (error) return <div className="max-w-2xl mx-auto px-5 py-16 text-red-700">{error}</div>;
  if (!order) return <div className="max-w-2xl mx-auto px-5 py-16 text-clay">Loading order...</div>;

  const canCancel = ['placed', 'accepted'].includes(order.status);

  async function handleCancelOrder() {
    setCancelling(true);
    setCancelError('');
    const finalReason = cancelReason === 'Other'
      ? (customCancelReason.trim() || 'Other reason')
      : cancelReason;

    try {
      let res;
      try {
        res = await api.post(`/orders/${order._id}/cancel`, { reason: finalReason });
      } catch {
        res = await api.put(`/orders/${order._id}/status`, { status: 'cancelled', cancellationReason: finalReason });
      }
      if (res?.data?.order) {
        setOrder(res.data.order);
      } else {
        load();
      }
      setCancelModalOpen(false);
    } catch (err) {
      setCancelError(apiErrorMessage(err));
    } finally {
      setCancelling(false);
    }
  }

  async function submitReview(e) {
    e.preventDefault();
    setReviewError('');
    try {
      await api.post('/reviews', { orderId: order._id, rating, comment });
      setReviewSubmitted(true);
    } catch (err) {
      setReviewError(apiErrorMessage(err));
    }
  }

  async function submitComplaint(e) {
    e.preventDefault();
    setComplaintError('');
    try {
      await api.post('/complaints', { orderId: order._id, category: complaintCategory, description: complaintDesc });
      setComplaintSubmitted(true);
      setComplaintOpen(false);
    } catch (err) {
      setComplaintError(apiErrorMessage(err));
    }
  }

  return (
    <div className="max-w-2xl mx-auto px-5 py-10">
      <Link to="/orders" className="text-sm text-marigold-dark">← Back to my orders</Link>
      <div className="flex items-center justify-between mt-2 flex-wrap gap-2">
        <h1 className="font-display text-3xl">Order #{order.orderNumber}</h1>
        {order.status === 'cancelled' && (
          <span className="px-3 py-1 bg-red-100 text-red-800 rounded-full text-xs font-semibold uppercase tracking-wider">
            Cancelled
          </span>
        )}
      </div>

      {/* Cancellation Banner if order is cancelled */}
      {order.status === 'cancelled' && (
        <div className="bg-red-50/80 border border-red-200 rounded-card p-5 mt-5">
          <div className="flex items-start gap-3">
            <span className="w-8 h-8 rounded-full bg-red-100 flex items-center justify-center font-bold text-red-600 flex-shrink-0">✕</span>
            <div className="flex-1">
              <h3 className="font-semibold text-red-900 text-base">This order was cancelled</h3>
              <p className="text-xs text-red-700 mt-1">
                {order.cancellationReason
                  ? `Reason: ${order.cancellationReason}`
                  : 'Order cancelled by customer.'}
              </p>

              {order.paymentMethod === 'upi' ? (
                <div className="mt-3 bg-white/90 border border-red-200 rounded-xl p-3.5 text-xs text-ink space-y-1.5 shadow-sm">
                  <div className="flex justify-between items-center">
                    <span className="font-semibold text-tulsi-dark flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-tulsi inline-block"></span>
                      100% UPI Refund Initiated
                    </span>
                    <span className="font-bold text-sm text-ink">₹{order.total}</span>
                  </div>
                  {order.refundReference && (
                    <p className="text-clay font-mono text-[11px]">
                      Refund ID: <span className="text-ink">{order.refundReference}</span>
                    </p>
                  )}
                  <p className="text-clay leading-relaxed">
                    Full refund of ₹{order.total} has been initiated back to your source UPI account. Standard UPI processing usually credits within 2 to 4 hours.
                  </p>
                </div>
              ) : (
                <div className="mt-3 bg-white/90 border border-red-200 rounded-xl p-3 text-xs text-ink shadow-sm">
                  <p className="font-semibold text-ink flex items-center gap-1.5">
                    💵 Cash on Fulfillment
                  </p>
                  <p className="text-clay mt-1">
                    Since this was a Cash payment order, no money was charged or collected.
                  </p>
                </div>
              )}

              <div className="mt-4">
                <Link
                  to="/browse"
                  className="inline-block px-4 py-2 bg-tulsi text-ivory rounded-full text-xs font-medium hover:bg-tulsi-dark transition shadow-sm"
                >
                  Explore other dishes near you →
                </Link>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Order Summary Card */}
      <div className="bg-white rounded-card border border-marigold-light/50 p-5 mt-5">
        {order.items.map((item) => (
          <div key={item.listingId} className="flex justify-between text-sm mb-1">
            <span>{item.name} × {item.quantity}</span>
            <span>₹{item.price * item.quantity}</span>
          </div>
        ))}
        <div className="border-t border-marigold-light/40 mt-2 pt-2 text-sm space-y-1">
          <div className="flex justify-between"><span className="text-clay">Delivery fee</span><span>₹{order.deliveryFee}</span></div>
          <div className="flex justify-between font-semibold"><span>Total</span><span>₹{order.total}</span></div>
        </div>
        <p className="text-xs text-clay mt-2 flex items-center justify-between flex-wrap gap-1">
          <span>
            {order.fulfillmentType === 'pickup' ? 'Pickup' : `Delivery to ${order.deliveryLocality}`} ·{' '}
            {order.paymentMethod === 'cash' ? 'Cash' : 'UPI'} ({order.paymentStatus?.replace(/_/g, ' ') || 'pending'})
          </span>
          {order.paymentMethod === 'upi' && order.status !== 'cancelled' && (
            <span className="text-tulsi-dark font-medium text-[11px]">UPI Paid / Secured</span>
          )}
        </p>
      </div>

      {/* Contact Cook */}
      {order.sellerId?.userId?.phone && !['completed', 'cancelled', 'rejected'].includes(order.status) && (
        <div className="bg-white rounded-card border border-marigold-light/50 p-5 mt-4">
          <h2 className="font-medium mb-1">Contact Cook</h2>
          <p className="text-sm text-clay mb-2">Need an update on your food?</p>
          <a href={`tel:${order.sellerId.userId.phone}`} className="inline-block px-4 py-2 bg-marigold-light/40 hover:bg-marigold text-ink rounded-full text-sm font-medium transition">
            📞 Call Cook
          </a>
        </div>
      )}

      {/* Status section */}
      <div className="mt-6">
        <h2 className="font-medium mb-3">Status</h2>
        <StatusStepper status={order.status} fulfillmentType={order.fulfillmentType} />
        {order.status === 'rejected' && order.rejectionReason && (
          <p className="text-sm text-clay mt-2">Reason: {order.rejectionReason}</p>
        )}
      </div>

      {/* Cancel Order Section (for eligible orders) */}
      {canCancel && (
        <div className="bg-white rounded-card border border-marigold-light/50 p-5 mt-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <h2 className="font-medium text-ink">Need to cancel this order?</h2>
              <p className="text-xs text-clay mt-0.5">
                {order.paymentMethod === 'upi'
                  ? 'UPI order: full 100% refund (₹' + order.total + ') back to your account.'
                  : 'Cash order: free cancellation with zero charges.'}
              </p>
            </div>
            <button
              type="button"
              onClick={() => {
                setCancelError('');
                setCancelModalOpen(true);
              }}
              className="px-4 py-2 rounded-full border border-red-300 text-red-700 hover:bg-red-50 text-sm font-medium transition self-start sm:self-auto flex items-center gap-1.5"
            >
              <span>✕</span>
              <span>Cancel Order</span>
            </button>
          </div>
        </div>
      )}

      {/* Cancel Confirmation Modal */}
      {cancelModalOpen && (
        <div className="fixed inset-0 bg-ink/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-card max-w-md w-full p-6 shadow-xl border border-marigold-light/60 animate-in fade-in zoom-in-95 duration-150">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="font-display text-xl text-ink">Cancel Order #{order.orderNumber}?</h3>
                <p className="text-xs text-clay mt-1">Please confirm if you would like to cancel.</p>
              </div>
              <button
                type="button"
                onClick={() => setCancelModalOpen(false)}
                className="text-clay hover:text-ink text-xl leading-none px-1"
              >
                ✕
              </button>
            </div>

            {/* Payment-method specific refund notice */}
            {order.paymentMethod === 'upi' ? (
              <div className="p-3.5 bg-emerald-50/80 border border-emerald-200 rounded-xl mb-4 text-xs text-emerald-900">
                <div className="flex items-center justify-between font-semibold mb-1">
                  <span className="flex items-center gap-1.5 text-tulsi-dark">
                    ⚡ UPI Payment · 100% Refund
                  </span>
                  <span className="font-bold text-sm text-ink">₹{order.total}</span>
                </div>
                <p className="text-emerald-800 leading-relaxed">
                  Your full payment of <strong>₹{order.total}</strong> will be refunded directly to your original UPI account (GPay, PhonePe, Paytm, or bank account). Zero cancellation fees.
                </p>
                <p className="text-[11px] text-emerald-700 mt-1">
                  ⏱ Expected refund credit: within 2–4 hours.
                </p>
              </div>
            ) : (
              <div className="p-3.5 bg-amber-50/80 border border-amber-200 rounded-xl mb-4 text-xs text-amber-900">
                <div className="flex items-center gap-1.5 font-semibold mb-1 text-amber-900">
                  <span>💵 Cash on Fulfillment</span>
                </div>
                <p className="text-amber-800 leading-relaxed">
                  No payment was collected for this order. It will be cancelled immediately at zero charge.
                </p>
              </div>
            )}

            {/* Reason selector */}
            <div className="mb-4">
              <label className="block text-xs font-semibold text-ink uppercase tracking-wider mb-2">
                Reason for cancellation
              </label>
              <div className="space-y-1.5">
                {CANCEL_REASONS.map((reason) => (
                  <label
                    key={reason}
                    className={`flex items-center gap-2.5 p-2.5 rounded-lg border text-xs cursor-pointer transition ${
                      cancelReason === reason
                        ? 'border-tulsi bg-tulsi/5 font-medium text-ink'
                        : 'border-marigold-light/40 hover:bg-ivory text-clay'
                    }`}
                  >
                    <input
                      type="radio"
                      name="cancelReason"
                      value={reason}
                      checked={cancelReason === reason}
                      onChange={(e) => setCancelReason(e.target.value)}
                      className="text-tulsi focus:ring-tulsi"
                    />
                    <span>{reason}</span>
                  </label>
                ))}
              </div>

              {cancelReason === 'Other' && (
                <textarea
                  className="w-full mt-2.5 border border-marigold-light/60 rounded-lg px-3 py-2 text-xs focus-ring"
                  rows={2}
                  placeholder="Please specify why you are cancelling..."
                  value={customCancelReason}
                  onChange={(e) => setCustomCancelReason(e.target.value)}
                />
              )}
            </div>

            {cancelError && (
              <p className="text-red-700 text-xs mb-3 p-2 bg-red-50 border border-red-200 rounded-lg">
                {cancelError}
              </p>
            )}

            {/* Actions */}
            <div className="flex gap-2 justify-end pt-2 border-t border-marigold-light/40">
              <button
                type="button"
                onClick={() => setCancelModalOpen(false)}
                disabled={cancelling}
                className="px-4 py-2 rounded-full border border-marigold-light/60 text-clay hover:text-ink text-xs font-medium"
              >
                Keep Order
              </button>
              <button
                type="button"
                onClick={handleCancelOrder}
                disabled={cancelling}
                className="px-5 py-2 rounded-full bg-red-600 hover:bg-red-700 text-ivory text-xs font-semibold transition disabled:opacity-50 shadow-sm flex items-center gap-1.5"
              >
                {cancelling ? 'Cancelling...' : 'Confirm Cancellation'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Review Form */}
      {order.status === 'completed' && !reviewSubmitted && (
        <form onSubmit={submitReview} className="mt-6 bg-white rounded-card border border-marigold-light/50 p-5">
          <h2 className="font-medium mb-3">Rate this order</h2>
          <div className="flex gap-1 mb-3">
            {[1, 2, 3, 4, 5].map((n) => (
              <button type="button" key={n} onClick={() => setRating(n)} className={`text-2xl ${n <= rating ? 'text-marigold-dark' : 'text-marigold-light'}`}>★</button>
            ))}
          </div>
          <textarea
            className="w-full border border-marigold-light/60 rounded-lg px-3 py-2 mb-3 focus-ring"
            placeholder="How was the food?"
            value={comment}
            onChange={(e) => setComment(e.target.value)}
          />
          {reviewError && <p className="text-red-700 text-sm mb-2">{reviewError}</p>}
          <button className="px-5 py-2 rounded-full bg-marigold text-ink font-medium hover:bg-marigold-dark hover:text-ivory transition">
            Submit review
          </button>
        </form>
      )}
      {reviewSubmitted && <p className="mt-6 text-tulsi-dark">Thanks for your review!</p>}

      {/* Complaints */}
      {['completed', 'rejected'].includes(order.status) && !complaintSubmitted && (
        <div className="mt-6">
          {!complaintOpen ? (
            <button onClick={() => setComplaintOpen(true)} className="text-marigold-dark text-sm underline">
              Report an issue with this order
            </button>
          ) : (
            <form onSubmit={submitComplaint} className="mt-4 border-t border-marigold-light/50 pt-4">
              {complaintError && <p className="text-red-600 text-sm mb-2">{complaintError}</p>}
              <label className="block text-sm text-clay/70 mb-1">What went wrong?</label>
              <select value={complaintCategory} onChange={(e) => setComplaintCategory(e.target.value)} className="w-full border border-marigold-light/60 rounded-lg px-3 py-2 mb-3">
                <option value="food_quality">Food quality</option>
                <option value="missing_item">Missing item</option>
                <option value="wrong_item">Wrong item</option>
                <option value="seller_issue">Seller issue</option>
                <option value="delivery_issue">Delivery issue</option>
                <option value="other">Other</option>
              </select>
              <textarea
                required
                className="w-full border border-marigold-light/60 rounded-lg px-3 py-2 mb-3 focus-ring"
                placeholder="Describe what happened"
                value={complaintDesc}
                onChange={(e) => setComplaintDesc(e.target.value)}
              />
              <button className="px-5 py-2 rounded-full bg-tulsi text-ivory font-medium hover:bg-tulsi-dark transition">
                Submit complaint
              </button>
            </form>
          )}
        </div>
      )}
      {complaintSubmitted && <p className="mt-4 text-tulsi-dark text-sm">Your complaint has been submitted. Our team will look into it.</p>}
    </div>
  );
}
