import axios from 'axios'
import { supabase } from '@/integrations/supabase/client'
import { config } from '@/config'

// Dev-auth bypass is enabled only when devAuth is true in config
const USE_DEV_AUTH = config.devAuth

const API_BASE_URL = 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 180000, // 3 minutes - orchestrator needs time for multiple AI agent calls
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor to add auth token
api.interceptors.request.use(async (config) => {
  if (USE_DEV_AUTH) {
    // For dev mode, use localStorage authToken for scheduling API
    const authToken = localStorage.getItem('authToken')
    if (authToken && config.url?.includes('/api/scheduling/')) {
      config.headers.Authorization = `Bearer ${authToken}`
    }
  } else {
    // Production mode: use Supabase session
    const { data: { session } } = await supabase.auth.getSession()
    if (session?.access_token) {
      config.headers.Authorization = `Bearer ${session.access_token}`
    }
  }
  return config
})

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

export interface PatientData {
  patientId: string
  age: number
  gender: string
  symptoms: string
  medicalHistory: string
  currentMedications: string
  urgency: string
}

export interface AnalysisResult {
  agentName: string
  status: string
  result: any
  timestamp: string
}

// Main analysis endpoint
export const analyzePatientCase = async (patientData: PatientData) => {
  const response = await api.post('/analyze', patientData)
  return response.data
}

// Generate PDF report
export const generatePdfReport = async (analysisPayload: any) => {
  const response = await api.post('/generate-pdf', analysisPayload, {
    responseType: 'blob'
  })
  return response.data as Blob
}

// Individual agent endpoints (aligned with backend FastAPI routes)
export const callSymptomAgent = async (payload: Partial<PatientData>) => {
  const response = await api.post('/symptom-analyzer', payload)
  return response.data
}

export const callLiteratureAgent = async (payload: Partial<PatientData>) => {
  const response = await api.post('/literature', payload)
  return response.data
}

export const callCaseAgent = async (payload: Partial<PatientData>) => {
  const response = await api.post('/case-matcher', payload)
  return response.data
}

export const callTreatmentAgent = async (payload: Partial<PatientData>) => {
  const response = await api.post('/treatment', payload)
  return response.data
}

export const callSummaryAgent = async (payload: Partial<PatientData>) => {
  const response = await api.post('/summary', payload)
  return response.data
}

// Auth functions using Supabase
export const loginUser = async (email: string, password: string) => {
  if (USE_DEV_AUTH) {
    const name = email?.split?.('@')?.[0] || 'Dev User'
    return {
      user: { id: 'dev-user-1', email, name, role: 'Patient' },
      session: null as any
    }
  }
  const { data, error } = await supabase.auth.signInWithPassword({
    email,
    password,
  })
  
  if (error) throw error
  
  return {
    user: {
      id: data.user!.id,
      email: data.user!.email!,
      name: data.user!.user_metadata?.name || data.user!.email!.split('@')[0],
      role: data.user!.user_metadata?.role || 'Patient'
    },
    session: data.session
  }
}

export const signupUser = async (email: string, password: string, name: string, role: string) => {
  if (USE_DEV_AUTH) {
    return {
      user: { id: 'dev-user-1', email, name: name || (email?.split?.('@')?.[0] || 'Dev User'), role },
      session: null as any
    }
  }
  const { data, error } = await supabase.auth.signUp({
    email,
    password,
    options: {
      data: {
        name: name,
        role: role,
      },
      emailRedirectTo: `${window.location.origin}/`
    }
  })
  
  if (error) throw error
  
  return {
    user: {
      id: data.user!.id,
      email: data.user!.email!,
      name: name,
      role: role
    },
    session: data.session
  }
}

export const signInWithProvider = async (provider: 'google' | 'github') => {
  if (USE_DEV_AUTH) {
    // In dev-auth mode, simulate a provider sign-in by returning immediately
    return { provider, url: null }
  }
  const { data, error } = await supabase.auth.signInWithOAuth({
    provider,
    options: {
      redirectTo: `${window.location.origin}/dashboard`
    }
  })
  
  if (error) throw error
  return data
}

export const signOut = async () => {
  if (USE_DEV_AUTH) return
  const { error } = await supabase.auth.signOut()
  if (error) throw error
}

export default api

// ================================
// Scheduling API Functions
// ================================

export interface Doctor {
  id: number
  user_id: number
  specialization: string
  experience_years: number
  default_slot_duration_minutes: number
  consultation_fee: number
  bio: string
  is_available_for_booking: boolean
  user: {
    id: number
    name: string
    email: string
    phone?: string
  }
}

export interface AppointmentSlot {
  id: number
  doctor_id: number
  start_datetime: string
  end_datetime: string
  duration_minutes: number
  status: 'available' | 'booked' | 'completed' | 'cancelled'
  doctor: Doctor
}

export interface Appointment {
  id: number
  patient_id: number
  doctor_id: number
  slot_id: number
  status: 'scheduled' | 'active' | 'completed' | 'cancelled' | 'no_show'
  patient_symptoms?: string
  patient_notes?: string
  doctor_notes?: string
  consultation_summary?: string
  daily_room_name?: string
  daily_room_url?: string
  booked_at: string
  started_at?: string
  completed_at?: string
  cancelled_at?: string
  ai_analysis_triggered?: boolean
  pdf_generated?: boolean
  pdf_path?: string
  patient: {
    id: number
    name: string
    email: string
  }
  doctor: Doctor
  slot: AppointmentSlot
}

export interface DoctorAvailability {
  id: number
  doctor_id: number
  day_of_week?: number
  specific_date?: string
  start_time: string
  end_time: string
  slot_duration_minutes?: number
  is_active: boolean
  is_blocked: boolean
  notes?: string
}

// Get list of available doctors
export const getDoctors = async (specialization?: string): Promise<Doctor[]> => {
  const params = specialization ? { specialization } : {}
  const response = await api.get('/api/scheduling/doctors', { params })
  return response.data
}

// Get available slots for a doctor on a specific date
export const getAvailableSlots = async (doctorId: number, date: string): Promise<{
  date: string
  doctor: Doctor
  available_slots: AppointmentSlot[]
}> => {
  const response = await api.get(`/api/scheduling/doctors/${doctorId}/slots`, {
    params: { target_date: date }
  })
  return response.data
}

// Book an appointment slot
export const bookAppointment = async (slotId: number, patientSymptoms?: string, patientNotes?: string): Promise<{
  success: boolean
  appointment?: Appointment
  error?: string
}> => {
  const response = await api.post('/api/scheduling/appointments/book', {
    slot_id: slotId,
    patient_symptoms: patientSymptoms,
    patient_notes: patientNotes
  })
  return response.data
}

// Get current user's appointments
export const getMyAppointments = async (includePast: boolean = false): Promise<Appointment[]> => {
  const response = await api.get('/api/scheduling/appointments/my', {
    params: { include_past: includePast }
  })
  return response.data
}

// Cancel an appointment
export const cancelAppointment = async (appointmentId: number, reason?: string): Promise<void> => {
  await api.delete(`/api/scheduling/appointments/${appointmentId}`, {
    data: { reason }
  })
}

// Update appointment (for doctors)
export const updateAppointment = async (appointmentId: number, updates: {
  status?: string
  doctor_notes?: string
  consultation_summary?: string
  patient_notes?: string
}): Promise<Appointment> => {
  const response = await api.put(`/api/scheduling/appointments/${appointmentId}`, updates)
  return response.data
}

// Join video call for an appointment
export const joinVideoCall = async (appointmentId: number): Promise<{
  room_url: string
  room_name: string
  token?: string
}> => {
  const response = await api.post(`/api/scheduling/appointments/${appointmentId}/video/join`)
  return response.data
}

// End video call (for doctors)
export const endVideoCall = async (appointmentId: number, doctorNotes?: string, consultationSummary?: string): Promise<void> => {
  await api.post(`/api/scheduling/appointments/${appointmentId}/video/end`, {
    doctor_notes: doctorNotes,
    consultation_summary: consultationSummary
  })
}

// Doctor-specific API functions

// Get doctor's availability patterns
export const getDoctorAvailability = async (doctorId: number): Promise<DoctorAvailability[]> => {
  const response = await api.get(`/api/scheduling/doctors/${doctorId}/availability`)
  return response.data
}

// Set doctor's availability schedule
export const setDoctorAvailability = async (doctorId: number, availabilityPatterns: Omit<DoctorAvailability, 'id' | 'doctor_id'>[]): Promise<DoctorAvailability[]> => {
  const response = await api.post(`/api/scheduling/doctors/${doctorId}/availability`, {
    availability_patterns: availabilityPatterns,
    generate_slots_for_weeks: 4
  })
  return response.data
}

// Generate slots for a doctor
export const generateSlots = async (doctorId: number, startDate: string, endDate: string, forceRegenerate: boolean = false): Promise<{
  message: string
  slots_generated: number
  date_range: string
}> => {
  const response = await api.post(`/api/scheduling/doctors/${doctorId}/generate-slots`, {
    doctor_id: doctorId,
    start_date: startDate,
    end_date: endDate,
    force_regenerate: forceRegenerate
  })
  return response.data
}

// ================================
// AI Integration Functions
// ================================

// Trigger AI analysis for a completed appointment
export const triggerAIAnalysis = async (appointmentId: number, generatePdf: boolean = true): Promise<{
  message: string
  analysis_results?: any
  pdf_generated: boolean
  pdf_path?: string
}> => {
  const response = await api.post(`/api/scheduling/appointments/${appointmentId}/ai-analysis`, null, {
    params: { generate_pdf: generatePdf }
  })
  return response.data
}

// Get AI analysis status for an appointment
export const getAIAnalysisStatus = async (appointmentId: number): Promise<{
  appointment_id: number
  status: string
  ai_analysis_triggered: boolean
  pdf_generated: boolean
  pdf_path?: string
  completed_at?: string
}> => {
  const response = await api.get(`/api/scheduling/appointments/${appointmentId}/ai-status`)
  return response.data
}

// Regenerate AI analysis and PDF
export const regenerateAIAnalysis = async (appointmentId: number): Promise<{
  message: string
  analysis_results?: any
  pdf_generated: boolean
}> => {
  const response = await api.post(`/api/scheduling/appointments/${appointmentId}/regenerate-analysis`)
  return response.data
}

// Download PDF report for an appointment
export const downloadConsultationPDF = async (appointmentId: number): Promise<Blob> => {
  const response = await api.get(`/api/scheduling/appointments/${appointmentId}/download-pdf`, {
    responseType: 'blob'
  })
  return response.data
}