import { useState, useEffect } from 'react';
import {
    Globe, Settings, FileText, Database,
    CheckCircle, AlertCircle, RefreshCw, Sparkles,
    Zap, Brain, Download, BookOpen, Target
} from 'lucide-react';
import { API_BASE_URL } from './config';
import {
    EmptyState, FileListItem, FileContentItem, MarkdownViewer
} from './components';

interface ScrapedFile {
    filename: string;
    content: Record<string, string> | string;
}

function App() {
    const [baseUrl, setBaseUrl] = useState('');
    const [topic, setTopic] = useState('');
    const [status, setStatus] = useState('Scraping status will appear here.');
    const [statusType, setStatusType] = useState<'normal' | 'error' | 'success'>('normal');
    const [scrapedFiles, setScrapedFiles] = useState<string[]>([]);
    const [selectedFile, setSelectedFile] = useState<ScrapedFile | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [activeTab, setActiveTab] = useState<'scraper' | 'history' | 'settings'>('scraper');
    const [theme, setTheme] = useState<'light' | 'dark'>('dark');
    const [apiStatus, setApiStatus] = useState<'checking' | 'online' | 'offline'>('checking');
    const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
    const [urlFocused, setUrlFocused] = useState(false);
    const [topicFocused, setTopicFocused] = useState(false);

    // Mouse tracking
    useEffect(() => {
        const handleMouseMove = (e: MouseEvent) => {
            setMousePosition({ x: e.clientX, y: e.clientY });
        };
        window.addEventListener('mousemove', handleMouseMove);
        return () => window.removeEventListener('mousemove', handleMouseMove);
    }, []);

    // API health check
    useEffect(() => {
        checkApiHealth();
        const interval = setInterval(checkApiHealth, 30000);
        return () => clearInterval(interval);
    }, []);

    // Load theme and files
    useEffect(() => {
        const savedTheme = localStorage.getItem('theme') as 'light' | 'dark';
        if (savedTheme) {
            setTheme(savedTheme);
        }
        listScrapedFiles();
    }, []);

    useEffect(() => {
        localStorage.setItem('theme', theme);
        document.documentElement.className = theme;
    }, [theme]);

    const checkApiHealth = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/health`);
            if (response.ok) {
                setApiStatus('online');
            } else {
                setApiStatus('offline');
            }
        } catch (error) {
            setApiStatus('offline');
        }
    };

    const scrapeUrl = async () => {
        if (!baseUrl.trim() || !topic.trim()) {
            setStatus('Please enter both a website URL and a topic.');
            setStatusType('error');
            return;
        }

        if (apiStatus !== 'online') {
            setStatus('Backend API is offline. Please check the connection.');
            setStatusType('error');
            return;
        }

        setIsLoading(true);
        setStatus('Starting scrape...');
        setStatusType('normal');

        const fullUrl = `${baseUrl.replace(/\/+$/, '')}/${topic.replace(/^\/+|\/+$/g, '')}/`;
        console.log('Constructed URL:', fullUrl);

        try {
            const response = await fetch(`${API_BASE_URL}/api/scrape`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: fullUrl })
            });

            console.log('Scrape Response Status:', response.status, response.statusText);

            if (!response.ok) {
                const text = await response.text();
                console.log('Scrape Response Body:', text.slice(0, 200));
                setStatus(`Error: HTTP ${response.status} - ${text.slice(0, 100) || response.statusText}`);
                setStatusType('error');
                return;
            }

            const result = await response.json();
            setStatus(`Success: ${result.message}. Pages found: ${result.pages_found}`);
            setStatusType('success');
            await listScrapedFiles();
        } catch (error: unknown) {
            console.error('Scrape Error:', error);
            setStatus(`Network Error: ${error instanceof Error ? error.message : String(error)}`);
            setStatusType('error');
        } finally {
            setIsLoading(false);
        }
    };

    const listScrapedFiles = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/list-scraped-data`);
            console.log('List Files Response Status:', response.status, response.statusText);

            if (!response.ok) {
                const text = await response.text();
                console.log('List Files Response Body:', text.slice(0, 200));
                setScrapedFiles([]);
                return;
            }

            const result = await response.json();
            if (result.files && result.files.length > 0) {
                const filenames = result.files.map((file: any) =>
                    typeof file === 'string' ? file : file.filename
                );
                setScrapedFiles(filenames);
            } else {
                setScrapedFiles([]);
            }
        } catch (error: unknown) {
            console.error('List Files Error:', error);
            setScrapedFiles([]);
        }
    };

    const loadFileContent = async (filename: string) => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/get-scraped-data/${filename}`);
            console.log('Load File Response Status:', response.status, response.statusText);

            if (!response.ok) {
                const text = await response.text();
                console.log('Load File Response Body:', text.slice(0, 200));
                setSelectedFile({
                    filename,
                    content: { error: `Error loading file ${filename}: HTTP ${response.status} - ${text.slice(0, 100) || response.statusText}` }
                });
                return;
            }

            const data = await response.json();
            if (filename.endsWith('.md')) {
                setSelectedFile({
                    filename,
                    content: typeof data === 'string' ? data : data.content || JSON.stringify(data, null, 2)
                });
            } else if (typeof data === 'object' && data !== null) {
                setSelectedFile({
                    filename,
                    content: data
                });
            } else {
                setSelectedFile({
                    filename,
                    content: { data: JSON.stringify(data, null, 2) }
                });
            }
        } catch (error: unknown) {
            console.error('Load File Error:', error);
            setSelectedFile({
                filename,
                content: { error: `Network Error loading file ${filename}: ${error instanceof Error ? error.message : String(error)}` }
            });
        }
    };

    const copyToClipboard = (text: string) => {
        navigator.clipboard.writeText(text);
    };

    return (
        <div className="min-h-screen text-white overflow-x-hidden relative" style={{ background: '#0A0B0E' }}>
            {/* Animated Background */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none">
                <div
                    className="absolute w-96 h-96 bg-blue-500/20 rounded-full blur-3xl animate-pulse"
                    style={{ top: '10%', left: '10%', animation: 'float 8s ease-in-out infinite' }}
                />
                <div
                    className="absolute w-96 h-96 bg-emerald-500/20 rounded-full blur-3xl animate-pulse"
                    style={{ bottom: '10%', right: '10%', animation: 'float 10s ease-in-out infinite reverse' }}
                />
                <div
                    className="absolute w-64 h-64 bg-cyan-500/10 rounded-full blur-3xl"
                    style={{ top: `${mousePosition.y / 20}px`, left: `${mousePosition.x / 20}px`, transition: 'all 0.3s ease-out' }}
                />
            </div>

            {/* Header */}
            <header className="relative z-10 px-4 md:px-8 py-6 flex flex-col md:flex-row items-center justify-between gap-4 md:gap-0">
                <div className="flex items-center gap-3">
                    <div className="relative">
                        <Brain className="w-10 h-10 text-blue-400" />
                        <Sparkles className="w-4 h-4 text-emerald-400 absolute -top-1 -right-1 animate-pulse" />
                    </div>
                    <div>
                        <h1 className="text-2xl font-bold gradient-text">WebGenius</h1>
                        <p className="text-xs text-blue-300">Extract. Transform. Discover.</p>
                    </div>
                </div>

                <div className="flex items-center gap-4">
                    <div className={`flex items-center gap-2 px-4 py-2 rounded-full glass ${apiStatus === 'online' ? 'border-emerald-500/50' : 'border-red-500/50'
                        }`}>
                        <div className={`w-2 h-2 rounded-full ${apiStatus === 'online' ? 'bg-emerald-400' : 'bg-red-400'
                            } animate-pulse`} />
                        <span className="text-sm font-medium">
                            {apiStatus === 'online' ? 'API Online' : apiStatus === 'offline' ? 'API Offline' : 'Checking...'}
                        </span>
                    </div>
                </div>
            </header>

            {/* API Offline Warning */}
            {apiStatus === 'offline' && (
                <div className="relative z-10 mx-4 md:mx-8 mb-4 glass border-l-4 border-red-500 p-4 rounded-r-lg">
                    <div className="flex items-center">
                        <AlertCircle className="w-5 h-5 text-red-500 mr-3" />
                        <div>
                            <p className="font-medium text-red-400">Backend API is offline</p>
                            <p className="text-sm text-red-300">Please start the backend server</p>
                        </div>
                    </div>
                </div>
            )}

            {/* Navigation */}
            <nav className="relative z-10 px-4 md:px-8 py-4 flex gap-4 md:gap-6 overflow-x-auto pb-2 custom-scrollbar">
                {[
                    { id: 'scraper', label: 'Scraper', icon: Globe },
                    { id: 'history', label: 'Files', icon: BookOpen },
                    { id: 'settings', label: 'Settings', icon: Settings }
                ].map(({ id, label, icon: Icon }) => (
                    <button
                        key={id}
                        onClick={() => setActiveTab(id as 'scraper' | 'history' | 'settings')}
                        className={`px-4 py-2 rounded-lg glass transition-all duration-300 hover:scale-105 hover:shadow-lg hover:shadow-blue-500/20 whitespace-nowrap flex-shrink-0 ${activeTab === id ? 'bg-white/10' : ''
                            }`}
                    >
                        <Icon className="w-4 h-4 inline mr-2" />
                        {label}
                    </button>
                ))}
            </nav>

            {/* Main Content */}
            <main className="relative z-10 px-4 md:px-8 py-8 max-w-6xl mx-auto">
                {/* Scraper Tab */}
                {activeTab === 'scraper' && (
                    <div>
                        {/* Hero Section */}
                        <div className="text-center mb-8 md:mb-12">
                            <h2 className="text-3xl md:text-5xl font-bold mb-4 md:mb-6 gradient-text">
                                AI Powered Web Extraction
                            </h2>
                            <p className="text-lg md:text-xl text-blue-200 max-w-2xl mx-auto">
                                Extract structured data from any site instantly.
                            </p>
                        </div>

                        {/* Feature Cards */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
                            {[
                                { icon: Zap, title: 'Lightning Fast', desc: 'Extract docs in seconds', color: 'from-blue-500 to-cyan-500' },
                                { icon: Target, title: 'Precise Extraction', desc: 'AI driven accuracy', color: 'from-emerald-500 to-teal-500' },
                                { icon: Brain, title: 'AI Enhanced', desc: 'Smart content parsing', color: 'from-cyan-500 to-blue-500' }
                            ].map((feature, i) => (
                                <div
                                    key={i}
                                    className="glass border border-blue-500/50 rounded-2xl p-6 hover:scale-105 transition-all duration-300 hover:shadow-2xl cursor-pointer group"
                                >
                                    <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${feature.color} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300`}>
                                        <feature.icon className="w-6 h-6 text-white" />
                                    </div>
                                    <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
                                    <p className="text-sm text-blue-300">{feature.desc}</p>
                                </div>
                            ))}
                        </div>

                        {/* Extraction Form */}
                        <div className="glass border border-blue-500/50 rounded-3xl p-6 md:p-8 shadow-2xl mb-8">
                            <div className="flex items-center gap-3 mb-8">
                                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center">
                                    <Zap className="w-6 h-6 text-white" />
                                </div>
                                <h3 className="text-xl md:text-2xl font-bold">Start New Extraction</h3>
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                                {/* URL Input */}
                                <div>
                                    <label className="block text-sm font-medium mb-3 text-blue-300">
                                        Documentation Website
                                    </label>
                                    <div
                                        className={`glass border border-blue-500/50 rounded-2xl transition-all duration-300 ${urlFocused ? 'ring-2 ring-blue-500 shadow-lg shadow-blue-500/30' : ''
                                            }`}
                                    >
                                        <div className="flex items-center gap-3 px-4 py-4">
                                            <Globe className="w-5 h-5 text-blue-400 flex-shrink-0" />
                                            <input
                                                type="text"
                                                value={baseUrl}
                                                onChange={(e) => setBaseUrl(e.target.value)}
                                                placeholder="https://docs.example.com"
                                                className="flex-1 bg-transparent outline-none border-0 focus:ring-0 focus-visible:ring-0 focus-visible:ring-offset-0 text-white placeholder-blue-400/50 w-full min-w-0"
                                                onFocus={() => setUrlFocused(true)}
                                                onBlur={() => setUrlFocused(false)}
                                            />
                                        </div>
                                    </div>
                                </div>

                                {/* Topic Input */}
                                <div>
                                    <label className="block text-sm font-medium mb-3 text-cyan-300">
                                        Topic/Section
                                    </label>
                                    <div
                                        className={`glass border border-cyan-500/50 rounded-2xl transition-all duration-300 ${topicFocused ? 'ring-2 ring-cyan-500 shadow-lg shadow-cyan-500/30' : ''
                                            }`}
                                    >
                                        <div className="flex items-center gap-3 px-4 py-4">
                                            <BookOpen className="w-5 h-5 text-cyan-400 flex-shrink-0" />
                                            <input
                                                type="text"
                                                value={topic}
                                                onChange={(e) => setTopic(e.target.value)}
                                                onKeyPress={(e) => e.key === 'Enter' && scrapeUrl()}
                                                placeholder="getting-started"
                                                className="flex-1 bg-transparent outline-none border-0 focus:ring-0 focus-visible:ring-0 focus-visible:ring-offset-0 text-white placeholder-cyan-400/50 w-full min-w-0"
                                                onFocus={() => setTopicFocused(true)}
                                                onBlur={() => setTopicFocused(false)}
                                            />
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* CTA Button */}
                            <button
                                onClick={scrapeUrl}
                                disabled={!baseUrl.trim() || !topic.trim() || isLoading || apiStatus !== 'online'}
                                className="w-full py-4 rounded-xl bg-gradient-to-r from-blue-600 via-cyan-600 to-emerald-600 bg-size-200 hover:bg-pos-100 transition-all duration-500 font-semibold text-lg shadow-lg hover:shadow-2xl hover:shadow-blue-500/50 hover:scale-105 transform flex items-center justify-center gap-3 group disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
                            >
                                <Zap className={`w-5 h-5 ${isLoading ? 'animate-spin' : 'group-hover:animate-pulse'}`} />
                                {isLoading ? 'Extracting...' : 'Start Extraction'}
                                <Sparkles className="w-5 h-5 group-hover:rotate-180 transition-transform duration-500" />
                            </button>
                        </div>

                        {/* Status Section */}
                        <div className="glass border border-blue-500/50 rounded-2xl p-6">
                            <div className="flex items-center gap-3 mb-4">
                                <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500/20 to-emerald-500/20 flex items-center justify-center">
                                    {statusType === 'error' && <AlertCircle className="w-5 h-5 text-red-400" />}
                                    {statusType === 'success' && <CheckCircle className="w-5 h-5 text-emerald-400" />}
                                    {statusType === 'normal' && <Target className="w-5 h-5 text-blue-400" />}
                                </div>
                                <h3 className="text-xl font-semibold">
                                    {statusType === 'error' ? 'Error' :
                                        statusType === 'success' ? 'Complete' :
                                            'Status'}
                                </h3>
                            </div>

                            <div className={`flex items-center gap-3 py-3 px-4 rounded-xl border ${statusType === 'error' ? 'bg-red-900/20 border-red-500/50' :
                                statusType === 'success' ? 'bg-emerald-900/20 border-emerald-500/50' :
                                    'bg-slate-900/50 border-blue-500/50'
                                }`}>
                                <div className={`w-2 h-2 rounded-full animate-pulse flex-shrink-0 ${statusType === 'error' ? 'bg-red-400' :
                                    statusType === 'success' ? 'bg-emerald-400' :
                                        'bg-blue-400/50'
                                    }`} />
                                <p className={`break-words ${statusType === 'error' ? 'text-red-300' :
                                    statusType === 'success' ? 'text-emerald-300' :
                                        'text-blue-300/70'
                                    }`}>{status}</p>
                            </div>
                        </div>
                    </div>
                )}

                {/* Files Tab */}
                {activeTab === 'history' && (
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        <div className="glass border border-blue-500/20 rounded-2xl p-6">
                            <div className="flex items-center justify-between mb-6">
                                <div className="flex items-center">
                                    <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-violet-500 to-purple-500 flex items-center justify-center mr-3">
                                        <Database className="w-6 h-6 text-white" />
                                    </div>
                                    <h2 className="text-xl font-semibold">Library</h2>
                                </div>
                                <button
                                    onClick={listScrapedFiles}
                                    className="px-3 py-2 glass rounded-lg hover:bg-white/10 transition-all duration-300"
                                >
                                    <RefreshCw className="w-4 h-4 inline mr-2" />
                                    Refresh
                                </button>
                            </div>

                            {scrapedFiles.length === 0 ? (
                                <EmptyState
                                    icon={FileText}
                                    title="No documentation found"
                                    description="Start by extracting some documentation content"
                                    action={{
                                        label: "Go to Scraper",
                                        onClick: () => setActiveTab('scraper')
                                    }}
                                />
                            ) : (
                                <div className="space-y-3 max-h-[600px] overflow-y-auto custom-scrollbar">
                                    {scrapedFiles.map((filename) => (
                                        <FileListItem
                                            key={filename}
                                            filename={filename}
                                            isSelected={selectedFile?.filename === filename}
                                            onClick={() => loadFileContent(filename)}
                                            icon={FileText}
                                        />
                                    ))}
                                </div>
                            )}
                        </div>

                        <div className="glass border border-blue-500/20 rounded-2xl p-6">
                            <div className="flex items-center justify-between mb-6">
                                <div className="flex items-center">
                                    <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center mr-3">
                                        <Brain className="w-6 h-6 text-white" />
                                    </div>
                                    <h2 className="text-xl font-semibold">Viewer</h2>
                                </div>
                                {selectedFile && (
                                    <button
                                        onClick={() => {
                                            const dataStr = JSON.stringify(selectedFile.content, null, 2);
                                            const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr);
                                            const linkElement = document.createElement('a');
                                            linkElement.setAttribute('href', dataUri);
                                            linkElement.setAttribute('download', selectedFile.filename);
                                            linkElement.click();
                                        }}
                                        className="px-3 py-2 glass rounded-lg hover:bg-white/10 transition-all duration-300"
                                    >
                                        <Download className="w-4 h-4 inline mr-2" />
                                        Export
                                    </button>
                                )}
                            </div>

                            {!selectedFile ? (
                                <EmptyState
                                    icon={Database}
                                    title="Select a document"
                                    description="Choose a file from the library to view its content"
                                />
                            ) : selectedFile.filename.endsWith('.md') ? (
                                <MarkdownViewer
                                    content={typeof selectedFile.content === 'string' ? selectedFile.content : JSON.stringify(selectedFile.content, null, 2)}
                                    filename={selectedFile.filename}
                                    theme={theme}
                                />
                            ) : (
                                <div className="space-y-4 max-h-[800px] overflow-y-auto custom-scrollbar">
                                    {typeof selectedFile.content === 'string' ? (
                                        <div className="p-4 bg-gray-800/50 rounded-lg">
                                            <pre className="whitespace-pre-wrap text-sm text-gray-200">
                                                {selectedFile.content}
                                            </pre>
                                        </div>
                                    ) : (
                                        Object.entries(selectedFile.content).map(([url, content]) => (
                                            <FileContentItem
                                                key={url}
                                                url={url}
                                                content={typeof content === 'string' ? content : JSON.stringify(content, null, 2)}
                                                theme={theme}
                                                onCopyUrl={copyToClipboard}
                                                onCopyContent={copyToClipboard}
                                            />
                                        ))
                                    )}
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {/* Settings Tab */}
                {activeTab === 'settings' && (
                    <div className="glass border border-blue-500/20 rounded-2xl p-6 md:p-8">
                        <h2 className="text-2xl font-semibold mb-8">Settings</h2>

                        <div className="space-y-8">
                            <div>
                                <h3 className="text-lg font-medium mb-4 text-blue-200">API Configuration</h3>
                                <div className="glass border border-blue-400/20 rounded-xl p-4">
                                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-2 md:gap-0">
                                        <div>
                                            <p className="font-medium text-white">Backend URL</p>
                                            <p className="text-sm text-blue-300 break-all">{API_BASE_URL}</p>
                                        </div>
                                        <div className={`self-start md:self-auto px-3 py-1 rounded-full text-xs font-medium ${apiStatus === 'online' ? 'bg-emerald-500/20 text-emerald-400' :
                                            apiStatus === 'offline' ? 'bg-red-500/20 text-red-400' :
                                                'bg-yellow-500/20 text-yellow-400'
                                            }`}>
                                            {apiStatus}
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div>
                                <h3 className="text-lg font-medium mb-4 text-blue-200">About</h3>
                                <div className="glass border border-blue-400/20 rounded-xl p-4">
                                    <p className="text-sm text-blue-300">
                                        WebGenius - Advanced documentation scraping tool with AI-powered content extraction.
                                        Built with React, TypeScript, and FastAPI.
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </main>
        </div>
    );
}

export default App;
