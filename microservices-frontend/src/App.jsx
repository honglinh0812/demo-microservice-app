import { useState } from 'react';
import { Button } from '@/components/ui/button.jsx';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx';
import UserManager from './components/UserManager.jsx';
import ProductManager from './components/ProductManager.jsx';
import './App.css';

function App() {
  const [apiStatus, setApiStatus] = useState('checking');

  const checkApiStatus = async () => {
    try {
      const response = await fetch('http://192.168.138.132:31111/api');
      if (response.ok) {
        setApiStatus('connected');
      } else {
        setApiStatus('error');
      }
    } catch (error) {
      setApiStatus('error');
    }
  };

  // Check API status on component mount
  useState(() => {
    checkApiStatus();
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-6xl mx-auto">
        <header className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Microservices Demo App v1
          </h1>
          <p className="text-gray-600 mb-4">
            Frontend React App + Backend Flask API
          </p>
          
          {/* API Status */}
          <div className="flex items-center justify-center gap-2 mb-4">
            <span className="text-sm">API Status:</span>
            <span className={`px-2 py-1 rounded text-sm ${
              apiStatus === 'connected' ? 'bg-green-100 text-green-800' :
              apiStatus === 'error' ? 'bg-red-100 text-red-800' :
              'bg-yellow-100 text-yellow-800'
            }`}>
              {apiStatus === 'connected' ? 'Connected' :
               apiStatus === 'error' ? 'Disconnected' :
               'Checking...'}
            </span>
            <Button onClick={checkApiStatus} variant="outline" size="sm">
              Refresh
            </Button>
          </div>
        </header>

        <main>
          <Tabs defaultValue="users" className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="users">User Management</TabsTrigger>
              <TabsTrigger value="products">Product Management</TabsTrigger>
            </TabsList>
            
            <TabsContent value="users" className="mt-6">
              <div className="flex justify-center">
                <UserManager />
              </div>
            </TabsContent>
            
            <TabsContent value="products" className="mt-6">
              <div className="flex justify-center">
                <ProductManager />
              </div>
            </TabsContent>
          </Tabs>
        </main>

        <footer className="text-center mt-12 text-gray-500 text-sm">
          <p>Microservices Architecture Demo v1</p>
          <p>Frontend: React + Vite | Backend: Flask + SQLite</p>
        </footer>
      </div>
    </div>
  );
}

export default App;

