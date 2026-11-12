const PICKUP_STEPS = ['placed', 'accepted', 'preparing', 'ready', 'completed'];
const DELIVERY_STEPS = ['placed', 'accepted', 'preparing', 'ready', 'out_for_delivery', 'completed'];

const LABELS = {
  placed: 'Order placed',
  accepted: 'Accepted by cook',
  preparing: 'Preparing',
  ready: 'Ready',
  out_for_delivery: 'Out for delivery',
  completed: 'Completed',
};

export default function StatusStepper({ status, fulfillmentType }) {
  if (status === 'rejected') {
    return <p className="text-red-700 font-medium">This order was rejected by the cook.</p>;
  }
  if (status === 'cancelled') {
    return (
      <div className="flex items-center gap-3 p-3.5 bg-red-50/80 border border-red-200 rounded-xl text-red-700">
        <span className="w-7 h-7 rounded-full bg-red-100 flex items-center justify-center font-bold text-red-600 flex-shrink-0">✕</span>
        <div>
          <p className="font-medium text-sm text-red-800">Order Cancelled</p>
          <p className="text-xs text-red-600 mt-0.5">This order has been cancelled and is no longer being processed.</p>
        </div>
      </div>
    );
  }

  const steps = fulfillmentType === 'delivery' ? DELIVERY_STEPS : PICKUP_STEPS;
  const currentIndex = steps.indexOf(status);

  return (
    <div className="flex flex-col gap-2">
      {steps.map((step, i) => (
        <div key={step} className="flex items-center gap-3">
          <div
            className={`w-3 h-3 rounded-full flex-shrink-0 ${
              i <= currentIndex ? 'bg-tulsi' : 'bg-marigold-light/50'
            }`}
          />
          <span className={i <= currentIndex ? 'text-ink font-medium' : 'text-clay'}>{LABELS[step]}</span>
        </div>
      ))}
    </div>
  );
}
