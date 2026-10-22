
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
  Clock3,
  CheckCircle2,
  Stethoscope,
} from "lucide-react"

const API_BASE_URL = "http://localhost:8080"

type Appointment = {
  appointment_id: number
  appointment_date: string
  appointment_time: string
  patient_name: string
  phone_number?: string
  reason_for_visit: string | null
  affected_area?: string | null
  issue_duration?: string | number | null
  status: string
}

type TodayResponse = {
  date: string
  total_appointments: number
  appointments: Appointment[]
}

function PhysiotherapistDashboard() {
  const [appointments, setAppointments] = useState<Appointment[]>([])
  const [date, setDate] = useState("")
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [updatingId, setUpdatingId] = useState<number | null>(null)

  useEffect(() => {
    async function fetchAppointments() {
      try {
        const response = await fetch(
          `${API_BASE_URL}/dashboard/appointments/today`
        )

        if (!response.ok) {
          throw new Error("Failed to fetch appointments")
        }

        const data: TodayResponse = await response.json()

        setAppointments(data.appointments)
        setDate(data.date)
      } catch {
        setError("Unable to load today's appointments.")
      } finally {
        setLoading(false)
      }
    }

    fetchAppointments()
  }, [])

  const booked = appointments.filter(
    (appointment) => appointment.status === "booked"
  ).length

  const completed = appointments.filter(
    (appointment) => appointment.status === "completed"
  ).length

  async function completeAppointment(appointmentId: number) {
    setUpdatingId(appointmentId)
    setError("")

    try {
      const response = await fetch(
        `${API_BASE_URL}/dashboard/appointments/${appointmentId}/status`,
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
        throw new Error("Failed to update appointment")
      }

      setAppointments((previous) =>
        previous.map((appointment) =>
          appointment.appointment_id === appointmentId
            ? { ...appointment, status: "completed" }
            : appointment
        )
      )
    } catch {
      setError("Unable to complete appointment. Please try again.")
    } finally {
      setUpdatingId(null)
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

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <main className="mx-auto max-w-7xl space-y-8 px-6 py-8">
        <div>
          <div className="flex items-center gap-3">
            <Stethoscope className="size-7 text-teal-600" />
            <h2 className="text-3xl font-bold tracking-tight">
              Physiotherapist Dashboard
            </h2>
          </div>

          <p className="mt-2 text-slate-500">
            Today's patient appointments
            {date ? ` · ${date}` : ""}
          </p>
        </div>

        <div className="grid gap-5 sm:grid-cols-3">
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
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Today's Appointments</CardTitle>
          </CardHeader>

          <CardContent>
            {loading && (
              <p className="text-sm text-slate-500">
                Loading appointments...
              </p>
            )}

            {error && (
              <p role="alert" className="mb-4 text-sm text-red-600">
                {error}
              </p>
            )}

            {!loading && !error && appointments.length === 0 && (
              <p className="text-sm text-slate-500">
                No appointments scheduled for today.
              </p>
            )}

            {!loading && (
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

                      <div className="space-y-1">
                        <p className="font-semibold">
                          {appointment.patient_name}
                        </p>

                        <p className="text-sm text-slate-500">
                          {formatTime(appointment.appointment_time)}
                        </p>

                        <p className="text-sm text-slate-600">
                          <span className="font-medium">Reason:</span>{" "}
                          {appointment.reason_for_visit || "Not specified"}
                        </p>

                        {appointment.affected_area && (
                          <p className="text-sm text-slate-600">
                            <span className="font-medium">
                              Affected area:
                            </span>{" "}
                            {appointment.affected_area}
                          </p>
                        )}

                        {appointment.issue_duration != null && (
                          <p className="text-sm text-slate-600">
                            <span className="font-medium">
                              Duration:
                            </span>{" "}
                            {appointment.issue_duration}
                          </p>
                        )}
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
                          disabled={updatingId !== null}
                          onClick={() =>
                            completeAppointment(appointment.appointment_id)
                          }
                          className="bg-teal-600 text-white hover:bg-teal-700"
                        >
                          {updatingId === appointment.appointment_id
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

export default PhysiotherapistDashboard
