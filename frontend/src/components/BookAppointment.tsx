import { useState, useEffect } from 'react'
import { Calendar } from "@/components/ui/calendar"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { toast } from "@/hooks/use-toast"
import { CalendarDays, Clock, User, Stethoscope, MapPin } from "lucide-react"
import { format, parseISO, isToday, isTomorrow } from "date-fns"
import { getDoctors, getAvailableSlots, bookAppointment, type Doctor, type AppointmentSlot } from "@/services/api"

interface BookAppointmentProps {
  onBookingComplete?: (appointment: any) => void
}

export default function BookAppointment({ onBookingComplete }: BookAppointmentProps) {
  const [selectedDoctor, setSelectedDoctor] = useState<Doctor | null>(null)
  const [selectedDate, setSelectedDate] = useState<Date>()
  const [selectedSlot, setSelectedSlot] = useState<AppointmentSlot | null>(null)
  const [doctors, setDoctors] = useState<Doctor[]>([])
  const [availableSlots, setAvailableSlots] = useState<AppointmentSlot[]>([])
  const [symptoms, setSymptoms] = useState("")
  const [notes, setNotes] = useState("")
  const [loading, setLoading] = useState(false)
  const [loadingSlots, setLoadingSlots] = useState(false)
  const [currentUserId, setCurrentUserId] = useState<string | null>(null)

  // Check for auth token on mount
  useEffect(() => {
    const authToken = localStorage.getItem('authToken')
    setCurrentUserId(authToken)
  }, [])

  // Quick auth for testing
  const setQuickAuth = (userId: string, userName: string) => {
    localStorage.setItem('authToken', userId)
    setCurrentUserId(userId)
    toast({
      title: "Authentication Set",
      description: `Logged in as ${userName} (ID: ${userId})`
    })
  }

  // Load doctors on component mount
  useEffect(() => {
    const loadDoctors = async () => {
      try {
        setLoading(true)
        const doctorsData = await getDoctors()
        setDoctors(doctorsData)
      } catch (error) {
        console.error('Failed to load doctors:', error)
        toast({
          variant: "destructive",
          title: "Error",
          description: "Failed to load available doctors"
        })
      } finally {
        setLoading(false)
      }
    }

    loadDoctors()
  }, [])

  // Load slots when doctor and date are selected
  useEffect(() => {
    if (selectedDoctor && selectedDate) {
      const loadSlots = async () => {
        try {
          setLoadingSlots(true)
          const dateStr = format(selectedDate, 'yyyy-MM-dd')
          const slotsData = await getAvailableSlots(selectedDoctor.id, dateStr)
          setAvailableSlots(slotsData.available_slots)
        } catch (error) {
          console.error('Failed to load slots:', error)
          toast({
            variant: "destructive",
            title: "Error",
            description: "Failed to load available time slots"
          })
          setAvailableSlots([])
        } finally {
          setLoadingSlots(false)
        }
      }

      loadSlots()
    } else {
      setAvailableSlots([])
    }
  }, [selectedDoctor, selectedDate])

  const handleBooking = async () => {
    if (!selectedSlot) return

    try {
      setLoading(true)
      
      const result = await bookAppointment(selectedSlot.id, symptoms, notes)
      
      if (result.success) {
        toast({
          title: "Success!",
          description: `Your appointment has been booked with Dr. ${selectedDoctor?.user.name}`
        })
        
        // Reset form
        setSelectedSlot(null)
        setSymptoms("")
        setNotes("")
        
        // Call callback if provided
        onBookingComplete?.(result.appointment)
      } else {
        toast({
          variant: "destructive",
          title: "Booking Failed",
          description: result.error || "Failed to book appointment"
        })
      }
    } catch (error) {
      console.error('Booking error:', error)
      toast({
        variant: "destructive",
        title: "Error",
        description: "An unexpected error occurred"
      })
    } finally {
      setLoading(false)
    }
  }

  const formatSlotTime = (slot: AppointmentSlot) => {
    const start = parseISO(slot.start_datetime)
    const end = parseISO(slot.end_datetime)
    return `${format(start, 'HH:mm')} - ${format(end, 'HH:mm')}`
  }

  const getDateLabel = (date: Date) => {
    if (isToday(date)) return "Today"
    if (isTomorrow(date)) return "Tomorrow"
    return format(date, 'EEEE, MMM d')
  }

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      {/* Authentication Section */}
      {!currentUserId && (
        <Card className="bg-blue-50 border-blue-200">
          <CardHeader>
            <CardTitle className="text-blue-900">Quick Login (Development Mode)</CardTitle>
            <CardDescription className="text-blue-700">
              Choose a test patient to book appointments
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              <Button onClick={() => setQuickAuth('5', 'Alice Johnson')} variant="outline" size="sm">
                Login as Alice Johnson
              </Button>
              <Button onClick={() => setQuickAuth('6', 'Bob Smith')} variant="outline" size="sm">
                Login as Bob Smith
              </Button>
              <Button onClick={() => setQuickAuth('7', 'Carol Davis')} variant="outline" size="sm">
                Login as Carol Davis
              </Button>
              <Button onClick={() => setQuickAuth('8', 'David Wilson')} variant="outline" size="sm">
                Login as David Wilson
              </Button>
              <Button onClick={() => setQuickAuth('9', 'Emma Brown')} variant="outline" size="sm">
                Login as Emma Brown
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {currentUserId && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-green-800">
              <User className="w-5 h-5" />
              <span>Logged in as Patient ID: {currentUserId}</span>
            </div>
            <Button 
              onClick={() => {
                localStorage.removeItem('authToken')
                setCurrentUserId(null)
                toast({ title: "Logged out successfully" })
              }} 
              variant="outline" 
              size="sm"
            >
              Logout
            </Button>
          </div>
        </div>
      )}

      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Book an Appointment</h1>
        <p className="text-gray-600">Choose a doctor, select a date and time that works for you</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Step 1: Select Doctor */}
        <Card className={`transition-all ${selectedDoctor ? 'ring-2 ring-blue-200' : ''}`}>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <User className="w-5 h-5" />
              Step 1: Choose Doctor
            </CardTitle>
            <CardDescription>
              Select from our available specialists
            </CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="space-y-3">
                {[1, 2, 3].map(i => (
                  <div key={i} className="animate-pulse">
                    <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                    <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {doctors.map(doctor => (
                  <Card 
                    key={doctor.id}
                    className={`cursor-pointer transition-all hover:shadow-md ${
                      selectedDoctor?.id === doctor.id ? 'ring-2 ring-blue-500 bg-blue-50' : 'hover:bg-gray-50'
                    }`}
                    onClick={() => {
                      setSelectedDoctor(doctor)
                      setSelectedDate(undefined)
                      setSelectedSlot(null)
                    }}
                  >
                    <CardContent className="p-4">
                      <div className="flex justify-between items-start mb-2">
                        <h3 className="font-semibold text-gray-900">Dr. {doctor.user.name}</h3>
                        <Badge variant="secondary" className="text-xs">
                          {doctor.experience_years} years
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-600 mb-2 flex items-center gap-1">
                        <Stethoscope className="w-4 h-4" />
                        {doctor.specialization || 'General Medicine'}
                      </p>
                      {doctor.consultation_fee && (
                        <p className="text-sm font-medium text-green-600">
                          ₹{doctor.consultation_fee}
                        </p>
                      )}
                      {doctor.bio && (
                        <p className="text-xs text-gray-500 mt-2 line-clamp-2">{doctor.bio}</p>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Step 2: Select Date */}
        <Card className={`transition-all ${selectedDate ? 'ring-2 ring-blue-200' : ''}`}>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CalendarDays className="w-5 h-5" />
              Step 2: Choose Date
            </CardTitle>
            <CardDescription>
              {selectedDoctor 
                ? `Select a date for your appointment with Dr. ${selectedDoctor.user.name}`
                : "Please select a doctor first"
              }
            </CardDescription>
          </CardHeader>
          <CardContent>
            {selectedDoctor ? (
              <div>
                <Calendar
                  mode="single"
                  selected={selectedDate}
                  onSelect={(date) => {
                    setSelectedDate(date)
                    setSelectedSlot(null)
                  }}
                  disabled={(date) => 
                    date < new Date() || 
                    date > new Date(Date.now() + 60 * 24 * 60 * 60 * 1000) // 60 days from now
                  }
                  className="rounded-md border"
                />
                {selectedDate && (
                  <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                    <p className="text-sm font-medium text-blue-900">
                      Selected: {getDateLabel(selectedDate)}
                    </p>
                    <p className="text-xs text-blue-700">
                      {format(selectedDate, 'EEEE, MMMM d, yyyy')}
                    </p>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-400">
                <CalendarDays className="w-12 h-12 mx-auto mb-2 opacity-50" />
                <p>Select a doctor to see available dates</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Step 3: Select Time Slot */}
        <Card className={`transition-all ${selectedSlot ? 'ring-2 ring-green-200' : ''}`}>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Clock className="w-5 h-5" />
              Step 3: Choose Time
            </CardTitle>
            <CardDescription>
              {selectedDate 
                ? `Available slots for ${getDateLabel(selectedDate)}`
                : "Please select a date first"
              }
            </CardDescription>
          </CardHeader>
          <CardContent>
            {selectedDoctor && selectedDate ? (
              <div>
                {loadingSlots ? (
                  <div className="space-y-2">
                    {[1, 2, 3, 4].map(i => (
                      <div key={i} className="animate-pulse h-12 bg-gray-200 rounded"></div>
                    ))}
                  </div>
                ) : availableSlots.length > 0 ? (
                  <div className="grid grid-cols-2 gap-2 max-h-96 overflow-y-auto">
                    {availableSlots.map(slot => (
                      <Button
                        key={slot.id}
                        variant={selectedSlot?.id === slot.id ? "default" : "outline"}
                        className={`h-auto p-3 text-left ${
                          selectedSlot?.id === slot.id ? 'ring-2 ring-green-500' : ''
                        }`}
                        onClick={() => setSelectedSlot(slot)}
                      >
                        <div>
                          <div className="font-medium text-sm">
                            {formatSlotTime(slot)}
                          </div>
                          <div className="text-xs opacity-75">
                            {slot.duration_minutes} min
                          </div>
                        </div>
                      </Button>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-400">
                    <Clock className="w-12 h-12 mx-auto mb-2 opacity-50" />
                    <p>No available slots for this date</p>
                    <p className="text-xs mt-1">Try selecting a different date</p>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-400">
                <Clock className="w-12 h-12 mx-auto mb-2 opacity-50" />
                <p>Select a doctor and date to see available times</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Booking Details Form */}
      {selectedSlot && (
        <Card className="mt-6">
          <CardHeader>
            <CardTitle>Appointment Details</CardTitle>
            <CardDescription>
              Provide additional information for your consultation
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div>
                  <Label htmlFor="symptoms">Current Symptoms *</Label>
                  <Textarea
                    id="symptoms"
                    placeholder="Describe your current symptoms, how long you've had them, and their severity..."
                    value={symptoms}
                    onChange={(e) => setSymptoms(e.target.value)}
                    className="min-h-[100px]"
                  />
                </div>
                <div>
                  <Label htmlFor="notes">Additional Notes</Label>
                  <Textarea
                    id="notes"
                    placeholder="Any other information you'd like the doctor to know..."
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    className="min-h-[80px]"
                  />
                </div>
              </div>

              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="font-semibold mb-3">Appointment Summary</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Doctor:</span>
                    <span className="font-medium">Dr. {selectedDoctor?.user.name}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Specialization:</span>
                    <span className="font-medium">{selectedDoctor?.specialization}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Date:</span>
                    <span className="font-medium">{selectedDate ? format(selectedDate, 'MMM d, yyyy') : ''}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Time:</span>
                    <span className="font-medium">{formatSlotTime(selectedSlot)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Duration:</span>
                    <span className="font-medium">{selectedSlot.duration_minutes} minutes</span>
                  </div>
                  {selectedDoctor?.consultation_fee && (
                    <div className="flex justify-between border-t pt-2 mt-2">
                      <span className="text-gray-600">Fee:</span>
                      <span className="font-bold text-green-600">₹{selectedDoctor.consultation_fee}</span>
                    </div>
                  )}
                </div>
              </div>
            </div>

            <div className="flex gap-3 pt-4">
              <Button 
                onClick={handleBooking}
                disabled={loading || !symptoms.trim()}
                className="flex-1 md:flex-none"
              >
                {loading ? "Booking..." : "Confirm Booking"}
              </Button>
              <Button 
                variant="outline" 
                onClick={() => {
                  setSelectedSlot(null)
                  setSymptoms("")
                  setNotes("")
                }}
              >
                Cancel
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}