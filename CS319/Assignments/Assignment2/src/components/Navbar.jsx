import { NavLink, useNavigate } from "react-router-dom";

export default function Navbar() {
  const navigate = useNavigate();
  return (
    <header className="sticky top-0 z-50 border-b border-neutral-800/60 bg-neutral-950/80 backdrop-blur">
      <div className="max-w-6xl mx-auto px-4 h-14 flex items-center justify-between">
        <button
          onClick={() => navigate("/")}
          className="text-lg font-semibold tracking-tight hover:opacity-90"
          aria-label="Go home"
        >
          Code & Cook Collective
        </button>

        <nav className="flex items-center gap-6 text-sm">
          <NavLink
            to="/"
            className={({ isActive }) =>
              `hover:text-white/90 ${isActive ? "text-white" : "text-white/70"}`
            }
          >
            Home
          </NavLink>

          
          <a
            href="https://www.udemy.com/topic/cooking/"
            target="_blank"
            rel="noreferrer"
            className="text-white/70 hover:text-white/90"
          >
            Explore
          </a>

          <a
            href="https://www.udemy.com/topic/cooking/"
            target="_blank"
            rel="noreferrer"
            className="px-4 py-2 rounded-xl border hover:bg-gray-50"
          >
            Get Started
          </a>
        </nav>
      </div>
    </header>
  );
}
