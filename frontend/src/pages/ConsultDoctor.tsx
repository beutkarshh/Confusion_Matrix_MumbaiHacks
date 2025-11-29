import { useState } from "react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import MainNavbar from "@/components/MainNavbar"
import BookAppointment from "@/components/BookAppointment"
import MyAppointments from "@/components/MyAppointments"
import { Calendar, MessageSquare, Video, Clock } from "lucide-react"

const ConsultDoctor = () => {
  const [activeTab, setActiveTab] = useState("book")

  const handleBookingComplete = (appointment: any) => {
    // Switch to appointments tab after successful booking
    setActiveTab("appointments")
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-100">
      <MainNavbar />
      
      <div className="flex justify-center items-start py-10 px-4">
        <div className="w-full max-w-7xl">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="bg-gradient-to-r from-emerald-600 to-green-400 p-8 rounded-3xl text-white mb-6">
              <h1 className="text-4xl font-bold mb-2">Consult a Doctor</h1>
              <p className="text-blue-100 text-lg font-medium">
                Book appointments, join video consultations, and manage your health
              </p>
            </div>
          </div>

          {/* Main Content */}
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="grid w-full grid-cols-3 mb-6">
              <TabsTrigger value="book" className="flex items-center gap-2">
                <Calendar className="w-4 h-4" />
                Book Appointment
              </TabsTrigger>
              <TabsTrigger value="appointments" className="flex items-center gap-2">
                <Clock className="w-4 h-4" />
                My Appointments
              </TabsTrigger>
              <TabsTrigger value="chat" className="flex items-center gap-2">
                <MessageSquare className="w-4 h-4" />
                Chat Consultation
              </TabsTrigger>
            </TabsList>

            <TabsContent value="book" className="space-y-6">
              <BookAppointment onBookingComplete={handleBookingComplete} />
            </TabsContent>

            <TabsContent value="appointments" className="space-y-6">
              <MyAppointments />
            </TabsContent>

            <TabsContent value="chat" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <MessageSquare className="w-5 h-5" />
                    Chat Consultation
                  </CardTitle>
                  <CardDescription>
                    Get quick advice through our chat system
                  </CardDescription>
                </CardHeader>
                <CardContent>
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
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  )
}

export default ConsultDoctor;
