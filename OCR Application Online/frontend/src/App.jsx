import React, { useState } from 'react';
import axios from 'axios';
import { Scan, AlertCircle, RefreshCw, Sparkles } from 'lucide-react';
import UploadArea from './components/UploadArea';
import ResultsPanel from './components/ResultsPanel';
import LoadingSpinner from './components/LoadingSpinner';

function App() {
    const [isProcessing, setIsProcessing] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);

    const handleFileSelect = async (file) => {
        setIsProcessing(true);
        setError(null);
        setResult(null);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await axios.post('/api/ocr', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });

            if (response.data.success) {
                setResult(response.data.data);
            } else {
                setError(response.data.error || 'Failed to process file');
            }
        } catch (err) {
            console.error('Error processing file:', err);
            setError(
                err.response?.data?.error ||
                err.message ||
                'An error occurred while processing your file'
            );
        } finally {
            setIsProcessing(false);
        }
    };

    const handleReset = () => {
        setResult(null);
        setError(null);
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-neutral-50 via-primary-50/20 to-neutral-50">
            {/* Header */}
            <header className="border-b border-neutral-200 bg-white/80 backdrop-blur-sm sticky top-0 z-10 shadow-sm">
                <div className="max-w-6xl mx-auto px-6 py-4">
                    <div className="flex items-center gap-3">
                        <div className="relative">
                            <div className="absolute inset-0 bg-primary-400 rounded-lg blur-md opacity-30"></div>
                            <div className="relative bg-gradient-to-br from-primary-500 to-primary-600 p-2 rounded-lg">
                                <Scan className="w-6 h-6 text-white" />
                            </div>
                        </div>
                        <div>
                            <h1 className="text-2xl font-bold text-neutral-800">OCR Web Application</h1>
                            <p className="text-sm text-neutral-500">Extract text from images and PDFs instantly</p>
                        </div>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="max-w-6xl mx-auto px-6 py-12">
                {/* Hero Section */}
                {!result && !isProcessing && (
                    <div className="text-center mb-12 animate-fade-in">
                        <div className="inline-flex items-center gap-2 bg-primary-100 text-primary-700 px-4 py-2 rounded-full text-sm font-medium mb-4">
                            <Sparkles className="w-4 h-4" />
                            Powered by Advanced OCR Technology
                        </div>
                        <h2 className="text-4xl md:text-5xl font-bold text-neutral-800 mb-4 text-balance">
                            Transform Images into Text
                        </h2>
                        <p className="text-lg text-neutral-600 max-w-2xl mx-auto text-balance">
                            Upload your documents and let our AI-powered OCR engine extract text with high accuracy.
                            Supports multiple formats and languages.
                        </p>
                    </div>
                )}

                {/* Error Display */}
                {error && (
                    <div className="mb-8 animate-slide-up">
                        <div className="card bg-red-50 border-2 border-red-200">
                            <div className="flex items-start gap-3">
                                <AlertCircle className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" />
                                <div className="flex-1">
                                    <h3 className="font-semibold text-red-800 mb-1">Error Processing File</h3>
                                    <p className="text-red-700 text-sm">{error}</p>
                                </div>
                                <button
                                    onClick={handleReset}
                                    className="text-red-600 hover:text-red-800 transition-colors"
                                >
                                    <RefreshCw className="w-5 h-5" />
                                </button>
                            </div>
                        </div>
                    </div>
                )}

                {/* Upload Area */}
                {!result && !isProcessing && (
                    <UploadArea onFileSelect={handleFileSelect} isProcessing={isProcessing} />
                )}

                {/* Loading State */}
                {isProcessing && (
                    <div className="card">
                        <LoadingSpinner message="Extracting text from your document..." />
                    </div>
                )}

                {/* Results */}
                {result && !isProcessing && (
                    <div>
                        <div className="flex items-center justify-between mb-6">
                            <div>
                                <h2 className="text-2xl font-bold text-neutral-800">Extraction Complete</h2>
                                <p className="text-neutral-600">Your text has been successfully extracted</p>
                            </div>
                            <button
                                onClick={handleReset}
                                className="btn btn-secondary flex items-center gap-2"
                            >
                                <RefreshCw className="w-4 h-4" />
                                Process Another
                            </button>
                        </div>
                        <ResultsPanel result={result} />
                    </div>
                )}

                {/* Features Section */}
                {!result && !isProcessing && (
                    <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-6 animate-fade-in">
                        <div className="text-center p-6">
                            <div className="inline-flex items-center justify-center w-12 h-12 bg-primary-100 text-primary-600 rounded-full mb-4">
                                <Sparkles className="w-6 h-6" />
                            </div>
                            <h3 className="font-semibold text-neutral-800 mb-2">High Accuracy</h3>
                            <p className="text-sm text-neutral-600">
                                Advanced preprocessing and OCR algorithms ensure maximum text extraction accuracy
                            </p>
                        </div>

                        <div className="text-center p-6">
                            <div className="inline-flex items-center justify-center w-12 h-12 bg-green-100 text-green-600 rounded-full mb-4">
                                <Scan className="w-6 h-6" />
                            </div>
                            <h3 className="font-semibold text-neutral-800 mb-2">Multiple Formats</h3>
                            <p className="text-sm text-neutral-600">
                                Support for PNG, JPG, JPEG, and PDF files up to 10MB in size
                            </p>
                        </div>

                        <div className="text-center p-6">
                            <div className="inline-flex items-center justify-center w-12 h-12 bg-purple-100 text-purple-600 rounded-full mb-4">
                                <RefreshCw className="w-6 h-6" />
                            </div>
                            <h3 className="font-semibold text-neutral-800 mb-2">Instant Processing</h3>
                            <p className="text-sm text-neutral-600">
                                Fast OCR processing with real-time results and confidence metrics
                            </p>
                        </div>
                    </div>
                )}
            </main>

            {/* Footer */}
            <footer className="border-t border-neutral-200 bg-white mt-20">
                <div className="max-w-6xl mx-auto px-6 py-8">
                    <div className="text-center text-neutral-600 text-sm">
                        <p>Built with FastAPI, React, and Tesseract OCR</p>
                        <p className="mt-1 text-neutral-400">© 2026 OCR Web Application. All rights reserved.</p>
                    </div>
                </div>
            </footer>
        </div>
    );
}

export default App;
