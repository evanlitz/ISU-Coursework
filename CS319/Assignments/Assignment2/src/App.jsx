import { Routes, Route, Navigate } from "react-router-dom";
import Navbar from "./components/Navbar.jsx";
import Home from "./components/Home.jsx";
import CourseDetails from "./components/CourseDetails.jsx";
import EnrollmentForm from "./components/EnrollmentForm.jsx";
import PaymentConfirmation from "./components/PaymentConfirmation.jsx";

export default function App() {
  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-100">
      <Navbar />
      <main className="max-w-6xl mx-auto px-4 py-8">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/course/:id" element={<CourseDetails />} />
          <Route path="/payment" element={<EnrollmentForm />} />
          <Route path="/confirmation" element={<PaymentConfirmation />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  );
}

