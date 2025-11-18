import { useLocation, useNavigate, useParams } from "react-router-dom";
import { useMemo, useState } from "react";
import data from "../data/courses.json"; // your local JSON array

export default function Enroll() {
  const { state } = useLocation();               // expect { course }
  const { id } = useParams();                    // backup: /enroll/:id
  const navigate = useNavigate();

  // Prefer course from route state; fall back to lookup by id if user refreshed
  const course = useMemo(() => {
    if (state?.course) return state.course;
    if (id) return data.find(c => String(c.id) === String(id));
    return null;
  }, [state, id]);

  // ---- form state ----
  const [fullName, setFullName] = useState("");
  const [email, setEmail]       = useState("");
  const [start, setStart]       = useState("");
  const [mode, setMode]         = useState("Online");
  const [message, setMessage]   = useState("");
  const [errors, setErrors]     = useState({});

  // ---- validate ----
  const validate = () => {
    const e = {};
    if (!fullName.trim()) e.fullName = "Full name is required.";
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) e.email = "Enter a valid email.";
    if (!start) e.start = "Please choose a start date.";
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  // ---- submit ----
  const onSubmit = (ev) => {
    ev.preventDefault();
    if (!validate()) return;

    const payload = {
      courseId: course?.id ?? id ?? null,
      courseTitle: course?.title ?? "",
      user: { fullName, email },
      enrollment: { start, mode, message }
    };

    // go to Payment & Confirmation view, pass state
    navigate("/confirmation", { state: { course, form: payload } });
  };

  return (
    <div className="max-w-3xl mx-auto p-6 space-y-6">
      <header className="space-y-1">
        <h1 className="text-2xl font-bold">Enroll</h1>
        <p className="text-gray-700">
          Course: <span className="font-semibold">{course?.title || "—"}</span>
        </p>
      </header>

      <form onSubmit={onSubmit} className="space-y-6">
        {/* User Information */}
        <fieldset className="border rounded-2xl p-4">
          <legend className="px-2 text-sm font-semibold">User Information</legend>

          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <label className="block text-sm mb-1">Full Name</label>
              <input
                className="w-full border rounded-lg p-2"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="Jane Doe"
              />
              {errors.fullName && <p className="text-sm text-red-600 mt-1">{errors.fullName}</p>}
            </div>

            <div>
              <label className="block text-sm mb-1">Email</label>
              <input
                className="w-full border rounded-lg p-2"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="jane@example.com"
              />
              {errors.email && <p className="text-sm text-red-600 mt-1">{errors.email}</p>}
            </div>
          </div>
        </fieldset>

        {/* Enrollment Details */}
        <fieldset className="border rounded-2xl p-4">
          <legend className="px-2 text-sm font-semibold">Enrollment Details</legend>

          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <label className="block text-sm mb-1">Preferred Start Date</label>
              <input
                type="date"
                className="w-full border rounded-lg p-2"
                value={start}
                onChange={(e) => setStart(e.target.value)}
              />
              {errors.start && <p className="text-sm text-red-600 mt-1">{errors.start}</p>}
            </div>

            <div>
              <label className="block text-sm mb-1">Mode</label>
              <select
                className="w-full border rounded-lg p-2"
                value={mode}
                onChange={(e) => setMode(e.target.value)}
              >
                <option>Online</option>
                <option>In-Person</option>
              </select>
            </div>
          </div>

          <div className="mt-4">
            <label className="block text-sm mb-1">Message to Instructor (optional)</label>
            <textarea
              rows={3}
              className="w-full border rounded-lg p-2"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Anything you'd like us to know?"
            />
          </div>
        </fieldset>

        <div className="flex justify-end gap-3">
          <button
            type="button"
            onClick={() => window.history.back()}
            className="px-4 py-2 rounded border"
          >
            Back
          </button>
          <button
            type="submit"
            className="px-4 py-2 rounded bg-red-600 text-white hover:bg-red-700"
          >
            Continue to Payment
          </button>
        </div>
      </form>
    </div>
  );
}
