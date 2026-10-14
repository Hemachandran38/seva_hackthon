import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { PublicLayout } from './components/layout/PublicLayout';
import { HomePage } from './pages/HomePage';
import { ReportIssuePage } from './pages/ReportIssuePage';
import { TrackComplaintPage } from './pages/TrackComplaintPage';
import { AllIssuesPage } from './pages/AllIssuesPage';
import { DashboardPage } from './pages/DashboardPage';
import { NotFoundPage } from './pages/NotFoundPage';
import './styles/tokens.css';
import './styles/global.css';
import './styles/components.css';

export default function App(){return <BrowserRouter><Routes><Route element={<PublicLayout/>}><Route index element={<HomePage/>}/><Route path="report" element={<ReportIssuePage/>}/><Route path="track" element={<TrackComplaintPage/>}/><Route path="issues" element={<AllIssuesPage/>}/><Route path="dashboard" element={<DashboardPage/>}/><Route path="*" element={<NotFoundPage/>}/></Route></Routes></BrowserRouter>}
