
import { NavLink } from "react-router-dom"
import { Activity, ClipboardList, Stethoscope } from "lucide-react"

function DashboardNav() {
  const linkClass =
    "flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition-colors"

  return (
    <header className="border-b border-slate-200 bg-white">
      <div className="mx-auto flex max-w-7xl flex-col gap-4 px-6 py-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <div className="rounded-xl bg-teal-600 p-2 text-white">
            <Activity size={24} />
          </div>

          <div>
            <h1 className="text-xl font-bold text-slate-900">
              ClinicoCall
            </h1>
            <p className="text-xs text-slate-500">
              Clinic Management
            </p>
          </div>
        </div>

        <nav
          aria-label="Dashboard navigation"
          className="flex flex-wrap items-center gap-2"
        >
          <NavLink
            to="/physiotherapist"
            className={({ isActive }) =>
              `${linkClass} ${
                isActive
                  ? "bg-teal-600 text-white"
                  : "bg-slate-100 text-slate-600 hover:bg-slate-200"
              }`
            }
          >
            <Stethoscope size={17} />
            Physiotherapist
          </NavLink>

          <NavLink
            to="/receptionist"
            className={({ isActive }) =>
              `${linkClass} ${
                isActive
                  ? "bg-teal-600 text-white"
                  : "bg-slate-100 text-slate-600 hover:bg-slate-200"
              }`
            }
          >
            <ClipboardList size={17} />
            Receptionist
          </NavLink>
        </nav>
      </div>
    </header>
  )
}

export default DashboardNav
