import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

export default function CourseDetails() {
  const { id } = useParams();               // expects routes like /course/B2
  const navigate = useNavigate();
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState("");

  useEffect(() => {
    let alive = true;
    (async () => {
      try {
        const res = await fetch("/src/data/courses.json");
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        if (alive) setCourses(data);
      } catch (e) {
        setErr("Could not load course info. Make sure courseinfo.json is in /public.");
      } finally {
        if (alive) setLoading(false);
      }
    })();
    return () => { alive = false; };
  }, []);

  const course = useMemo(
    () => courses.find((c) => c.id.toUpperCase() === String(id).toUpperCase()),
    [courses, id]
  );

  if (loading) {
    return (
      <div className="max-w-5xl mx-auto p-6">
        <div className="animate-pulse h-6 w-40 bg-gray-300 rounded mb-4" />
        <div className="animate-pulse h-64 bg-gray-200 rounded" />
      </div>
    );
  }

  if (err) {
    return <div className="max-w-3xl mx-auto p-6 text-red-600">{err}</div>;
  }

  if (!course) {
    return (
      <div className="max-w-3xl mx-auto p-6">
        <p className="text-gray-700">Course not found.</p>
      </div>
    );
  }

  const {
    title,
    instructor,
    category,
    duration,
    price,
    description,
    trailerUrl,
    courseUrl,
    thumbnail,
  } = course;

  const enroll = () => {
    // hand off the course object to Payment/Confirmation page
    navigate("/payment", { state: { course } });
  };

  return (
    <div className="max-w-5xl mx-auto p-6">
      <div className="grid md:grid-cols-2 gap-6">
        <div className="overflow-hidden rounded-2xl shadow">
          <img
            src={thumbnail?.startsWith("/") ? thumbnail : `/images/${id}.jpg`}
            alt={title}
            className="w-full h-full object-cover"
          />
        </div>

        <div className="space-y-3">
          <h1 className="text-3xl font-semibold">{title}</h1>
          <p className="text-gray-700">By <span className="font-medium">{instructor}</span></p>
          <div className="flex flex-wrap gap-3 text-gray-700">
            <span className="px-3 py-1 rounded-full bg-gray-100">{category}</span>
            <span className="px-3 py-1 rounded-full bg-gray-100">{duration}</span>
          </div>

          <p className="text-gray-800 leading-relaxed">{description}</p>

          <div className="pt-2">
            <p className="text-2xl font-bold">${Number(price).toFixed(2)}</p>
          </div>

          <div className="flex flex-wrap gap-3 pt-2">
            <a
              href={trailerUrl}
              target="_blank"
              rel="noreferrer"
              className="px-4 py-2 rounded-xl border hover:bg-gray-50"
            >
              Watch Trailer
            </a>
            <a
              href={courseUrl}
              target="_blank"
              rel="noreferrer"
              className="px-4 py-2 rounded-xl border hover:bg-gray-50"
            >
              Course Page
            </a>
            <button
              onClick={enroll}
              className="px-5 py-2 rounded-xl bg-black text-white hover:opacity-90"
            >
              Enroll Now
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
