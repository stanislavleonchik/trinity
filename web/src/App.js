import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import axios from 'axios';
import './App.css';

const backendAddress = 'http://127.0.0.1:5000';

const UploadFile = ({ onResult, setLoading }) => {
    const [file, setFile] = useState(null);

    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
    };

    const handleFileUpload = async () => {
        if (file) {
            setLoading(true);

            const formData = new FormData();
            formData.append('file', file);

            try {
                const response = await axios.post(`${backendAddress}/upload-pdf`, formData, {
                    headers: {
                        'Content-Type': 'multipart/form-data',
                    },
                });
                onResult(response.data);
            } catch (error) {
                console.error('Error uploading file:', error);
            } finally {
                setLoading(false);
            }
        }
    };

    return (
        <div className="form-section">
            <h3>Upload File</h3>
            <div className="form-group">
                <input type="file" onChange={handleFileChange} className="form-input-file"/>
                <button onClick={handleFileUpload} className="form-button">Upload File</button>
            </div>
        </div>
    );
};

const EnterUrl = ({ onResult, setLoading }) => {
    const [url, setUrl] = useState('');

    const handleUrlChange = (e) => {
        setUrl(e.target.value);
    };

    const handleUrlSubmit = async () => {
        setLoading(true);

        try {
            const response = await axios.get(`${backendAddress}/web`, {
                params: { url },
            });
            onResult(response.data);
        } catch (error) {
            console.error('Error fetching URL data:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="form-section">
            <h3>Enter URL</h3>
            <div className="form-group">
                <input
                    type="text"
                    placeholder="URL of article"
                    value={url}
                    onChange={handleUrlChange}
                    className="form-input"
                />
                <button onClick={handleUrlSubmit} className="form-button">Submit URL</button>
            </div>
        </div>
    );
};

const Results = ({ data, isLoading }) => {
    return (
        <div className="results-section">
            {isLoading ? (
                <p className="loading-message">Loading...</p>
            ) : (
                <>
                    {data && data.hash ? (
                        <div className="message-container">
                            <p className="message">Message: {data.message}</p>
                        </div>
                    ) : (
                        <div className="no-data-container">
                            <p className="no-data-message">No data available</p>
                        </div>
                    )}
                </>
            )}
        </div>
    );
};

const Collocations = ({ data }) => {
    if (!Array.isArray(data)) {
        return <p>No collocations available</p>;
    }

    return (
        <div className="collocations-section">
            <h2>Collocations</h2>
            <ul>
                {data.map((item) => (
                    <li key={item.coloc}>
                        <h3>{item.coloc}</h3>
                        <p>Количество упоминаний: {item.count}</p>
                        <p>Перевод: {item.translation}</p>
                    </li>
                ))}
            </ul>
        </div>
    );
};

const Grammar = ({ data, isLoading }) => {
    const [userInputs, setUserInputs] = useState(data.map(() => ''));

    const handleInputChange = (index, value) => {
        const newInputs = [...userInputs];
        newInputs[index] = value;
        setUserInputs(newInputs);
    };

    return (
        <div className="grammar-section">
            <h2>Grammar Exercises</h2>
            <ul>
                {isLoading ? (
                    <p className="loading-message">Loading...</p>
                ) : (
                    <>
                        {data.map((item, index) => (
                            <li key={index}>
                                <p>{item.sentence}</p>
                                <p>Исходная форма глагола: {item.raw_verb}</p>
                                <input
                                    type="text"
                                    value={userInputs[index]}
                                    onChange={(e) => handleInputChange(index, e.target.value)}
                                    style={{
                                        backgroundColor: userInputs[index].toLowerCase() === item.ready_verb.toLowerCase() ? 'lightgreen' : 'white'
                                    }}
                                />
                            </li>
                        ))}
                    </>
                )}
            </ul>
        </div>
    );
};

const App = () => {
    const [resultData, setResultData] = useState(null);
    const [activeTab, setActiveTab] = useState('');
    const [collocations, setCollocations] = useState([]);
    const [grammar, setGrammar] = useState([]);
    const [fileHash, setFileHash] = useState('');
    const [isLoading, setLoading] = useState(false);

    const handleResult = (data) => {
        setResultData(data);
        setFileHash(data.hash || '');
        setActiveTab('');
        setLoading(false);
    };

    const fetchCollocations = async () => {
        setLoading(true);

        try {
            const response = await axios.get(`${backendAddress}/collocations`, {
                headers: {
                    'hash': fileHash
                }
            });
            if (Array.isArray(response.data)) {
                setCollocations(response.data);
                setActiveTab('terms');
            } else {
                console.error('Unexpected response format for collocations:', response.data);
            }
        } catch (error) {
            console.error('Error fetching collocations:', error);
        } finally {
            setLoading(false);
        }
    };

    const fetchGrammar = async () => {
        setLoading(true);

        try {
            const response = await axios.get(`${backendAddress}/tense`, {
                headers: {
                    'hash': fileHash
                }
            });
            if (Array.isArray(response.data)) {
                setGrammar(response.data);
                setActiveTab('grammar');
            } else {
                console.error('Unexpected response format for grammar:', response.data);
            }
        } catch (error) {
            console.error('Error fetching grammar:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <Router>
            <div className="App">
                <header className="App-header">
                    <h2 style={{color: '#61dafb', fontStyle: 'italic'}}>Trinity</h2>
                </header>
                <div className="input-section">
                    <Routes>
                        <Route path="/" element={<UploadFile onResult={handleResult} setLoading={setLoading} />} />
                        <Route path="/url" element={<EnterUrl onResult={handleResult} setLoading={setLoading} />} />
                    </Routes>
                </div>
                <Results data={resultData} isLoading={isLoading} />
                <div className="tab-buttons">
                    <button onClick={fetchCollocations} disabled={!fileHash || isLoading}>
                        TERMS
                    </button>
                    <button onClick={fetchGrammar} disabled={!fileHash || isLoading}>
                        GRAMMAR
                    </button>
                </div>
                <div className="results-content">
                    {activeTab === 'terms' && <Collocations data={collocations} />}
                    {activeTab === 'grammar' && <Grammar data={grammar} isLoading={isLoading} />}
                </div>
                <nav className="tab-bar">
                    <Link to="/" className={activeTab === '' ? 'active' : ''} onClick={() => setActiveTab('')}>
                        Upload File
                    </Link>
                    <Link to="/url" className={activeTab === '' ? 'active' : ''} onClick={() => setActiveTab('')}>
                        Enter URL
                    </Link>
                </nav>
            </div>
        </Router>
    );
};

export default App;
