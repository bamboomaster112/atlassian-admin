import { Routes, Route } from 'react-router-dom'
import Sidebar from './components/common/Sidebar'
import DashboardPage from './pages/DashboardPage'
import JiraUsersPage from './pages/JiraUsersPage'
import CustomFieldsPage from './pages/CustomFieldsPage'
import SchemesPage from './pages/SchemesPage'
import JiraProjectsPage from './pages/JiraProjectsPage'
import ConfluenceSpacesPage from './pages/ConfluenceSpacesPage'
import ConfluenceContentPage from './pages/ConfluenceContentPage'
import JSMOverviewPage from './pages/JSMOverviewPage'
import LicensesPage from './pages/LicensesPage'
import PermissionsPage from './pages/PermissionsPage'
import CleanupPage from './pages/CleanupPage'

export default function App() {
  return (
    <div className="app-layout">
      <Sidebar />
      <main className="main-content">
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/jira/users" element={<JiraUsersPage />} />
          <Route path="/jira/custom-fields" element={<CustomFieldsPage />} />
          <Route path="/jira/schemes" element={<SchemesPage />} />
          <Route path="/jira/projects" element={<JiraProjectsPage />} />
          <Route path="/confluence/spaces" element={<ConfluenceSpacesPage />} />
          <Route path="/confluence/content" element={<ConfluenceContentPage />} />
          <Route path="/jsm/overview" element={<JSMOverviewPage />} />
          <Route path="/governance/licenses" element={<LicensesPage />} />
          <Route path="/governance/permissions" element={<PermissionsPage />} />
          <Route path="/governance/cleanup" element={<CleanupPage />} />
        </Routes>
      </main>
    </div>
  )
}
