import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_URL = 'http://localhost:8000';

function App() {
  const [elapsedTime, setElapsedTime] = useState('00:00:00');
  const [isRunning, setIsRunning] = useState(false);

  // Busca o tempo a cada segundo
  useEffect(() => {
    const interval = setInterval(() => {
      fetchElapsedTime();
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  const fetchElapsedTime = async () => {
    try {
      const response = await axios.get(`${API_URL}/timer/elapsed`);
      setElapsedTime(response.data.elapsed_formatted);
      setIsRunning(response.data.is_running);
    } catch (error) {
      console.error('Erro ao buscar tempo:', error);
    }
  };

  const handleStart = async () => {
    try {
      await axios.post(`${API_URL}/timer/start`);
      fetchElapsedTime();
    } catch (error) {
      console.error('Erro ao iniciar:', error);
    }
  };

  const handlePause = async () => {
    try {
      await axios.post(`${API_URL}/timer/pause`);
      fetchElapsedTime();
    } catch (error) {
      console.error('Erro ao pausar:', error);
    }
  };

    const handleReset = async () => {
    try {
      await axios.post(`${API_URL}/timer/reset`);
      fetchElapsedTime();
    } catch (error) {
      console.error('Erro ao resetar:', error);
    }
  };

  

  return (
    <div className="App">
      <h1>Pomodoro Timer</h1>
      <div className="timer-display">
        {elapsedTime}
      </div>
      <div className="buttons">
        <button 
          onClick={handleStart} 
          disabled={isRunning}
          className="btn-start"
        >
          Iniciar
        </button>
        <button 
          onClick={handlePause} 
          disabled={!isRunning}
          className="btn-pause"
        >
          Pausar
        </button>
      </div>
      <div className="status">
        Status: {isRunning ? '▶️ Rodando' : '⏸️ Pausado'}
      </div>
         <button 
          onClick={handleReset}
          className="btn-reset"
        >
          Recomeçar
        </button>
    </div>
  );
}

export default App;