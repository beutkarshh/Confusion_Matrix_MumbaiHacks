import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { toast } from "@/hooks/use-toast"
import { 
  Calendar, Clock, Settings, User, Video, FileText, 
  CheckCircle, XCircle, Plus, Trash2
} from "lucide-react"
import { format, parseISO, addWeeks, startOfWeek } from "date-fns"
import { 
  getDoctorAvailability,
  setDoctorAvailability,
  generateSlots,
  getMyAppointments,
  updateAppointment,
  joinVideoCall,
  endVideoCall,
  triggerAIAnalysis,
  getAIAnalysisStatus,
  downloadConsultationPDF,
  type DoctorAvailability,
  type Appointment 
} from "@/services/api"

interface DoctorScheduleProps {
  doctorId?: number // Current doctor's ID
}

export default function DoctorSchedule({ doctorId = 1 }: DoctorScheduleProps) {
  const [activeTab, setActiveTab] = useState("availability")
  const [availability, setAvailability] = useState<DoctorAvailability[]>([])
  const [appointments, setAppointments] = useState<Appointment[]>([])
  const [loading, setLoading] = useState(false)

  // Availability form state
  const [availabilityPatterns, setAvailabilityPatterns] = useState<{
    day_of_week?: number
    start_time: string
    end_time: string
    slot_duration_minutes?: number
  }[]>([
    { day_of_week: 1, start_time: "09:00", end_time: "17:00", slot_duration_minutes: 20 }
  ])

  useEffect(() => {
    if (activeTab === "availability") {
      loadAvailability()
    } else if (activeTab === "appointments") {
      loadAppointments()
    }
  }, [activeTab, doctorId])

  const loadAvailability = async () => {
    try {
      setLoading(true)
      const availabilityData = await getDoctorAvailability(doctorId)
      setAvailability(availabilityData)
    } catch (error) {
      console.error('Failed to load availability:', error)
      toast({
        variant: "destructive",
        title: "Error",
        description: "Failed to load availability settings"
      })
    } finally {
      setLoading(false)
    }
  }

  const loadAppointments = async () => {
    try {
      setLoading(true)
      const appointmentsData = await getMyAppointments(false)
      setAppointments(appointmentsData)
    } catch (error) {
      console.error('Failed to load appointments:', error)
      toast({
        variant: "destructive",
        title: "Error",
        description: "Failed to load appointments"
      })
    } finally {
      setLoading(false)
    }
  }

  const handleSaveAvailability = async () => {
    try {
      setLoading(true)
      
      const patterns = availabilityPatterns.map(pattern => ({
        day_of_week: pattern.day_of_week,
        specific_date: undefined,
        start_time: pattern.start_time,
        end_time: pattern.end_time,
        slot_duration_minutes: pattern.slot_duration_minutes,
        is_active: true,
        is_blocked: false
      }))

      await setDoctorAvailability(doctorId, patterns)
      
      toast({
        title: "Success",
        description: "Availability schedule saved successfully"
      })
      
      loadAvailability()
    } catch (error) {
      console.error('Failed to save availability:', error)
      toast({
        variant: "destructive",
        title: "Error",
        description: "Failed to save availability schedule"
      })
    } finally {
      setLoading(false)
    }
  }

  const handleGenerateSlots = async () => {
    try {
      setLoading(true)
      
      const startDate = format(new Date(), 'yyyy-MM-dd')
      const endDate = format(addWeeks(new Date(), 4), 'yyyy-MM-dd')
      
      const result = await generateSlots(doctorId, startDate, endDate, true)
      
      toast({
        title: "Success",
        description: result.message
      })
    } catch (error) {
      console.error('Failed to generate slots:', error)
      toast({
        variant: "destructive",
        title: "Error",
        description: "Failed to generate appointment slots"
      })
    } finally {
      setLoading(false)
    }
  }

  const handleUpdateAppointment = async (appointmentId: number, updates: any) => {
    try {
      await updateAppointment(appointmentId, updates)
      toast({
        title: "Success",
        description: "Appointment updated successfully"
      })
      loadAppointments()
    } catch (error) {
      console.error('Failed to update appointment:', error)
      toast({
        variant: "destructive",
        title: "Error",
        description: "Failed to update appointment"
      })
    }
  }

  const handleJoinCall = async (appointmentId: number) => {
    try {
      const joinInfo = await joinVideoCall(appointmentId)
      window.open(joinInfo.room_url, '_blank', 'width=1200,height=800')
      
      // Mark appointment as active
      await handleUpdateAppointment(appointmentId, { status: 'active' })
    } catch (error) {
      console.error('Failed to join call:', error)
      toast({
        variant: "destructive",
        title: "Error",
        description: "Failed to join video call"
      })
    }
  }

  const handleEndCall = async (appointmentId: number, doctorNotes: string = "") => {
    try {
      await endVideoCall(appointmentId, doctorNotes, "Consultation completed via video call")
      toast({
        title: "Success",
        description: "Consultation completed successfully"
      })
      loadAppointments()
    } catch (error) {
      console.error('Failed to end call:', error)
      toast({
        variant: "destructive",
        title: "Error",
        description: "Failed to end consultation"
      })
    }
  }

  const handleTriggerAI = async (appointmentId: number) => {
    try {
      setLoading(true)
      const result = await triggerAIAnalysis(appointmentId, true)
      toast({
        title: "Success",
        description: result.message
      })
      loadAppointments()
    } catch (error) {
      console.error('Failed to trigger AI analysis:', error)
      toast({
        variant: "destructive",
        title: "Error", 
        description: "Failed to trigger AI analysis"
      })
    } finally {
      setLoading(false)
    }
  }

  const handleDownloadPDF = async (appointmentId: number) => {
    try {
      const pdfBlob = await downloadConsultationPDF(appointmentId)
      
      // Create download link
      const url = window.URL.createObjectURL(pdfBlob)
      const link = document.createElement('a')
      link.href = url
      link.download = `consultation_report_${appointmentId}.pdf`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
      
      toast({
        title: "Success",
        description: "PDF report downloaded"
      })
    } catch (error) {
      console.error('Failed to download PDF:', error)
      toast({
        variant: "destructive",
        title: "Error",
        description: "Failed to download PDF report"
      })
    }
  }

  const addAvailabilityPattern = () => {
    setAvailabilityPatterns([
      ...availabilityPatterns,
      { day_of_week: 1, start_time: "09:00", end_time: "17:00", slot_duration_minutes: 20 }
    ])
  }

  const removeAvailabilityPattern = (index: number) => {
    setAvailabilityPatterns(availabilityPatterns.filter((_, i) => i !== index))
  }

  const updateAvailabilityPattern = (index: number, field: string, value: any) => {
    const updated = availabilityPatterns.map((pattern, i) => 
      i === index ? { ...pattern, [field]: value } : pattern
    )
    setAvailabilityPatterns(updated)
  }

  const dayNames = [
    "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"
  ]

  const getStatusBadge = (status: string) => {
    const variants = {
      scheduled: { variant: "default" as const, icon: Clock, label: "Scheduled" },
      active: { variant: "default" as const, icon: Video, label: "Active" },
      completed: { variant: "secondary" as const, icon: CheckCircle, label: "Completed" },
      cancelled: { variant: "destructive" as const, icon: XCircle, label: "Cancelled" },
      no_show: { variant: "destructive" as const, icon: XCircle, label: "No Show" }
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

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Doctor Schedule & Appointments</h1>
        <p className="text-gray-600">Manage your availability and upcoming consultations</p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="availability" className="flex items-center gap-2">
            <Settings className="w-4 h-4" />
            Availability Settings
          </TabsTrigger>
          <TabsTrigger value="appointments" className="flex items-center gap-2">
            <Calendar className="w-4 h-4" />
            Upcoming Appointments
          </TabsTrigger>
        </TabsList>

        <TabsContent value="availability" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="w-5 h-5" />
                Weekly Schedule
              </CardTitle>
              <CardDescription>
                Set your regular weekly availability. Slots will be automatically generated based on this schedule.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {availabilityPatterns.map((pattern, index) => (
                <Card key={index} className="p-4">
                  <div className="grid grid-cols-1 md:grid-cols-5 gap-4 items-end">
                    <div>
                      <Label>Day of Week</Label>
                      <Select
                        value={pattern.day_of_week?.toString()}
                        onValueChange={(value) => updateAvailabilityPattern(index, 'day_of_week', parseInt(value))}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select day" />
                        </SelectTrigger>
                        <SelectContent>
                          {dayNames.map((day, dayIndex) => (
                            <SelectItem key={dayIndex} value={dayIndex.toString()}>
                              {day}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    <div>
                      <Label>Start Time</Label>
                      <Input
                        type="time"
                        value={pattern.start_time}
                        onChange={(e) => updateAvailabilityPattern(index, 'start_time', e.target.value)}
                      />
                    </div>

                    <div>
                      <Label>End Time</Label>
                      <Input
                        type="time"
                        value={pattern.end_time}
                        onChange={(e) => updateAvailabilityPattern(index, 'end_time', e.target.value)}
                      />
                    </div>

                    <div>
                      <Label>Slot Duration (minutes)</Label>
                      <Select
                        value={pattern.slot_duration_minutes?.toString()}
                        onValueChange={(value) => updateAvailabilityPattern(index, 'slot_duration_minutes', parseInt(value))}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Duration" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="15">15 minutes</SelectItem>
                          <SelectItem value="20">20 minutes</SelectItem>
                          <SelectItem value="30">30 minutes</SelectItem>
                          <SelectItem value="45">45 minutes</SelectItem>
                          <SelectItem value="60">60 minutes</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="flex gap-2">
                      {availabilityPatterns.length > 1 && (
                        <Button
                          variant="outline"
                          size="icon"
                          onClick={() => removeAvailabilityPattern(index)}
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      )}
                    </div>
                  </div>
                </Card>
              ))}

              <div className="flex gap-3">
                <Button
                  variant="outline"
                  onClick={addAvailabilityPattern}
                  className="flex items-center gap-2"
                >
                  <Plus className="w-4 h-4" />
                  Add Another Day
                </Button>
                
                <Button
                  onClick={handleSaveAvailability}
                  disabled={loading}
                  className="flex items-center gap-2"
                >
                  <Settings className="w-4 h-4" />
                  {loading ? "Saving..." : "Save Schedule"}
                </Button>
                
                <Button
                  variant="secondary"
                  onClick={handleGenerateSlots}
                  disabled={loading}
                  className="flex items-center gap-2"
                >
                  <Calendar className="w-4 h-4" />
                  Generate Slots (4 weeks)
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Current Availability Display */}
          {availability.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Current Schedule</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {availability.map(avail => (
                    <Card key={avail.id} className="p-3">
                      <div className="text-sm font-medium">
                        {avail.day_of_week !== undefined ? dayNames[avail.day_of_week] : 'Specific Date'}
                      </div>
                      <div className="text-xs text-gray-600">
                        {avail.start_time} - {avail.end_time}
                      </div>
                      <div className="text-xs text-gray-500">
                        {avail.slot_duration_minutes || 20} min slots
                      </div>
                    </Card>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="appointments" className="space-y-6">
          {loading ? (
            <div className="space-y-4">
              {[1, 2, 3].map(i => (
                <div key={i} className="animate-pulse h-32 bg-gray-200 rounded"></div>
              ))}
            </div>
          ) : appointments.length === 0 ? (
            <Card>
              <CardContent className="text-center py-12">
                <Calendar className="w-12 h-12 mx-auto text-gray-400 mb-4" />
                <p className="text-lg font-medium text-gray-600">No upcoming appointments</p>
                <p className="text-gray-400">Appointments will appear here once patients book slots</p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {appointments.map(appointment => {
                const datetime = parseISO(appointment.slot.start_datetime)
                
                return (
                  <Card key={appointment.id} className="border-l-4 border-l-green-500">
                    <CardHeader className="pb-4">
                      <div className="flex justify-between items-start">
                        <div>
                          <CardTitle className="flex items-center gap-2 text-lg">
                            <User className="w-5 h-5" />
                            {appointment.patient.name}
                          </CardTitle>
                          <CardDescription>
                            {format(datetime, 'EEEE, MMM d, yyyy')} at {format(datetime, 'h:mm a')}
                          </CardDescription>
                        </div>
                        {getStatusBadge(appointment.status)}
                      </div>
                    </CardHeader>
                    
                    <CardContent className="space-y-4">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                        <div>
                          <div className="font-medium text-gray-700">Patient Contact</div>
                          <div className="text-gray-600">{appointment.patient.email}</div>
                        </div>
                        <div>
                          <div className="font-medium text-gray-700">Duration</div>
                          <div className="text-gray-600">{appointment.slot.duration_minutes} minutes</div>
                        </div>
                      </div>

                      {appointment.patient_symptoms && (
                        <div className="bg-blue-50 rounded-lg p-3">
                          <div className="text-sm font-medium text-blue-700 mb-1">Patient Symptoms</div>
                          <div className="text-sm text-blue-600">{appointment.patient_symptoms}</div>
                        </div>
                      )}

                      {appointment.patient_notes && (
                        <div className="bg-gray-50 rounded-lg p-3">
                          <div className="text-sm font-medium text-gray-700 mb-1">Patient Notes</div>
                          <div className="text-sm text-gray-600">{appointment.patient_notes}</div>
                        </div>
                      )}

                      <div className="flex flex-wrap gap-2 pt-2">
                        {appointment.status === 'scheduled' && (
                          <>
                            <Button
                              onClick={() => handleJoinCall(appointment.id)}
                              className="flex items-center gap-2"
                            >
                              <Video className="w-4 h-4" />
                              Start Video Call
                            </Button>
                            <Button
                              variant="outline"
                              onClick={() => handleUpdateAppointment(appointment.id, { status: 'cancelled' })}
                            >
                              Cancel Appointment
                            </Button>
                          </>
                        )}
                        
                        {appointment.status === 'active' && (
                          <Button
                            onClick={() => handleEndCall(appointment.id)}
                            variant="secondary"
                            className="flex items-center gap-2"
                          >
                            <CheckCircle className="w-4 h-4" />
                            Complete Consultation
                          </Button>
                        )}
                        
                        {appointment.status === 'completed' && (
                          <>
                            <Button
                              variant="outline"
                              onClick={() => handleTriggerAI(appointment.id)}
                              className="flex items-center gap-2"
                              disabled={loading}
                            >
                              <FileText className="w-4 h-4" />
                              {appointment.ai_analysis_triggered ? 'Regenerate Report' : 'Generate AI Report'}
                            </Button>
                            
                            {appointment.pdf_generated && (
                              <Button
                                variant="secondary"
                                onClick={() => handleDownloadPDF(appointment.id)}
                                className="flex items-center gap-2"
                              >
                                <FileText className="w-4 h-4" />
                                Download PDF
                              </Button>
                            )}
                          </>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                )
              })}
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}