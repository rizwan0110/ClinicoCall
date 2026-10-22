
import {
  BrowserRouter,
  Route,
  Routes,
} from "react-router-dom"

import DashboardNav from "./components/DashboardNav"
import PhysiotherapistDashboard from "./pages/PhysiotherapistDashboard"
import ReceptionistDashboard from "./pages/ReceptionistDashboard"
import VoiceReceptionist from "./pages/VoiceReceptionist";

function App() {
  return (
    <BrowserRouter>
      <DashboardNav />

  <Routes>
  <Route path="/" element={<VoiceReceptionist />} />
  <Route
    path="/receptionist"
    element={<ReceptionistDashboard />}
  />
  <Route
    path="/physiotherapist"
    element={<PhysiotherapistDashboard />}
  />
</Routes>
    </BrowserRouter>
  )
}

export default App
