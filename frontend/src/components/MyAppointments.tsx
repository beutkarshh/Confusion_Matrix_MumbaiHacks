import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { toast } from "@/hooks/use-toast"
import { 
  Calendar, Clock, Video, User, MessageSquare, FileText,
  AlertCircle, CheckCircle, XCircle, Phone
} from "lucide-react"
import { format, parseISO, isAfter, isBefore, addMinutes, subMinutes } from "date-fns"
import { 
  getMyAppointments, 
  cancelAppointment, 
  joinVideoCall,
  type Appointment 
} from "@/services/api"

export default function MyAppointments() {
  const [appointments, setAppointments] = useState<Appointment[]>([])
  const [loading, setLoading] = useState(true)
  const [includePast, setIncludePast] = useState(false)

  useEffect(() => {
    loadAppointments()
  }, [includePast])

  const loadAppointments = async () => {
    try {
      setLoading(true)
      const appointmentsData = await getMyAppointments(includePast)
      setAppointments(appointmentsData)
    } catch (error) {
      console.error('Failed to load appointments:', error)
      toast({
        variant: "destructive",
        title: "Error",
        description: "Failed to load your appointments"
      })
    } finally {
      setLoading(false)
    }
  }

  const handleCancelAppointment = async (appointmentId: number) => {
    if (!confirm('Are you sure you want to cancel this appointment?')) {
      return
    }

    try {
      await cancelAppointment(appointmentId)
      toast({
        title: "Success",
        description: "Appointment cancelled successfully"
      })
      loadAppointments()
    } catch (error) {
      console.error('Failed to cancel appointment:', error)
      toast({
        variant: "destructive",
        title: "Error",
        description: "Failed to cancel appointment"
      })
    }
  }

  const handleJoinVideoCall = async (appointmentId: number) => {
    try {
      const joinInfo = await joinVideoCall(appointmentId)
      
      // Open video call in new window/tab
      window.open(joinInfo.room_url, '_blank', 'width=1200,height=800')
      
      toast({
        title: "Joining Video Call",
        description: "Video call window opened. If it didn't open, please check your popup blocker."
      })
    } catch (error) {
      console.error('Failed to join video call:', error)
      toast({
        variant: "destructive",
        title: "Error",
        description: "Failed to join video call. Please try again."
      })
    }
  }

  const getStatusBadge = (status: string) => {
    const variants = {
      scheduled: { variant: "default" as const, icon: Clock, label: "Scheduled" },
      active: { variant: "default" as const, icon: Video, label: "Active" },
      completed: { variant: "secondary" as const, icon: CheckCircle, label: "Completed" },
      cancelled: { variant: "destructive" as const, icon: XCircle, label: "Cancelled" },
      no_show: { variant: "destructive" as const, icon: AlertCircle, label: "No Show" }
    }

    const config = variants[status as keyof typeof variants] || variants.scheduled
    const Icon = config.icon

    return (
      <Badge variant={config.variant} className="flex items-center gap-1">
        <Icon className="w-3 h-3" />
        {config.label}
      </Badge>
    )
  }

  const isJoinable = (appointment: Appointment) => {
    const now = new Date()
    const startTime = parseISO(appointment.slot.start_datetime)
    const endTime = parseISO(appointment.slot.end_datetime)
    
    // Can join 10 minutes before to 30 minutes after start
    const joinStart = subMinutes(startTime, 10)
    const joinEnd = addMinutes(endTime, 30)
    
    return (
      appointment.status === 'scheduled' || appointment.status === 'active'
    ) && isAfter(now, joinStart) && isBefore(now, joinEnd)
  }

  const isCancellable = (appointment: Appointment) => {
    const now = new Date()
    const startTime = parseISO(appointment.slot.start_datetime)
    
    // Can cancel until 30 minutes before start
    const cancelDeadline = subMinutes(startTime, 30)
    
    return (
      appointment.status === 'scheduled' && 
      isAfter(cancelDeadline, now)
    )
  }

  const formatDateTime = (datetimeStr: string) => {
    const dt = parseISO(datetimeStr)
    return {
      date: format(dt, 'MMM d, yyyy'),
      time: format(dt, 'h:mm a'),
      dayOfWeek: format(dt, 'EEEE')
    }
  }

  const upcomingAppointments = appointments.filter(apt => 
    apt.status === 'scheduled' || apt.status === 'active'
  )
  
  const pastAppointments = appointments.filter(apt => 
    apt.status === 'completed' || apt.status === 'cancelled' || apt.status === 'no_show'
  )

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/3"></div>
          {[1, 2, 3].map(i => (
            <div key={i} className="h-32 bg-gray-200 rounded"></div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">My Appointments</h1>
          <p className="text-gray-600 mt-1">Manage your upcoming and past consultations</p>
        </div>
        <Button
          variant="outline"
          onClick={() => setIncludePast(!includePast)}
        >
          {includePast ? 'Hide Past' : 'Show Past'} Appointments
        </Button>
      </div>

      {appointments.length === 0 && (
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            You don't have any appointments yet. Book your first consultation to get started!
          </AlertDescription>
        </Alert>
      )}

      {/* Upcoming Appointments */}
      {upcomingAppointments.length > 0 && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
            <Clock className="w-5 h-5" />
            Upcoming Appointments ({upcomingAppointments.length})
          </h2>
          
          {upcomingAppointments.map(appointment => {
            const datetime = formatDateTime(appointment.slot.start_datetime)
            
            return (
              <Card key={appointment.id} className="border-l-4 border-l-blue-500">
                <CardHeader className="pb-4">
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle className="flex items-center gap-2 text-lg">
                        <User className="w-5 h-5" />
                        Dr. {appointment.doctor.user.name}
                      </CardTitle>
                      <CardDescription className="mt-1">
                        {appointment.doctor.specialization || 'General Medicine'}
                      </CardDescription>
                    </div>
                    {getStatusBadge(appointment.status)}
                  </div>
                </CardHeader>
                
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                    <div className="flex items-center gap-2">
                      <Calendar className="w-4 h-4 text-gray-500" />
                      <div>
                        <div className="font-medium">{datetime.date}</div>
                        <div className="text-gray-500">{datetime.dayOfWeek}</div>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      <Clock className="w-4 h-4 text-gray-500" />
                      <div>
                        <div className="font-medium">{datetime.time}</div>
                        <div className="text-gray-500">{appointment.slot.duration_minutes} minutes</div>
                      </div>
                    </div>
                    
                    {appointment.doctor.consultation_fee && (
                      <div className="flex items-center gap-2">
                        <div className="w-4 h-4 text-gray-500">₹</div>
                        <div>
                          <div className="font-medium">₹{appointment.doctor.consultation_fee}</div>
                          <div className="text-gray-500">Consultation Fee</div>
                        </div>
                      </div>
                    )}
                  </div>

                  {appointment.patient_symptoms && (
                    <div className="bg-gray-50 rounded-lg p-3">
                      <div className="flex items-start gap-2">
                        <MessageSquare className="w-4 h-4 text-gray-500 mt-0.5" />
                        <div>
                          <div className="text-sm font-medium text-gray-700">Your Symptoms</div>
                          <div className="text-sm text-gray-600 mt-1">{appointment.patient_symptoms}</div>
                        </div>
                      </div>
                    </div>
                  )}

                  {appointment.patient_notes && (
                    <div className="bg-blue-50 rounded-lg p-3">
                      <div className="flex items-start gap-2">
                        <FileText className="w-4 h-4 text-blue-500 mt-0.5" />
                        <div>
                          <div className="text-sm font-medium text-blue-700">Additional Notes</div>
                          <div className="text-sm text-blue-600 mt-1">{appointment.patient_notes}</div>
                        </div>
                      </div>
                    </div>
                  )}

                  <div className="flex flex-wrap gap-2 pt-2">
                    {isJoinable(appointment) && (
                      <Button
                        onClick={() => handleJoinVideoCall(appointment.id)}
                        className="flex items-center gap-2"
                      >
                        <Video className="w-4 h-4" />
                        Join Video Call
                      </Button>
                    )}
                    
                    {isCancellable(appointment) && (
                      <Button
                        variant="outline"
                        onClick={() => handleCancelAppointment(appointment.id)}
                        className="flex items-center gap-2"
                      >
                        <XCircle className="w-4 h-4" />
                        Cancel
                      </Button>
                    )}
                    
                    {appointment.doctor.user.phone && (
                      <Button
                        variant="outline"
                        onClick={() => window.open(`tel:${appointment.doctor.user.phone}`)}
                        className="flex items-center gap-2"
                      >
                        <Phone className="w-4 h-4" />
                        Call Doctor
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>
      )}

      {/* Past Appointments */}
      {includePast && pastAppointments.length > 0 && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
            <FileText className="w-5 h-5" />
            Past Appointments ({pastAppointments.length})
          </h2>
          
          {pastAppointments.map(appointment => {
            const datetime = formatDateTime(appointment.slot.start_datetime)
            
            return (
              <Card key={appointment.id} className="border-l-4 border-l-gray-300 bg-gray-50/50">
                <CardHeader className="pb-3">
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle className="flex items-center gap-2 text-lg">
                        <User className="w-5 h-5" />
                        Dr. {appointment.doctor.user.name}
                      </CardTitle>
                      <CardDescription>
                        {datetime.date} at {datetime.time}
                      </CardDescription>
                    </div>
                    {getStatusBadge(appointment.status)}
                  </div>
                </CardHeader>
                
                <CardContent>
                  {appointment.doctor_notes && (
                    <div className="bg-green-50 rounded-lg p-3 mb-3">
                      <div className="flex items-start gap-2">
                        <User className="w-4 h-4 text-green-500 mt-0.5" />
                        <div>
                          <div className="text-sm font-medium text-green-700">Doctor's Notes</div>
                          <div className="text-sm text-green-600 mt-1">{appointment.doctor_notes}</div>
                        </div>
                      </div>
                    </div>
                  )}

                  {appointment.consultation_summary && (
                    <div className="bg-blue-50 rounded-lg p-3">
                      <div className="flex items-start gap-2">
                        <FileText className="w-4 h-4 text-blue-500 mt-0.5" />
                        <div>
                          <div className="text-sm font-medium text-blue-700">Consultation Summary</div>
                          <div className="text-sm text-blue-600 mt-1">{appointment.consultation_summary}</div>
                        </div>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            )
          })}
        </div>
      )}
    </div>
  )
}