import React, { useState, useEffect } from 'react';
import './App.css';

interface User {
  id: number;
  email: string;
  full_name: string;
  role: 'tutor' | 'student';
}

interface Classroom {
  id: number;
  title: string;
  invite_code: string;
  teacher_id: number;
  created_at: string;
  students_count: number;
}

const API_BASE_URL = 'http://localhost:8000/api/v1';

export default function App() {
  const [isLogin, setIsLogin] = useState(true);
  const [user, setUser] = useState<User | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  // Поля авторизации
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [role, setRole] = useState<'tutor' | 'student'>('tutor');

  // Поля управления классами
  const [classrooms, setClassrooms] = useState<Classroom[]>([]);
  const [newClassTitle, setNewClassTitle] = useState('');
  const [joinCode, setJoinCode] = useState('');
  const [loadingClasses, setLoadingClasses] = useState(false);

  // Проверяем сохраненный JWT-токен при загрузке страницы
  useEffect(() => {
    const token = localStorage.getItem('teachlab_token');
    if (token) {
      fetch(`${API_BASE_URL}/auth/me`, {
        headers: { Authorization: `Bearer ${token}` }
      })
        .then(res => (res.ok ? res.json() : null))
        .then(data => {
          if (data) {
            setUser(data);
          }
        })
        .catch(() => localStorage.removeItem('teachlab_token'));
    }
  }, []);

  // Загружаем классы при авторизации
  useEffect(() => {
    if (user) {
      fetchClassrooms();
    }
  }, [user]);

  const fetchClassrooms = async () => {
    const token = localStorage.getItem('teachlab_token');
    if (!token) return;

    setLoadingClasses(true);
    try {
      const res = await fetch(`${API_BASE_URL}/classrooms/`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setClassrooms(data);
      }
    } catch {
      // Игнорируем сетевые сбои при polling
    } finally {
      setLoadingClasses(false);
    }
  };

  const handleAuthSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccessMsg(null);

    try {
      if (isLogin) {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password })
        });

        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || 'Неверный логин или пароль');

        localStorage.setItem('teachlab_token', data.access_token);
        setUser(data.user);
      } else {
        const response = await fetch(`${API_BASE_URL}/auth/register`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password, full_name: fullName, role })
        });

        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || 'Ошибка регистрации');

        setSuccessMsg('Аккаунт успешно создан! Войдите под своими данными.');
        setIsLogin(true);
      }
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('teachlab_token');
    setUser(null);
    setClassrooms([]);
    setError(null);
    setSuccessMsg(null);
  };

  // Преподаватель: создание класса
  const handleCreateClass = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newClassTitle.trim()) return;

    setError(null);
    setSuccessMsg(null);
    const token = localStorage.getItem('teachlab_token');

    try {
      const res = await fetch(`${API_BASE_URL}/classrooms/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ title: newClassTitle })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Не удалось создать класс');

      setNewClassTitle('');
      setSuccessMsg(`Класс "${data.title}" создан! Инвайт-код: ${data.invite_code}`);
      fetchClassrooms();
    } catch (err: any) {
      setError(err.message);
    }
  };

  // Ученик: вступление в класс
  const handleJoinClass = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!joinCode.trim()) return;

    setError(null);
    setSuccessMsg(null);
    const token = localStorage.getItem('teachlab_token');

    try {
      const res = await fetch(`${API_BASE_URL}/classrooms/join`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ invite_code: joinCode.trim() })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Не удалось вступить в класс');

      setJoinCode('');
      setSuccessMsg(`Вы успешно вступили в класс "${data.title}"!`);
      fetchClassrooms();
    } catch (err: any) {
      setError(err.message);
    }
  };

  // Преподаватель: перегенерация инвайт-кода
  const handleRegenerateCode = async (classroomId: number) => {
    setError(null);
    const token = localStorage.getItem('teachlab_token');
    try {
      const res = await fetch(`${API_BASE_URL}/classrooms/${classroomId}/regenerate-code`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Ошибка обновления кода');
      setSuccessMsg(`Новый инвайт-код: ${data.invite_code}`);
      fetchClassrooms();
    } catch (err: any) {
      setError(err.message);
    }
  };

  // Преподаватель: удаление класса
  const handleDeleteClass = async (classroomId: number) => {
    if (!confirm('Вы уверены, что хотите удалить этот класс?')) return;
    setError(null);
    const token = localStorage.getItem('teachlab_token');
    try {
      const res = await fetch(`${API_BASE_URL}/classrooms/${classroomId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || 'Ошибка удаления');
      }
      setSuccessMsg('Класс успешно удален.');
      fetchClassrooms();
    } catch (err: any) {
      setError(err.message);
    }
  };

  // Ученик: выход из класса
  const handleLeaveClass = async (classroomId: number) => {
    if (!confirm('Покинуть этот класс?')) return;
    setError(null);
    const token = localStorage.getItem('teachlab_token');
    try {
      const res = await fetch(`${API_BASE_URL}/classrooms/${classroomId}/leave`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || 'Ошибка выхода');
      }
      setSuccessMsg('Вы покинули класс.');
      fetchClassrooms();
    } catch (err: any) {
      setError(err.message);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    alert(`Инвайт-код ${text} скопирован в буфер обмена!`);
  };

  // 1. Экран авторизованного пользователя
  if (user) {
    const isTutor = user.role === 'tutor';

    return (
      <div className="dashboard-card">
        <div className="logo-title">
          <h1>TeachLab</h1>
          <p>Панель управления обучением</p>
        </div>

        {/* Профиль */}
        <div className="user-profile">
          <div className="user-profile-info">
            <p><strong>{user.full_name}</strong></p>
            <p style={{ color: '#94a3b8' }}>{user.email}</p>
            <p>
              <span className={`badge ${user.role}`}>
                {isTutor ? 'Преподаватель' : 'Ученик'}
              </span>
            </p>
          </div>
          <button onClick={handleLogout} className="btn-logout">
            Выйти
          </button>
        </div>

        {error && <div className="error-banner">{error}</div>}
        {successMsg && <div className="success-banner">{successMsg}</div>}

        {/* Блок управления классами */}
        <div className="section-title">
          <h3>{isTutor ? 'Мои учебные классы' : 'Мои курсы и классы'}</h3>
          <span style={{ fontSize: '13px', color: '#94a3b8' }}>
            Всего: {classrooms.length}
          </span>
        </div>

        {/* Форма создания (для Tutor) или вступления (для Student) */}
        {isTutor ? (
          <form onSubmit={handleCreateClass} className="input-row">
            <input
              type="text"
              value={newClassTitle}
              onChange={e => setNewClassTitle(e.target.value)}
              placeholder="Название нового класса (например, Математика 11-А)"
              required
            />
            <button type="submit">Создать класс</button>
          </form>
        ) : (
          <form onSubmit={handleJoinClass} className="input-row">
            <input
              type="text"
              value={joinCode}
              onChange={e => setJoinCode(e.target.value.toUpperCase())}
              placeholder="Введите 6-значный инвайт-код"
              required
            />
            <button type="submit">Вступить в класс</button>
          </form>
        )}

        {/* Список классов */}
        {loadingClasses ? (
          <p style={{ color: '#94a3b8' }}>Загрузка классов...</p>
        ) : classrooms.length === 0 ? (
          <div className="empty-state">
            {isTutor
              ? 'У вас пока нет созданных классов. Создайте первый класс выше!'
              : 'Вы пока не состоите ни в одном классе. Введите инвайт-код от преподавателя выше!'}
          </div>
        ) : (
          <div className="classes-list">
            {classrooms.map(c => (
              <div key={c.id} className="class-card">
                <div className="class-info">
                  <h4>{c.title}</h4>
                  <p>
                    Инвайт-код:
                    <span
                      className="code-tag"
                      title="Нажмите, чтобы скопировать"
                      onClick={() => copyToClipboard(c.invite_code)}
                    >
                      {c.invite_code}
                    </span>
                  </p>
                  <p>Учеников в группе: <strong>{c.students_count}</strong></p>
                </div>

                <div className="card-actions">
                  {isTutor ? (
                    <>
                      <button
                        onClick={() => handleRegenerateCode(c.id)}
                        className="btn-small-secondary"
                        title="Сгенерировать новый инвайт-код"
                      >
                        Новый код
                      </button>
                      <button
                        onClick={() => handleDeleteClass(c.id)}
                        className="btn-small-danger"
                        title="Удалить класс"
                      >
                        Удалить
                      </button>
                    </>
                  ) : (
                    <button
                      onClick={() => handleLeaveClass(c.id)}
                      className="btn-small-danger"
                    >
                      Покинуть
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  }

  // 2. Экран входа и регистрации
  return (
    <div className="auth-card">
      <div className="logo-title">
        <h1>TeachLab</h1>
        <p>Платформа для репетиторов и учеников</p>
      </div>

      <div className="tabs">
        <button
          className={isLogin ? 'active' : ''}
          onClick={() => { setIsLogin(true); setError(null); setSuccessMsg(null); }}
        >
          Вход
        </button>
        <button
          className={!isLogin ? 'active' : ''}
          onClick={() => { setIsLogin(false); setError(null); setSuccessMsg(null); }}
        >
          Регистрация
        </button>
      </div>

      {error && <div className="error-banner">{error}</div>}
      {successMsg && <div className="success-banner">{successMsg}</div>}

      <form onSubmit={handleAuthSubmit}>
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