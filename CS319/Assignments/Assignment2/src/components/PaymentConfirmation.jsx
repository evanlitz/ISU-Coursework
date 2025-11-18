import { useLocation, useNavigate } from "react-router-dom";
import { useMemo, useState, useEffect } from "react";
import courses from "../data/courses.json";

export default function PaymentConfirmation() {
  const navigate = useNavigate();
  const { state } = useLocation(); // { course, form }
  const passedCourse = state?.course;
  const form = state?.form; // {courseId, courseTitle, user:{}, enrollment:{}}

  // Resolve course (prefer passed object; fallback by id/title from JSON)
  const course = useMemo(() => {
    if (passedCourse) return passedCourse;
    if (form?.courseId) {
      const byId = courses.find((c) => String(c.id) === String(form.courseId));
      if (byId) return byId;
    }
    if (form?.courseTitle) {
      const byTitle = courses.find((c) => c.title === form.courseTitle);
      if (byTitle) return byTitle;
    }
    return null;
  }, [passedCourse, form]);

  // if someone lands here directly
  useEffect(() => {
    if (!form || !course) {
      // send them home to start fresh
      navigate("/", { replace: true });
    }
  }, [form, course, navigate]);

  if (!form || !course) return null;

  const price = Number(course.price ?? 0);
  const fees  = Math.max(1.99, Number((price * 0.025).toFixed(2)));
  const tax   = Number((price * 0.06).toFixed(2));
  const total = Number((price + fees + tax).toFixed(2));

  // ----- Payment form state -----
  const [cardName, setCardName] = useState("");
  const [cardNum,  setCardNum]  = useState("");
  const [exp,      setExp]      = useState("");
  const [cvv,      setCvv]      = useState("");

  const [bill, setBill] = useState({ line1:"", line2:"", city:"", state:"", zip:"", country:"" });
  const [shipSame, setShipSame] = useState(true);
  const [ship, setShip] = useState({ line1:"", line2:"", city:"", state:"", zip:"", country:"" });

  const [errors, setErrors] = useState({});
  const [paid, setPaid] = useState(false);
  const [txnId, setTxnId] = useState("");

  useEffect(() => { if (shipSame) setShip(bill); }, [shipSame, bill]);

  const validate = () => {
    const e = {};
    if (!cardName.trim()) e.cardName = "Cardholder name required.";
    if (!/^\d{13,19}$/.test(cardNum.replace(/\s+/g, ""))) e.cardNum = "Enter a valid card number.";
    if (!/^\d{2}\/\d{2}$/.test(exp)) e.exp = "Use MM/YY format.";
    if (!/^\d{3,4}$/.test(cvv)) e.cvv = "CVV must be 3–4 digits.";
    if (!bill.line1.trim()) e.bill = "Billing address line 1 required.";
    if (!bill.city.trim() || !bill.state.trim() || !bill.zip.trim())
      e.bill2 = "City / State / ZIP required.";
    if (!shipSame) {
      if (!ship.line1.trim()) e.ship = "Shipping address line 1 required.";
      if (!ship.city.trim() || !ship.state.trim() || !ship.zip.trim())
        e.ship2 = "City / State / ZIP required.";
    }
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const confirmPay = (e) => {
    e.preventDefault();
    if (!validate()) return;
    const id = "TXN-" + Math.random().toString(36).slice(2, 10).toUpperCase();
    setTxnId(id);
    setPaid(true);
  };

  const goHomeReset = () => navigate("/", { replace: true });

  // -------- SUCCESS PANEL --------
  if (paid) {
    return (
      <div className="max-w-4xl mx-auto p-6 space-y-6">
        <div className="rounded-2xl border border-green-500 bg-green-500/10 p-6">
          <h1 className="text-2xl font-semibold text-green-400">Payment Successful</h1>
          <p className="mt-2 text-gray-200">
            Enrollment confirmed for <span className="font-medium">{course.title}</span>.
          </p>
          <p className="mt-1 text-sm text-gray-400">
            Transaction ID: <span className="font-mono">{txnId}</span>
          </p>
        </div>

        <div className="rounded-2xl border p-6 space-y-2">
          <h2 className="text-lg font-semibold">Order Summary</h2>
          <div className="flex items-center gap-4">
            <img src={course.thumbnail} alt={course.title} className="w-24 h-24 rounded-xl object-cover" />
            <div className="flex-1">
              <p className="font-medium">{course.title}</p>
              <p className="text-sm text-gray-400">Course ID: {course.id}</p>
              <p className="text-sm text-gray-400">
                Student: {form.user.fullName} • {form.user.email}
              </p>
              <p className="text-sm text-gray-400">
                Start: {form.enrollment.start} • Mode: {form.enrollment.mode}
              </p>
            </div>
            <div className="text-right">
              <p className="font-semibold">${price.toFixed(2)}</p>
              <p className="text-sm text-gray-400">Total paid: ${total.toFixed(2)}</p>
            </div>
          </div>
        </div>

        <button
          onClick={goHomeReset}
          className="px-5 py-2 rounded-xl bg-indigo-600 text-white hover:bg-indigo-500"
        >
          Return Home
        </button>
      </div>
    );
  }

  // -------- PAYMENT FORM + ORDER SUMMARY --------
  return (
    <div className="max-w-5xl mx-auto p-6 space-y-6">
      <h1 className="text-2xl font-semibold">Payment & Confirmation</h1>

      {/* Order summary */}
      <div className="rounded-2xl border p-5">
        <h2 className="text-lg font-semibold mb-4">Order Summary</h2>
        <div className="flex items-center gap-4">
          <img src={course.thumbnail} alt={course.title} className="w-24 h-24 object-cover rounded-xl" />
          <div className="flex-1">
            <p className="font-medium">{course.title}</p>
            <p className="text-sm text-gray-400">Course ID: {course.id}</p>
            <p className="text-sm text-gray-400">
              Student: {form.user.fullName} • {form.user.email}
            </p>
            <p className="text-sm text-gray-400">
              Start: {form.enrollment.start} • Mode: {form.enrollment.mode}
            </p>
          </div>
          <div className="text-right">
            <p className="font-semibold">${price.toFixed(2)}</p>
            <p className="text-sm text-gray-400">Fees: ${fees.toFixed(2)}</p>
            <p className="text-sm text-gray-400">Tax: ${tax.toFixed(2)}</p>
            <p className="font-semibold mt-1">Total: ${total.toFixed(2)}</p>
          </div>
        </div>
      </div>

      {/* Two-section form */}
      <form onSubmit={confirmPay} className="grid gap-6 md:grid-cols-2">
        {/* Payment details */}
        <section className="rounded-2xl border p-5 space-y-4">
          <h2 className="text-lg font-semibold">Payment Details</h2>

          <div>
            <label className="block text-sm mb-1">Cardholder Name</label>
            <input
              className="w-full rounded-lg border bg-transparent p-2"
              value={cardName}
              onChange={(e) => setCardName(e.target.value)}
              placeholder="Jane Doe"
            />
            {errors.cardName && <p className="text-sm text-red-500 mt-1">{errors.cardName}</p>}
          </div>

          <div>
            <label className="block text-sm mb-1">Card Number</label>
            <input
              className="w-full rounded-lg border bg-transparent p-2"
              inputMode="numeric"
              placeholder="4242 4242 4242 4242"
              value={cardNum}
              onChange={(e) => setCardNum(e.target.value.replace(/[^\d\s]/g, ""))}
            />
            {errors.cardNum && <p className="text-sm text-red-500 mt-1">{errors.cardNum}</p>}
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm mb-1">Expiry (MM/YY)</label>
              <input
                className="w-full rounded-lg border bg-transparent p-2"
                placeholder="02/28"
                value={exp}
                onChange={(e) => setExp(e.target.value)}
              />
              {errors.exp && <p className="text-sm text-red-500 mt-1">{errors.exp}</p>}
            </div>
            <div>
              <label className="block text-sm mb-1">CVV</label>
              <input
                className="w-full rounded-lg border bg-transparent p-2"
                inputMode="numeric"
                placeholder="123"
                value={cvv}
                onChange={(e) => setCvv(e.target.value.replace(/\D/g, ""))}
              />
              {errors.cvv && <p className="text-sm text-red-500 mt-1">{errors.cvv}</p>}
            </div>
          </div>
        </section>

        {/* Billing & Shipping */}
        <section className="rounded-2xl border p-5 space-y-4">
          <h2 className="text-lg font-semibold">Billing & Shipping</h2>

          <AddressBlock
            title="Billing Address"
            value={bill}
            onChange={setBill}
            errors={{ bill: errors.bill, bill2: errors.bill2 }}
          />

          <div className="flex items-center gap-2">
            <input
              id="same"
              type="checkbox"
              className="h-4 w-4"
              checked={shipSame}
              onChange={(e) => setShipSame(e.target.checked)}
            />
            <label htmlFor="same" className="text-sm">Shipping same as billing</label>
          </div>

          {!shipSame && (
            <AddressBlock
              title="Shipping Address"
              value={ship}
              onChange={setShip}
              errors={{ ship: errors.ship, ship2: errors.ship2 }}
            />
          )}
        </section>

        <div className="md:col-span-2 flex justify-end gap-3">
          <button
            type="button"
            onClick={() => navigate(-1)}
            className="px-4 py-2 rounded-lg border hover:bg-white/5"
          >
            Back
          </button>
          <button
            type="submit"
            className="px-5 py-2 rounded-lg bg-indigo-600 text-white hover:bg-indigo-500"
          >
            Confirm Payment
          </button>
        </div>
      </form>
    </div>
  );
}

function AddressBlock({ title, value, onChange, errors }) {
  return (
    <div className="space-y-3">
      <p className="font-medium">{title}</p>
      <input
        className="w-full rounded-lg border bg-transparent p-2"
        placeholder="Address line 1"
        value={value.line1}
        onChange={(e) => onChange({ ...value, line1: e.target.value })}
      />
      <input
        className="w-full rounded-lg border bg-transparent p-2"
        placeholder="Address line 2 (optional)"
        value={value.line2}
        onChange={(e) => onChange({ ...value, line2: e.target.value })}
      />

      <div className="grid grid-cols-3 gap-3">
        <input
          className="rounded-lg border bg-transparent p-2"
          placeholder="City"
          value={value.city}
          onChange={(e) => onChange({ ...value, city: e.target.value })}
        />
        <input
          className="rounded-lg border bg-transparent p-2"
          placeholder="State"
          value={value.state}
          onChange={(e) => onChange({ ...value, state: e.target.value })}
        />
        <input
          className="rounded-lg border bg-transparent p-2"
          placeholder="ZIP"
          value={value.zip}
          onChange={(e) => onChange({ ...value, zip: e.target.value })}
        />
      </div>

      <input
        className="w-full rounded-lg border bg-transparent p-2"
        placeholder="Country"
        value={value.country}
        onChange={(e) => onChange({ ...value, country: e.target.value })}
      />

      {(errors.bill || errors.bill2 || errors.ship || errors.ship2) && (
        <p className="text-sm text-red-500">
          {errors.bill || errors.bill2 || errors.ship || errors.ship2}
        </p>
      )}
    </div>
  );
}
