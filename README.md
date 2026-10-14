# CivicPulse AI - Infrastructure Management Platform

A comprehensive civic technology platform for reporting, tracking, and managing municipal infrastructure complaints with AI-powered priority assessment.

## 🎯 Overview

CivicPulse AI is a full-stack web application that enables citizens to report infrastructure issues (streetlights, potholes, water leaks, etc.) and track their resolution. The system uses machine learning to prioritize complaints and provides real-time visualization through an interactive map dashboard.

## ✨ Features

### Frontend (React + TypeScript)
- **Dashboard**: Real-time interactive map with color-coded infrastructure complaints
- **Explore Issues**: Browse and filter all reported issues with advanced search
- **Report Issue**: User-friendly form to submit new complaints with location
- **Track Complaint**: Monitor the status of specific complaints
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Theme**: Professional municipal design with accessible color scheme

### Backend (FastAPI + Python)
- **REST API**: Complete API for complaint management and tracking
- **SQLite Database**: Persistent storage for all complaints and repairs
- **AI Integration**: Scikit-learn models for priority prediction
- **Real-time Data**: Database-backed complaint tracking
- **Status Management**: Complete workflow from reported to resolved
- **Audit Logging**: Track all changes and actions

### Key Capabilities
✅ Report infrastructure complaints with location  
✅ View all complaints on interactive map  
✅ Filter and search complaints by priority, status, category  
✅ Track complaint status in real-time  
✅ Color-coded priority levels (Critical, High, Medium, Low)  
✅ Responsive design for all devices  
✅ AI-powered priority assessment  
✅ Complete audit trail  

## 📁 Project Structure

```
seva_hackthon/
├── frontend/                    # React frontend
│   ├── src/
│   │   ├── pages/              # Page components
│   │   ├── components/         # Reusable components
│   │   │   └── map/           # Map component with Leaflet
│   │   ├── services/          # API services
│   │   ├── styles/            # Global styles & dashboard CSS
│   │   └── data/              # Sample demo data
│   ├── package.json           # Dependencies
│   └── vite.config.ts        # Vite configuration
│
├── backend/                     # FastAPI backend
│   ├── app/
│   │   ├── main.py            # Entry point
│   │   ├── models/            # Database models
│   │   ├── schemas/           # Request/response schemas
│   │   ├── routers/           # API endpoints
│   │   ├── services/          # Business logic
│   │   └── database.py        # Database setup
│   ├── requirements.txt        # Python dependencies
│   └── civicpulse.db         # SQLite database
│
├── docs/                        # Documentation
├── model/                       # AI models (placeholder)
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Node.js 16+ (for frontend)
- Python 3.11+ (for backend)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Hemachandran38/seva_hackthon.git
   cd seva_hackthon
   ```

2. **Setup Frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   Frontend runs on: `http://localhost:5173`

3. **Setup Backend** (in a new terminal)
   ```bash
   cd backend
   pip install -r requirements.txt
   python -m uvicorn app.main:app --host 127.0.0.1 --port 9000 --reload
   ```
   Backend runs on: `http://127.0.0.1:9000`

### Access the Application
- **Dashboard**: http://localhost:5173/dashboard
- **Explore Issues**: http://localhost:5173/issues
- **Report Issue**: http://localhost:5173/report
- **API Docs**: http://127.0.0.1:9000/docs

## 📊 Dashboard Features

### Interactive Map
- Real-time visualization of all reported issues
- Color-coded markers by priority level
- Zoom and pan controls
- Click markers to see detailed information
- Mobile-friendly touch interactions

### Metrics Cards
- Total Reports count
- Open Issues count
- Critical/High Priority count
- Resolved Issues count

### Recent Reports Table
- List of 10 latest complaints
- Sortable by priority, status, location
- Quick access to full complaint details
- Status and priority badges

## 🎨 Design System

### Color Scheme
- **Primary**: #244b67 (Navy Blue)
- **Deep**: #05344f (Darker Blue)
- **Accent**: #bd8645 (Amber Gold)
- **Critical**: #991b1b (Dark Red)
- **Success**: #397557 (Green)
- **Resolved**: #10b981 (Light Green)

### Priority Levels
- 🔴 **Critical**: Immediate attention required
- 🟠 **High**: Urgent, within 24-48 hours
- 🟡 **Medium**: Normal priority, 1-2 weeks
- 🔵 **Low**: Can be addressed when convenient

## 📱 Complaint Status Workflow

1. **Reported** - Initial complaint received
2. **Under Review** - Being evaluated for priority
3. **Assigned** - Work order assigned to team
4. **In Progress** - Repair/maintenance underway
5. **Awaiting Verification** - Awaiting inspection
6. **Resolved** - Issue completed and verified

## 🔧 Tech Stack

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Leaflet** - Interactive mapping
- **React Router** - Navigation
- **CSS3** - Styling

### Backend
- **FastAPI** - API framework
- **SQLModel** - ORM & validation
- **SQLite** - Database
- **Scikit-learn** - ML models
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation

### DevOps
- **Node.js** - Runtime
- **Python 3.11** - Runtime
- **Git** - Version control
- **npm** - Package management
- **pip** - Package management

## 📚 API Documentation

Full API documentation available at: `http://127.0.0.1:9000/docs` (when backend is running)

### Key Endpoints
- `GET /api/complaints` - List all complaints
- `POST /api/complaints` - Create new complaint
- `GET /api/complaints/{id}` - Get specific complaint
- `PUT /api/complaints/{id}/status` - Update complaint status
- `GET /api/dashboard/stats` - Get dashboard statistics

## 🧪 Sample Data

The application includes 15+ sample complaints with demo data:
- Pre-geolocated in Coimbatore, India
- Various priority levels and statuses
- Real-world inspired issue descriptions
- Used for development and demonstration

## 📝 Environment Variables

### Frontend
No special environment variables required (uses default localhost API)

### Backend
Create `.env` in `backend/` directory:
```
DATABASE_URL=sqlite:///./civicpulse.db
DEBUG=false
```

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Kill process on port 5173 or 9000
lsof -i :5173  # or :9000
kill -9 <PID>
```

### Database Issues
```bash
# Reset database
rm backend/civicpulse.db
python backend/app/seed.py
```

### Frontend Not Loading
```bash
# Clear cache and reinstall
rm -rf frontend/node_modules
npm install
npm run dev
```

## 📄 Documentation

Additional documentation files:
- `docs/SETUP_COMPLETE.md` - Detailed setup instructions
- `docs/PROJECT_SUMMARY.md` - Project overview
- `backend/README.md` - Backend documentation
- `frontend/README.md` - Frontend documentation
- `backend/API_DOCUMENTATION.md` - Detailed API docs

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is created for the Municipal Civic Technology Hackathon.

## 👥 Team

- **Development**: Hemachandran
- **Design**: Municipal Infrastructure Management Themed

## 🙏 Acknowledgments

- OpenStreetMap for map tiles
- React and FastAPI communities
- Leaflet.js for mapping functionality
- All contributors and testers

## 📞 Support

For issues and questions:
1. Check existing GitHub issues
2. Review documentation in `/docs`
3. Check backend/frontend README files
4. Create a new GitHub issue with details

---

**Status**: ✅ Production Ready

**Last Updated**: October 14, 2026

**Version**: 1.0.0

**Repository**: https://github.com/Hemachandran38/seva_hackthon
