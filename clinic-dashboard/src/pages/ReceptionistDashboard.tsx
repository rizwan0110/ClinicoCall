
import { useEffect, useState } from "react"
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  CalendarDays,
  ClipboardList,
  Clock3,
  Phone,
  PhoneCall,
  CheckCircle2,
} from "lucide-react"


const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8080"


type Appointment = {
  appointment_id: number
  appointment_date: string
  appointment_time: string
  patient_name: string
  phone_number: string
  reason_for_visit: string | null
  status: string
}

type AppointmentsResponse = {
  total_appointments: number
  appointments: Appointment[]
}

type CallbackRequest = {
  callback_id: number
  reason: string | null
  status: string
  created_at: string
  patient_id: number
  patient_name: string
  phone_number: string
}

type CallbacksResponse = {
  total_callbacks: number
  callbacks: CallbackRequest[]
}

function ReceptionistDashboard() {
  const [appointments, setAppointments] = useState<Appointment[]>([])
  const [callbacks, setCallbacks] = useState<CallbackRequest[]>([])

  const [loadingAppointments, setLoadingAppointments] = useState(true)
  const [loadingCallbacks, setLoadingCallbacks] = useState(true)

  const [appointmentError, setAppointmentError] = useState("")
  const [callbackError, setCallbackError] = useState("")

  const [cancellingId, setCancellingId] = useState<number | null>(null)
  const [completingCallbackId, setCompletingCallbackId] =
    useState<number | null>(null)

  useEffect(() => {
    async function fetchAppointments() {
      try {
        const response = await fetch(
          `${API_BASE_URL}/dashboard/appointments`
        )

        if (!response.ok) {
          throw new Error("Failed to fetch appointments")
        }

        const data: AppointmentsResponse = await response.json()
        setAppointments(data.appointments)
      } catch {
        setAppointmentError("Unable to load appointments.")
      } finally {
        setLoadingAppointments(false)
      }
    }

    async function fetchCallbacks() {
      try {
        const response = await fetch(
          `${API_BASE_URL}/dashboard/callbacks`
        )

        if (!response.ok) {
          throw new Error("Failed to fetch callbacks")
        }

        const data: CallbacksResponse = await response.json()
        setCallbacks(data.callbacks)
      } catch {
        setCallbackError("Unable to load callback requests.")
      } finally {
        setLoadingCallbacks(false)
      }
    }

    fetchAppointments()
    fetchCallbacks()
  }, [])

  const booked = appointments.filter(
    (appointment) => appointment.status === "booked"
  ).length

  const completed = appointments.filter(
    (appointment) => appointment.status === "completed"
  ).length

  const pendingCallbacks = callbacks.filter(
    (callback) => callback.status === "pending"
  ).length

  async function cancelAppointment(appointmentId: number) {
    const confirmed = window.confirm(
      "Are you sure you want to cancel this appointment?"
    )

    if (!confirmed) return

    setCancellingId(appointmentId)
    setAppointmentError("")

    try {
      const response = await fetch(
        `${API_BASE_URL}/dashboard/appointments/${appointmentId}/status`,
        {
          method: "PATCH",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            status: "cancelled",
          }),
        }
      )

      if (!response.ok) {
        throw new Error("Failed to cancel appointment")
      }

      setAppointments((previous) =>
        previous.map((appointment) =>
          appointment.appointment_id === appointmentId
            ? { ...appointment, status: "cancelled" }
            : appointment
        )
      )
    } catch {
      setAppointmentError(
        "Unable to cancel appointment. Please try again."
      )
    } finally {
      setCancellingId(null)
    }
  }

  async function completeCallback(callbackId: number) {
    setCompletingCallbackId(callbackId)
    setCallbackError("")

    try {
      const response = await fetch(
        `${API_BASE_URL}/dashboard/callbacks/${callbackId}/status`,
        {
          method: "PATCH",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            status: "completed",
          }),
        }
      )

      if (!response.ok) {
        throw new Error("Failed to complete callback")
      }

      setCallbacks((previous) =>
        previous.map((callback) =>
          callback.callback_id === callbackId
            ? { ...callback, status: "completed" }
            : callback
        )
      )
    } catch {
      setCallbackError(
        "Unable to update callback. Please try again."
      )
    } finally {
      setCompletingCallbackId(null)
    }
  }

  function formatTime(time: string) {
    const [hours, minutes] = time.split(":").map(Number)

    return new Date(2000, 0, 1, hours, minutes).toLocaleTimeString(
      "en-IN",
      {
        hour: "2-digit",
        minute: "2-digit",
        hour12: true,
      }
    )
  }

  function formatCallbackDate(dateString: string) {
    const date = new Date(dateString)

    if (Number.isNaN(date.getTime())) {
      return dateString
    }

    return date.toLocaleString("en-IN", {
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      hour12: true,
    })
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <main className="mx-auto max-w-7xl space-y-8 px-6 py-8">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">
            Receptionist Overview
          </h2>
          <p className="mt-2 text-slate-500">
            Manage patient appointments and callback requests.
          </p>
        </div>

        {/* Summary cards */}
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="text-sm font-medium">
                Total Appointments
              </CardTitle>
              <CalendarDays className="size-5 text-teal-600" />
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold">
                {appointments.length}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="text-sm font-medium">
                Booked
              </CardTitle>
              <Clock3 className="size-5 text-blue-600" />
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold">{booked}</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="text-sm font-medium">
                Completed
              </CardTitle>
              <CheckCircle2 className="size-5 text-green-600" />
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold">{completed}</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="text-sm font-medium">
                Pending Callbacks
              </CardTitle>
              <PhoneCall className="size-5 text-orange-600" />
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold">{pendingCallbacks}</p>
            </CardContent>
          </Card>
        </div>

        {/* Appointments */}
        <Card>
          <CardHeader>
            <CardTitle>All Appointments</CardTitle>
          </CardHeader>

          <CardContent>
            {loadingAppointments && (
              <p className="text-sm text-slate-500">
                Loading appointments...
              </p>
            )}

            {appointmentError && (
              <p role="alert" className="mb-4 text-sm text-red-600">
                {appointmentError}
              </p>
            )}

            {!loadingAppointments &&
              !appointmentError &&
              appointments.length === 0 && (
                <p className="text-sm text-slate-500">
                  No appointments found.
                </p>
              )}

            {!loadingAppointments && (
              <div className="space-y-4">
                {appointments.map((appointment) => (
                  <div
                    key={appointment.appointment_id}
                    className="flex flex-col gap-4 rounded-xl border p-4 sm:flex-row sm:items-center sm:justify-between"
                  >
                    <div className="flex items-start gap-4">
                      <div className="flex size-11 shrink-0 items-center justify-center rounded-full bg-teal-50 font-semibold text-teal-700">
                        {appointment.patient_name.charAt(0)}
                      </div>

                      <div>
                        <p className="font-semibold">
                          {appointment.patient_name}
                        </p>

                        <p className="mt-1 flex items-center gap-2 text-sm text-slate-500">
                          <Phone size={14} />
                          {appointment.phone_number}
                        </p>

                        <p className="mt-1 text-sm text-slate-500">
                          {appointment.reason_for_visit || "Not specified"}
                        </p>

                        <p className="mt-1 text-sm text-slate-500">
                          {appointment.appointment_date} ·{" "}
                          {formatTime(appointment.appointment_time)}
                        </p>
                      </div>
                    </div>

                    <div className="flex flex-wrap items-center gap-3">
                      <Badge
                        variant={
                          appointment.status === "completed"
                            ? "secondary"
                            : "outline"
                        }
                      >
                        {appointment.status}
                      </Badge>

                      {appointment.status === "booked" && (
                        <Button
                          size="sm"
                          variant="destructive"
                          disabled={cancellingId !== null}
                          onClick={() =>
                            cancelAppointment(appointment.appointment_id)
                          }
                        >
                          {cancellingId === appointment.appointment_id
                            ? "Cancelling..."
                            : "Cancel Appointment"}
                        </Button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Callback requests */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between gap-3">
              <div>
                <CardTitle>Callback Requests</CardTitle>
                <p className="mt-1 text-sm text-slate-500">
                  Follow up with patients who requested a call.
                </p>
              </div>

              <Badge variant="secondary">
                <ClipboardList className="mr-1 size-4" />
                {pendingCallbacks} Pending
              </Badge>
            </div>
          </CardHeader>

          <CardContent>
            {loadingCallbacks && (
              <p className="text-sm text-slate-500">
                Loading callback requests...
              </p>
            )}

            {callbackError && (
              <p role="alert" className="mb-4 text-sm text-red-600">
                {callbackError}
              </p>
            )}

            {!loadingCallbacks &&
              !callbackError &&
              callbacks.length === 0 && (
                <p className="text-sm text-slate-500">
                  No callback requests found.
                </p>
              )}

            {!loadingCallbacks && (
              <div className="space-y-4">
                {callbacks.map((callback) => (
                  <div
                    key={callback.callback_id}
                    className="flex flex-col gap-4 rounded-xl border p-4 sm:flex-row sm:items-center sm:justify-between"
                  >
                    <div className="flex items-start gap-4">
                      <div className="flex size-11 shrink-0 items-center justify-center rounded-full bg-orange-50 text-orange-700">
                        <PhoneCall size={20} />
                      </div>

                      <div>
                        <p className="font-semibold">
                          {callback.patient_name}
                        </p>

                        <p className="mt-1 flex items-center gap-2 text-sm text-slate-500">
                          <Phone size={14} />
                          {callback.phone_number}
                        </p>

                        <p className="mt-2 text-sm">
                          <span className="font-medium">Reason:</span>{" "}
                          {callback.reason || "Not specified"}
                        </p>

                        <p className="mt-1 text-xs text-slate-500">
                          Requested:{" "}
                          {formatCallbackDate(callback.created_at)}
                        </p>
                      </div>
                    </div>

                    <div className="flex flex-wrap items-center gap-3">
                      <Badge
                        variant={
                          callback.status === "completed"
                            ? "secondary"
                            : "outline"
                        }
                      >
                        {callback.status}
                      </Badge>

                      {callback.status === "pending" && (
                        <Button
                          size="sm"
                          disabled={completingCallbackId !== null}
                          onClick={() =>
                            completeCallback(callback.callback_id)
                          }
                          className="bg-teal-600 text-white hover:bg-teal-700"
                        >
                          {completingCallbackId === callback.callback_id
                            ? "Updating..."
                            : "Mark Completed"}
                        </Button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </main>
    </div>
  )
}

export default ReceptionistDashboard
