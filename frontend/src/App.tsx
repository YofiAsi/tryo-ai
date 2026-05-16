import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom"
import { SidebarProvider } from "@/components/ui/sidebar"
import { AppSidebar } from "@/components/layout/sidebar"
import { PositionsPage } from "@/pages/positions"
import { PositionDetailsPage } from "@/pages/position-details"
import { AddPositionPage } from "@/pages/add-position"
import { ThemeProvider } from "@/contexts/theme-context"

export default function App() {
  return (
    <ThemeProvider defaultTheme="system" storageKey="tyro-theme">
      <Router>
        <SidebarProvider>
          <AppSidebar />
          <main className="flex-1">
            <Routes>
              <Route path="/" element={<PositionsPage />} />
              <Route path="/positions/:id" element={<PositionDetailsPage />} />
              <Route path="/positions/add" element={<AddPositionPage />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
        </SidebarProvider>
      </Router>
    </ThemeProvider>
  )
}
