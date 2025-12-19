# Project DAAN Express - React Migration

This is the React frontend migration of Project DAAN Express, a digital analytics platform for asset-based navigation of roads.

## 🚀 Features

- **Interactive Map**: Leaflet-based map with multiple data layer support
- **Data Upload**: Drag-and-drop file upload for vehicle, pothole, IRI, and image data
- **Real-time Analytics**: Charts and metrics powered by Recharts
- **Responsive Design**: Clean, modern UI built with TailwindCSS
- **State Management**: Zustand for efficient state management
- **Collapsible Sidebar**: Toggle-able navigation and controls

## 🛠️ Tech Stack

- **React 19** - Frontend framework
- **Vite** - Build tool and dev server
- **TailwindCSS** - Utility-first CSS framework
- **React Leaflet** - Map integration
- **Recharts** - Data visualization
- **Zustand** - State management
- **React Dropzone** - File upload handling

## 📦 Installation

1. Navigate to the migration directory:
   ```bash
   cd migration
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

4. Open your browser and visit `http://localhost:5173`

## 🏗️ Project Structure

```
migration/
├── src/
│   ├── components/
│   │   ├── Navbar.jsx          # Top navigation bar
│   │   ├── Sidebar.jsx         # Collapsible sidebar
│   │   ├── MapView.jsx         # Leaflet map component
│   │   ├── UploadPanel.jsx     # File upload interface
│   │   └── AnalyticsPanel.jsx  # Data analytics dashboard
│   ├── pages/
│   │   └── Dashboard.jsx       # Main dashboard page
│   ├── store/
│   │   └── useAppStore.js      # Zustand state store
│   ├── hooks/                  # Custom React hooks
│   ├── App.jsx                 # Main app component
│   ├── main.jsx               # App entry point
│   └── index.css              # Global styles with Tailwind
├── public/                    # Static assets
├── tailwind.config.js         # TailwindCSS configuration
├── postcss.config.js          # PostCSS configuration
└── package.json               # Dependencies and scripts
```

## 🎨 UI Components

### Navbar
- Project title and branding
- Sidebar toggle button
- System status indicators
- Settings and controls

### Sidebar
- **Data Upload Tab**: File upload areas for different data types
- **Analytics Tab**: Charts, metrics, and data visualization
- **Map Controls**: Layer toggles and map style selection

### MapView
- Interactive Leaflet map centered on Los Baños, Laguna
- Sample marker with popup
- Support for multiple data layers (vehicles, potholes, IRI)
- Map style switching (OpenStreetMap, Satellite, 3D Terrain, Dark Mode)

### Upload Panel
- Drag-and-drop file upload
- Support for CSV, XLS, XLSX files
- Image upload for pothole detections
- Upload progress and validation

### Analytics Panel
- Key metrics cards
- Interactive charts (pie charts, bar charts)
- Data quality indicators
- Export functionality

## 🗺️ Map Features

- **Default Location**: Los Baños, Laguna (14.1667°N, 121.2500°E)
- **Default Zoom**: 13
- **Map Styles**: 4 different tile layers
- **Markers**: Color-coded markers for different data types
- **Popups**: Detailed information on marker click
- **Responsive**: Works on desktop and tablet

## 📊 Data Support

- **Vehicle Detection Data**: GPS coordinates, timestamps, vehicle types
- **Pothole Detection Data**: Location, severity, size information
- **IRI Sensor Data**: Road roughness measurements
- **Image Data**: Pothole photos for visual analysis

## 🎯 State Management

The app uses Zustand for state management with the following key states:

- UI state (sidebar visibility, current view)
- Map state (center, zoom, style)
- Data state (vehicle, pothole, IRI data)
- Layer controls (visibility toggles)

## 🚀 Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

### Customization

- **Colors**: Modify `tailwind.config.js` for custom color schemes
- **Components**: Add new components in `src/components/`
- **Pages**: Add new pages in `src/pages/`
- **State**: Extend the store in `src/store/useAppStore.js`

## 🔧 Configuration

### TailwindCSS
The project uses TailwindCSS v4 with custom configuration:
- Custom color palette for primary and secondary colors
- Custom shadows and animations
- Responsive design utilities

### Leaflet
- Default marker icons configured
- Custom popup styling
- Multiple tile layer support

## 📱 Responsive Design

The app is designed to work on:
- Desktop (1024px+)
- Tablet (768px - 1023px)
- Mobile (320px - 767px) - with collapsible sidebar

## 🎨 Styling

- **Design System**: Consistent color palette and typography
- **Components**: Reusable UI components with TailwindCSS
- **Animations**: Smooth transitions and hover effects
- **Icons**: Heroicons for consistent iconography

## 🚀 Deployment

To build for production:

```bash
npm run build
```

The built files will be in the `dist/` directory, ready for deployment to any static hosting service.

## 📝 Notes

- This is a UI-only migration of the original Streamlit app
- Backend integration will be added in future iterations
- All file uploads are currently handled in the frontend only
- Map data layers are simulated with sample data

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is part of Project DAAN Express and follows the same licensing terms.