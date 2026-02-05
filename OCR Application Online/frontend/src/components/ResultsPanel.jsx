import React, { useState } from 'react';
import { Copy, Download, CheckCircle2, FileText, TrendingUp } from 'lucide-react';

const ResultsPanel = ({ result }) => {
    const [copied, setCopied] = useState(false);

    const handleCopy = async () => {
        try {
            await navigator.clipboard.writeText(result.text);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        } catch (err) {
            console.error('Failed to copy text:', err);
        }
    };

    const handleDownload = () => {
        const blob = new Blob([result.text], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `extracted-text-${Date.now()}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    };

    const getConfidenceColor = (confidence) => {
        if (confidence >= 80) return 'text-green-600 bg-green-50';
        if (confidence >= 60) return 'text-yellow-600 bg-yellow-50';
        return 'text-orange-600 bg-orange-50';
    };

    const getConfidenceLabel = (confidence) => {
        if (confidence >= 80) return 'High Confidence';
        if (confidence >= 60) return 'Medium Confidence';
        return 'Low Confidence';
    };

    return (
        <div className="w-full animate-slide-up">
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                {/* Confidence Score */}
                <div className="card">
                    <div className="flex items-center gap-3">
                        <div className={`p-3 rounded-lg ${getConfidenceColor(result.confidence)}`}>
                            <TrendingUp className="w-5 h-5" />
                        </div>
                        <div>
                            <p className="text-sm text-neutral-500 font-medium">Confidence</p>
                            <p className="text-2xl font-bold text-neutral-800">{result.confidence}%</p>
                            <p className="text-xs text-neutral-400">{getConfidenceLabel(result.confidence)}</p>
                        </div>
                    </div>
                </div>

                {/* Word Count */}
                <div className="card">
                    <div className="flex items-center gap-3">
                        <div className="p-3 rounded-lg bg-blue-50 text-blue-600">
                            <FileText className="w-5 h-5" />
                        </div>
                        <div>
                            <p className="text-sm text-neutral-500 font-medium">Words Detected</p>
                            <p className="text-2xl font-bold text-neutral-800">{result.word_count}</p>
                            <p className="text-xs text-neutral-400">Total count</p>
                        </div>
                    </div>
                </div>

                {/* Language */}
                <div className="card">
                    <div className="flex items-center gap-3">
                        <div className="p-3 rounded-lg bg-purple-50 text-purple-600">
                            <CheckCircle2 className="w-5 h-5" />
                        </div>
                        <div>
                            <p className="text-sm text-neutral-500 font-medium">Language</p>
                            <p className="text-2xl font-bold text-neutral-800">{result.language.toUpperCase()}</p>
                            <p className="text-xs text-neutral-400">Detected</p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Extracted Text */}
            <div className="card">
                <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-neutral-800 flex items-center gap-2">
                        <FileText className="w-5 h-5 text-primary-600" />
                        Extracted Text
                    </h3>

                    <div className="flex gap-2">
                        <button
                            onClick={handleCopy}
                            className={`
                btn transition-all duration-200 flex items-center gap-2
                ${copied
                                    ? 'bg-green-500 text-white hover:bg-green-600'
                                    : 'btn-secondary'
                                }
              `}
                        >
                            {copied ? (
                                <>
                                    <CheckCircle2 className="w-4 h-4" />
                                    Copied!
                                </>
                            ) : (
                                <>
                                    <Copy className="w-4 h-4" />
                                    Copy
                                </>
                            )}
                        </button>

                        <button
                            onClick={handleDownload}
                            className="btn btn-primary flex items-center gap-2"
                        >
                            <Download className="w-4 h-4" />
                            Download
                        </button>
                    </div>
                </div>

                <div className="relative">
                    <textarea
                        readOnly
                        value={result.text}
                        className="w-full h-96 p-4 bg-neutral-50 border border-neutral-200 rounded-lg
                     font-mono text-sm text-neutral-800 resize-none
                     focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent
                     custom-scrollbar"
                        placeholder="Extracted text will appear here..."
                    />

                    {!result.text && (
                        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                            <p className="text-neutral-400">No text extracted</p>
                        </div>
                    )}
                </div>

                {result.page_count && (
                    <p className="mt-3 text-sm text-neutral-500">
                        Processed {result.page_count} page{result.page_count > 1 ? 's' : ''}
                    </p>
                )}
            </div>
        </div>
    );
};

export default ResultsPanel;
