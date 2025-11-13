import React, { useState, useEffect, useRef } from 'react';
import { Camera, CameraOff, Activity } from 'lucide-react';

export default function Frontend() {
  const [isConnected, setIsConnected] = useState(false);
  const [postureData, setPostureData] = useState({
    posture: 'Connecting...',
    angle: 0
  });
  const [frame, setFrame] = useState(null);
  const wsRef = useRef(null);

  useEffect(() => {
    // Connect to WebSocket
    connectWebSocket();

    return () => {
      // Cleanup on unmount
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const connectWebSocket = () => {
    // Connect to Django WebSocket
    const ws = new WebSocket('ws://localhost:8000/ws/posture/');
    
    ws.onopen = () => {
      console.log('WebSocket Connected');
      setIsConnected(true);
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      // Update frame
      if (data.frame) {
        setFrame(`data:image/jpeg;base64,${data.frame}`);
      }
      
      // Update posture data
      setPostureData({
        posture: data.posture,
        angle: data.angle
      });
    };

    ws.onerror = (error) => {
      console.error('WebSocket Error:', error);
      setIsConnected(false);
    };

    ws.onclose = () => {
      console.log('WebSocket Disconnected');
      setIsConnected(false);
      
      // Attempt to reconnect after 3 seconds
      setTimeout(() => {
        console.log('Attempting to reconnect...');
        connectWebSocket();
      }, 3000);
    };

    wsRef.current = ws;
  };

  const stopStream = () => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ command: 'stop' }));
    }
  };

  const startStream = () => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ command: 'start' }));
    }
  };

  const getPostureColor = () => {
    if (postureData.posture === 'Good Posture') return 'text-green-500';
    if (postureData.posture === 'Bad Posture') return 'text-red-500';
    return 'text-gray-500';
  };

  const getPostureBg = () => {
    if (postureData.posture === 'Good Posture') return 'bg-green-500/10 border-green-500';
    if (postureData.posture === 'Bad Posture') return 'bg-red-500/10 border-red-500';
    return 'bg-gray-500/10 border-gray-500';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2 flex items-center justify-center gap-3">
            <Activity className="w-10 h-10 text-blue-400" />
            Sitting Posture Detector
          </h1>
          <p className="text-gray-400">Real-time posture analysis using AI</p>
        </div>

        {/* Connection Status */}
        <div className="flex justify-center mb-6">
          <div className={`flex items-center gap-2 px-4 py-2 rounded-full ${
            isConnected ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
          }`}>
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-400' : 'bg-red-400'} animate-pulse`}></div>
            {isConnected ? 'Connected' : 'Disconnected'}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Video Feed */}
          <div className="lg:col-span-2">
            <div className="bg-slate-800/50 backdrop-blur rounded-2xl border border-slate-700 overflow-hidden shadow-2xl">
              <div className="aspect-video bg-slate-900 relative">
                {frame ? (
                  <img 
                    src={frame} 
                    alt="Posture Detection Feed" 
                    className="w-full h-full object-contain"
                  />
                ) : (
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="text-center">
                      <Camera className="w-16 h-16 text-slate-600 mx-auto mb-4" />
                      <p className="text-slate-500">Waiting for video feed...</p>
                    </div>
                  </div>
                )}
              </div>
              
              {/* Controls */}
              <div className="p-4 border-t border-slate-700 flex gap-3">
                <button
                  onClick={startStream}
                  disabled={!isConnected}
                  className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-700 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
                >
                  <Camera className="w-5 h-5" />
                  Start
                </button>
                <button
                  onClick={stopStream}
                  disabled={!isConnected}
                  className="flex-1 bg-red-600 hover:bg-red-700 disabled:bg-slate-700 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
                >
                  <CameraOff className="w-5 h-5" />
                  Stop
                </button>
              </div>
            </div>
          </div>

          {/* Stats Panel */}
          <div className="space-y-6">
            {/* Posture Status */}
            <div className={`bg-slate-800/50 backdrop-blur rounded-2xl border-2 ${getPostureBg()} p-6 shadow-2xl`}>
              <div className="text-sm text-gray-400 mb-2">Current Status</div>
              <div className={`text-3xl font-bold ${getPostureColor()}`}>
                {postureData.posture}
              </div>
            </div>

            {/* Angle Measurement */}
            <div className="bg-slate-800/50 backdrop-blur rounded-2xl border border-slate-700 p-6 shadow-2xl">
              <div className="text-sm text-gray-400 mb-2">Hip Angle</div>
              <div className="text-5xl font-bold text-white mb-4">
                {postureData.angle}°
              </div>
              
              {/* Angle Indicator */}
              <div className="w-full bg-slate-700 rounded-full h-3 overflow-hidden">
                <div 
                  className={`h-full transition-all duration-300 ${
                    postureData.angle > 90 ? 'bg-green-500' : 'bg-red-500'
                  }`}
                  style={{ width: `${Math.min((postureData.angle / 180) * 100, 100)}%` }}
                ></div>
              </div>
              <div className="flex justify-between text-xs text-gray-500 mt-2">
                <span>0°</span>
                <span>90°</span>
                <span>180°</span>
              </div>
            </div>

            {/* Guidelines */}
            <div className="bg-slate-800/50 backdrop-blur rounded-2xl border border-slate-700 p-6 shadow-2xl">
              <h3 className="font-semibold text-white mb-3 flex items-center gap-2">
                <Activity className="w-5 h-5 text-blue-400" />
                Posture Tips
              </h3>
              <ul className="space-y-2 text-sm text-gray-400">
                <li className="flex items-start gap-2">
                  <span className="text-green-400 mt-0.5">✓</span>
                  <span>Keep hip angle above 90°</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-400 mt-0.5">✓</span>
                  <span>Sit upright with back straight</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-400 mt-0.5">✓</span>
                  <span>Take breaks every 30 minutes</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-400 mt-0.5">✓</span>
                  <span>Keep feet flat on floor</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}