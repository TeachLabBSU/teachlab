import React, { useState, useEffect } from 'react';
import './App.css';

interface User {
  id: number;
  email: string;
  full_name: string;
  role: 'tutor' | 'student';
}

const API_BASE_URL = 'http://localhost:8000/api/v1';

export default function App() {
  const [isLogin, setIsLogin] = useState(true);
  const [user, setUser] = useState<User | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Поля формы
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [role, setRole] = useState<'tutor' | 'student'>('tutor');

  // Проверяем сохраненный JWT-токен при загрузке страницы
  useEffect(() => {
    const token = localStorage.getItem('teachlab_token');
    if (token) {
      fetch(`${API_BASE_URL}/auth/me`, {
        headers: { Authorization: `Bearer ${token}` }
      })
        .then(res => (res.ok ? res.json() : null))
        .then(data => { if (data) setUser(data); })
        .catch(() => localStorage.removeItem('teachlab_token'));
    }
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    try {
      if (isLogin) {
        // 1. ВХОД (LOGIN)
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password })
        });

        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || 'Неверный логин или пароль');

        // Сохраняем JWT в памяти браузера
        localStorage.setItem('teachlab_token', data.access_token);
        setUser(data.user);
      } else {
        // 2. РЕГИСТРАЦИЯ (REGISTER)
        const response = await fetch(`${API_BASE_URL}/auth/register`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password, full_name: fullName, role })
        });

        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || 'Ошибка регистрации');

        alert('Успешно! Теперь войдите в аккаунт.');
        setIsLogin(true);
      }
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('teachlab_token');
    setUser(null);
  };

  // Если пользователь уже авторизован:
  if (user) {
    return (
      <div className="auth-card">
        <h2>Личный кабинет TeachLab 🎓</h2>
        <div className="user-profile">
          <p><strong>ФИО:</strong> {user.full_name}</p>
          <p><strong>Email:</strong> {user.email}</p>
          <p>
            <strong>Роль:</strong>{' '}
            <span className={`badge ${user.role}`}>
              {user.role === 'tutor' ? 'Преподаватель / Репетитор' : 'Ученик'}
            </span>
          </p>
        </div>
        <button onClick={handleLogout} className="btn-logout">Выйти из аккаунта</button>
      </div>
    );
  }

  // Экран с формами:
  return (
    <div className="auth-card">
      <div className="logo-title">
        <h1>TeachLab</h1>
        <p>Платформа для репетиторов и учеников</p>
      </div>

      <div className="tabs">
        <button className={isLogin ? 'active' : ''} onClick={() => { setIsLogin(true); setError(null); }}>
          Вход
        </button>
        <button className={!isLogin ? 'active' : ''} onClick={() => { setIsLogin(false); setError(null); }}>
          Регистрация
        </button>
      </div>

      {error && <div className="error-banner">{error}</div>}

      <form onSubmit={handleSubmit}>
        {!isLogin && (
          <>
            <div className="form-group">
              <label>ФИО</label>
              <input
                type="text"
                value={fullName}
                onChange={e => setFullName(e.target.value)}
                required
                placeholder="Иван Иванов"
              />
            </div>

            <div className="form-group">
              <label>Роль в системе</label>
              <select value={role} onChange={e => setRole(e.target.value as any)}>
                <option value="tutor">Репетитор / Преподаватель</option>
                <option value="student">Ученик</option>
              </select>
            </div>
          </>
        )}

        <div className="form-group">
          <label>Email</label>
          <input
            type="email"
            value={email}
            onChange={e => setEmail(e.target.value)}
            required
            placeholder="name@teachlab.by"
          />
        </div>

        <div className="form-group">
          <label>Пароль</label>
          <input
            type="password"
            value={password}
            onChange={e => setPassword(e.target.value)}
            required
            placeholder="••••••••"
          />
        </div>

        <button type="submit" className="btn-submit">
          {isLogin ? 'Войти в аккаунт' : 'Зарегистрироваться'}
        </button>
      </form>
    </div>
  );
}