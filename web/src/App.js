import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Link, useNavigate } from 'react-router-dom';
import './App.css';

const AboutOwner = () => (
    <article className="main-content">
        <h2>Станислав Леончик</h2>
        <p>Южный Федеральный Университет</p>
    </article>
);

const FeedBack = () => (
    <article className="main-content">
        <h2>Обратная связь</h2>
        <p>leonchik@sfedu.ru</p>
        <p>tg: @steveleonchik</p>
    </article>
);

const LoginForm = ({ onLogin }) => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');

    const handleSubmit = (event) => {
        event.preventDefault();
        onLogin(username, password);
    };

    return (
        <article className="main-content">
            <form onSubmit={handleSubmit}>
                <input
                    type="text"
                    placeholder="Username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    required
                />
                <input
                    type="password"
                    placeholder="Password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                />
                <button type="submit">Login</button>
            </form>
        </article>
    );
};

const App = () => {
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const navigate = useNavigate();

    const handleLogin = (username, password) => {
        if (username === 'admin' && password === 'admin') {
            setIsLoggedIn(true);
            navigate('/');
        } else {
            alert('Invalid credentials');
        }
    };

    const handleLogout = () => {
        setIsLoggedIn(false);
        navigate('/login');
    };

    return (
        <div className="App">
            <header className="App-header">
                <h2>Trinity</h2>
                {isLoggedIn ? (
                    <button onClick={handleLogout}>Выход</button>
                ) : (
                    <Link to="/login" className="login-section">Войти</Link>
                )}
            </header>
            <div className="content-area">
                <Routes>
                    <Route path="/about-owner" element={<AboutOwner />} />
                    <Route path="/feedback" element={<FeedBack />} />
                    <Route path="/login" element={<LoginForm onLogin={handleLogin} />} />
                </Routes>
            </div>
            <footer className="App-footer">
                Southern Federal University
            </footer>
            <nav className="tab-bar">
                <Link to="/about-owner">О создателе</Link>
                <Link to="/feedback">Обратная связь</Link>
            </nav>
        </div>
    );
};

export default App;
