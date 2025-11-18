import { useEffect, useState, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import data from "../data/courses.json"; 

export default function Home() {
  const [courses, setCourses] = useState([]);
  const navigate = useNavigate();

  // Load JSON once
  useEffect(() => {
    setCourses(data);
  }, []);

  // Group by category
  const grouped = useMemo(() => {
    return courses.reduce((acc, course) => {
      if (!acc[course.category]) acc[course.category] = [];
      acc[course.category].push(course);
      return acc;
    }, {});
  }, [courses]);

  // "View Details" button click
  const handleViewDetails = (course) => {
    navigate(`/course/${course.id}`, { state: { course, courseId: course.id } });

  };

  return (
    <div className="p-6 space-y-10">
      <h1 className="text-3xl font-bold">Browse Courses</h1>

      {Object.keys(grouped).map((category) => (
        <section key={category} className="space-y-4">
          <h2 className="text-2xl font-semibold">{category}</h2>

          {/* Horizontal scroll container */}
          <div className="flex gap-5 overflow-x-auto pb-3">
            {grouped[category].map((course) => (
              <CourseCard
                key={course.id}
                course={course}
                onView={handleViewDetails}
              />
            ))}
          </div>
        </section>
      ))}
    </div>
  );
}


// Course Card Component

function CourseCard({ course, onView }) {
  return (
    <article className="w-72 shrink-0 rounded-2xl border border-neutral-800 bg-neutral-900 p-3 shadow-sm hover:shadow transition">
      <img
        src={course.thumbnail}
        alt={course.title}
        className="h-40 w-full object-cover rounded-xl mb-3"
      />
      <h3 className="font-semibold leading-snug line-clamp-2">{course.title}</h3>
      <p className="text-xs text-neutral-400">{course.instructor}</p>
      <p className="text-sm text-neutral-300 my-2 line-clamp-2">{course.description}</p>

      <div className="flex items-center justify-between pt-1">
        <span className="font-semibold">${course.price}</span>
        <button
          onClick={() => onView(course)}
          className="px-4 py-2 rounded-xl border hover:bg-gray-50"
        >
          View Details
        </button>
      </div>
    </article>
  );
}
