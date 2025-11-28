import MainNavbar from "@/components/MainNavbar";

const ConsultDoctor = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-100">
      <MainNavbar />
      <div className="flex justify-center items-start py-10 px-4">
        <div className="w-full max-w-5xl bg-white shadow-2xl rounded-3xl overflow-hidden border border-gray-200">
          <div className="bg-gradient-to-r from-emerald-600 to-green-400 p-8 text-center text-white">
            <h1 className="text-4xl font-bold mb-2">Consult a Doctor</h1>
            <p className="text-blue-100 text-sm font-medium">
              Book an appointment or join an online consultation
            </p>
          </div>

          <div className="p-8 space-y-10">
            <div className="bg-blue-50 border border-blue-200 rounded-2xl p-6 shadow-inner">
              <h2 className="text-2xl font-semibold text-zinc-900 mb-4">Book an Appointment</h2>
              <p className="text-sm text-gray-600">
                In the hackathon demo, this section is static UI inspired by your
                  original app. You can later wire this to a real scheduling backend.
              </p>
            </div>

            <div className="bg-gray-50 border border-gray-200 rounded-2xl p-6">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">Chat Consultation</h2>
              <div className="bg-white border border-gray-300 rounded-lg p-4 h-64 overflow-y-auto shadow-inner">
                <div className="text-center text-gray-500 mt-20">
                  <div className="text-6xl mb-4 animate-bounce">💬</div>
                  <p className="text-lg font-medium">Start chatting with a doctor</p>
                  <p className="text-sm text-gray-400">
                    Type your message below to begin the conversation
                  </p>
                </div>
              </div>
              <div className="mt-4 flex gap-2">
                <input
                  type="text"
                  placeholder="Type your message..."
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                />
                <button className="bg-green-600 hover:bg-green-700 text-white font-semibold py-2 px-5 rounded-lg transition-all shadow">
                  Send
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ConsultDoctor;
