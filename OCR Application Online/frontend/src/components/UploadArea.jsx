import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, X, Image as ImageIcon } from 'lucide-react';

const UploadArea = ({ onFileSelect, isProcessing }) => {
    const [preview, setPreview] = useState(null);
    const [selectedFile, setSelectedFile] = useState(null);

    const onDrop = useCallback((acceptedFiles) => {
        if (acceptedFiles.length > 0) {
            const file = acceptedFiles[0];
            setSelectedFile(file);

            // Create preview for images
            if (file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    setPreview(e.target.result);
                };
                reader.readAsDataURL(file);
            } else {
                setPreview(null);
            }
        }
    }, []);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            'image/png': ['.png'],
            'image/jpeg': ['.jpg', '.jpeg'],
            'application/pdf': ['.pdf']
        },
        maxSize: 10485760, // 10MB
        multiple: false,
        disabled: isProcessing
    });

    const handleUpload = () => {
        if (selectedFile) {
            onFileSelect(selectedFile);
        }
    };

    const handleClear = () => {
        setSelectedFile(null);
        setPreview(null);
    };

    return (
        <div className="w-full animate-slide-up">
            {/* Upload Zone */}
            <div
                {...getRootProps()}
                className={`
          relative border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer
          transition-all duration-300 ease-out
          ${isDragActive
                        ? 'border-primary-500 bg-primary-50 scale-[1.02]'
                        : 'border-neutral-300 bg-white hover:border-primary-400 hover:bg-neutral-50'
                    }
          ${isProcessing ? 'opacity-50 cursor-not-allowed' : ''}
          ${selectedFile ? 'border-primary-400 bg-primary-50/30' : ''}
        `}
            >
                <input {...getInputProps()} />

                {!selectedFile ? (
                    <div className="flex flex-col items-center gap-4">
                        <div className="relative">
                            <div className="absolute inset-0 bg-primary-400 rounded-full blur-xl opacity-20 animate-pulse-slow"></div>
                            <div className="relative bg-gradient-to-br from-primary-500 to-primary-600 p-4 rounded-full">
                                <Upload className="w-8 h-8 text-white" />
                            </div>
                        </div>

                        <div>
                            <h3 className="text-xl font-semibold text-neutral-800 mb-2">
                                {isDragActive ? 'Drop your file here' : 'Upload Image or PDF'}
                            </h3>
                            <p className="text-neutral-500 text-sm">
                                Drag and drop or click to browse
                            </p>
                            <p className="text-neutral-400 text-xs mt-2">
                                Supports PNG, JPG, JPEG, PDF • Max 10MB
                            </p>
                        </div>
                    </div>
                ) : (
                    <div className="flex flex-col items-center gap-4">
                        {/* Preview */}
                        {preview ? (
                            <div className="relative group">
                                <img
                                    src={preview}
                                    alt="Preview"
                                    className="max-h-48 rounded-lg shadow-soft"
                                />
                                <button
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        handleClear();
                                    }}
                                    className="absolute top-2 right-2 bg-red-500 text-white p-2 rounded-full
                           opacity-0 group-hover:opacity-100 transition-opacity duration-200
                           hover:bg-red-600 focus:outline-none focus:ring-2 focus:ring-red-400"
                                >
                                    <X className="w-4 h-4" />
                                </button>
                            </div>
                        ) : (
                            <div className="flex items-center gap-3 bg-white px-6 py-4 rounded-lg shadow-sm">
                                <FileText className="w-8 h-8 text-primary-600" />
                                <div className="text-left">
                                    <p className="font-medium text-neutral-800">{selectedFile.name}</p>
                                    <p className="text-xs text-neutral-500">
                                        {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                                    </p>
                                </div>
                                <button
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        handleClear();
                                    }}
                                    className="ml-4 text-neutral-400 hover:text-red-500 transition-colors"
                                >
                                    <X className="w-5 h-5" />
                                </button>
                            </div>
                        )}

                        <p className="text-sm text-neutral-600">
                            Click to change or drag a different file
                        </p>
                    </div>
                )}
            </div>

            {/* Upload Button */}
            {selectedFile && !isProcessing && (
                <div className="mt-6 flex justify-center animate-fade-in">
                    <button
                        onClick={handleUpload}
                        className="btn btn-primary px-8 py-3 text-lg font-semibold
                     transform hover:scale-105 active:scale-95"
                    >
                        Extract Text
                    </button>
                </div>
            )}
        </div>
    );
};

export default UploadArea;
