import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom"
import { SidebarProvider } from "@/components/ui/sidebar"
import { AppSidebar } from "@/components/app-sidebar"
import { PositionsPage } from "@/components/positions-page"
import { PositionDetailsPage } from "@/components/position-page"
import { AddPositionPage } from "@/components/search-page"
import { AdminOverviewPage } from "@/components/admin/overview-page"
import { UserManagementPage } from "@/components/admin/user-management-page"
import { ActivityMonitorPage } from "@/components/admin/activity-monitor-page"
import { LoginPage } from "@/components/login-page"
import { ProtectedRoute } from "@/components/protected-route"
import { AdminRoute } from "@/components/admin-route"
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
                    <main className="flex-1 overflow-hidden">
                      <Routes>
                        <Route path="/" element={<PositionsPage />} />
                        <Route path="/positions/:id" element={<PositionDetailsPage />} />
                        <Route path="/add-position" element={<AddPositionPage />} />
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