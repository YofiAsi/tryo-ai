import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom"
import { SidebarProvider } from "@/components/ui/sidebar"
import { AppSidebar } from "@/components/layout/sidebar"
import { PositionsPage } from "@/pages/positions"
import { PositionDetailsPage } from "@/pages/position-details"
import { AddPositionPage } from "@/pages/add-position"
import { AdminOverviewPage } from "@/components/admin/overview-page"
import { UserManagementPage } from "@/components/admin/user-management-page"
import { ActivityMonitorPage } from "@/components/admin/activity-monitor-page"
import { LoginPage } from "@/pages/login"
import { ProtectedRoute } from "@/routes/protected-route"
import { AdminRoute } from "@/routes/admin-route"
import { AuthProvider } from "@/contexts/auth-context"

export default function App() {
  return (
    <AuthProvider>
        <Router>
          <Routes>
          <Route path="/login" element={<LoginPage />}/>
            <Route
              path="/*"
              element={
                <ProtectedRoute>
                  <SidebarProvider>
                    <AppSidebar />
                    <main className="flex-1">
                      <Routes>
                        <Route path="/" element={<PositionsPage />} />
                        <Route path="/positions/:id" element={<PositionDetailsPage />} />
                        <Route path="/positions/add" element={<AddPositionPage />} />
                        <Route path="/admin/overview" element={<AdminRoute><AdminOverviewPage /></AdminRoute>} />
                        <Route path="/admin/users" element={<AdminRoute><UserManagementPage /></AdminRoute>} />
                        <Route path="/admin/activity" element={<AdminRoute><ActivityMonitorPage /></AdminRoute>} />
                        <Route path="*" element={<Navigate to="/" replace />} />
                      </Routes>
                    </main>
                  </SidebarProvider>
                </ProtectedRoute>
              }
            />
          </Routes>
        </Router>
      </AuthProvider>
  )
}