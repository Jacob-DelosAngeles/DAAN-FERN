import React from 'react';
import Sidebar from '../components/Sidebar';
import MapArea from '../components/MapArea';

const Dashboard = () => {
  return (
    <div className="flex h-[calc(100vh-64px)] overflow-hidden">
      <Sidebar />
      <MapArea />
    </div>
  );
};

export default Dashboard;
