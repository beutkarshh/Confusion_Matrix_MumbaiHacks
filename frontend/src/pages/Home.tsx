import MainNavbar from "@/components/MainNavbar";
import { Link } from "react-router-dom";
import homeBg from "@/assets/hero-medical.jpg";

const Home = () => {
  const services = [
    { label: "Telemedicine", icon: (
      <svg className="w-7 h-7" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
      </svg>
    ) },
    { label: "Digital Health Records", icon: (
      <svg className="w-7 h-7" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4M7 7h10a2 2 0 012 2v8a2 2 0 01-2 2H7a2 2 0 01-2-2V9a2 2 0 012-2z" />
      </svg>
    ) },
    { label: "Medicine Availability", icon: (
      <svg className="w-7 h-7" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 3v12a4 4 0 108 0V3M7 13h10" />
      </svg>
    ) },
    { label: "AI Symptom Checker", icon: (
      <svg className="w-7 h-7" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15M4.5 12h15M8 8l8 8M16 8l-8 8" />
      </svg>
    ) },
    { label: "Offline Access", icon: (
      <svg className="w-7 h-7" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" d="M3 12h18M5 19h14M5 5h14" />
      </svg>
    ) },
  ];

  return (
    <div className="min-h-screen bg-muted/20">
      <MainNavbar />
      <div className="w-full font-sans">
      <section
        className="relative w-screen left-1/2 right-1/2 ml-[-50vw] mr-[-50vw] pt-14 min-h-[75vh] md:min-h-[85vh] flex items-center justify-center"
        style={{ backgroundImage: `url(${homeBg})`, backgroundSize: "cover", backgroundPosition: "center" }}
      >
        <div className="absolute inset-0 bg-gradient-to-b from-black/70 via-black/40 to-transparent" />
        <div className="relative z-10 text-center max-w-3xl px-6 py-12">
          <p className="text-sm md:text-base tracking-wider text-emerald-200 uppercase mb-3">
            Bridging Healthcare Gaps in Villages
          </p>
          <h1 className="text-4xl md:text-6xl font-extrabold text-white leading-tight mb-6 drop-shadow-lg">
            Better Healthcare Access for Rural Areas
          </h1>
          <p className="text-lg text-gray-100 mb-8 max-w-2xl mx-auto">
            MedsAI brings doctors, medicines, and AI diagnosis to every village — anytime, anywhere.
          </p>
          <div className="flex flex-col sm:flex-row justify-center gap-4">
            <Link
              to="/login"
              className="inline-flex items-center justify-center rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white px-6 py-3 text-base font-semibold shadow-lg hover:shadow-emerald-200/40 transition"
            >
              Get Started
            </Link>
            <a
              href="#about"
              className="inline-flex items-center justify-center rounded-lg border border-white/80 text-white hover:bg-white hover:text-gray-900 px-6 py-3 text-base font-semibold transition"
            >
              Learn More
            </a>
          </div>
        </div>
      </section>

      <section className="max-w-7xl mx-auto px-6 -mt-10 md:-mt-14 relative z-20">
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4 md:gap-6">
          {services.map((s) => (
            <div
              key={s.label}
              className="group bg-white/90 backdrop-blur-md rounded-xl shadow-md hover:shadow-xl transition transform hover:-translate-y-1 hover:scale-[1.02] p-5 flex flex-col items-center text-center border border-transparent hover:border-emerald-100"
            >
              <div className="w-12 h-12 rounded-full bg-emerald-50 text-emerald-700 flex items-center justify-center mb-3 group-hover:bg-emerald-100 transition">
                {s.icon}
              </div>
              <span className="text-sm md:text-base font-medium text-gray-800">{s.label}</span>
            </div>
          ))}
        </div>
      </section>

      <section id="about" className="bg-white">
        <div className="max-w-4xl mx-auto px-6 py-16 md:py-20 text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-6">Healthcare Challenges in Rural Areas</h2>
          <p className="text-base md:text-lg text-gray-600 leading-relaxed">
            Rural areas face limited access to medical facilities, delayed treatment, and lack of record digitization.
            MedsAI simplifies these challenges with telemedicine, digital records, and AI-powered diagnosis — in one place.
          </p>
        </div>
      </section>

      <section className="bg-gradient-to-b from-gray-50 to-white">
        <div className="max-w-5xl mx-auto px-6 py-16 md:py-20">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 text-center mb-10">Our Solution for Rural Healthcare</h2>
          <ul className="grid grid-cols-1 sm:grid-cols-2 gap-4 md:gap-6">
            {[
              "Multilingual Telemedicine App",
              "Digital Health Records with Offline Access",
              "Real-time Medicine Availability",
              "AI-powered Symptom Checker",
              "Scalable and Inclusive Health Model",
            ].map((item) => (
              <li
                key={item}
                className="flex items-start gap-3 bg-white rounded-xl p-4 shadow-md hover:shadow-lg transition border border-gray-100 hover:border-emerald-100"
              >
                <span className="mt-1 inline-flex items-center justify-center w-6 h-6 rounded-full bg-emerald-100 text-emerald-700">
                  <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                  </svg>
                </span>
                <span className="text-gray-800 font-medium">{item}</span>
              </li>
            ))}
          </ul>
        </div>
      </section>
      </div>
    </div>
  );
};

export default Home;
