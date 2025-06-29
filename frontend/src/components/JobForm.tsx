import React, { useState } from 'react';
import { Send, AlertCircle, Briefcase } from 'lucide-react';

interface JobFormProps {
  onSubmit: (jobDescription: string) => void;
  isLoading: boolean;
  showResults: boolean;
}

const JobForm: React.FC<JobFormProps> = ({ onSubmit, isLoading, showResults }) => {
  const [jobDescription, setJobDescription] = useState('');
  const [error, setError] = useState('');
  const [charCount, setCharCount] = useState(0);

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    setJobDescription(value);
    setCharCount(value.length);
    if (error) setError('');
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (jobDescription.trim().length < 100) {
      setError('Job description must be at least 100 characters long.');
      return;
    }
    
    if (jobDescription.trim().length > 2000) {
      setError('Job description must not exceed 2000 characters.');
      return;
    }

    onSubmit(jobDescription.trim());
  };

  if (showResults) return null;

  return (
    <section id="job-form-section" className="py-20 bg-white">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <div className="flex justify-center mb-6">
            <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center">
              <Briefcase className="h-8 w-8 text-blue-600" />
            </div>
          </div>
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 font-inter mb-4">
            Describe Your Perfect Candidate
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Provide a detailed job description including required skills, experience level, 
            and any specific qualifications. Our AI will find the best matches.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="bg-gray-50 p-8 rounded-2xl shadow-sm">
          <div className="mb-6">
            <label htmlFor="job-description" className="block text-sm font-semibold text-gray-700 mb-3">
              Job Description *
            </label>
            <div className="relative">
              <textarea
                id="job-description"
                value={jobDescription}
                onChange={handleChange}
                placeholder="Example: We are looking for a Senior React Developer with 5+ years of experience in building scalable web applications. Must have expertise in TypeScript, Node.js, and modern testing frameworks. Experience with AWS and microservices architecture is a plus..."
                className={`w-full h-48 p-4 border-2 rounded-xl resize-none transition-all duration-200 font-open-sans
                          placeholder-gray-400 focus:outline-none focus:ring-4 focus:ring-blue-300 
                          ${error ? 'border-red-300 bg-red-50' : 'border-gray-200 focus:border-blue-500'}`}
                maxLength={2000}
              />
              <div className="absolute bottom-3 right-3 text-sm text-gray-500">
                {charCount}/2000
              </div>
            </div>
            
            {error && (
              <div className="mt-3 flex items-center text-red-600 animate-shake">
                <AlertCircle className="h-4 w-4 mr-2" />
                <span className="text-sm">{error}</span>
              </div>
            )}
            
            <div className="mt-3 text-sm text-gray-500">
              Minimum 100 characters required. Be specific about required skills, experience, and qualifications.
            </div>
          </div>

          <div className="flex flex-col sm:flex-row gap-4">
            <button
              type="submit"
              disabled={isLoading || jobDescription.trim().length < 100}
              className={`flex items-center justify-center px-8 py-4 rounded-xl font-semibold text-lg
                        transition-all duration-300 focus:outline-none focus:ring-4 focus:ring-blue-300
                        ${isLoading || jobDescription.trim().length < 100
                          ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                          : 'bg-blue-600 text-white hover:bg-blue-700 hover:scale-105 shadow-lg hover:shadow-xl'
                        }`}
            >
              {isLoading ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-3"></div>
                  Analyzing & Sourcing...
                </>
              ) : (
                <>
                  <Send className="h-5 w-5 mr-3" />
                  Find Candidates
                </>
              )}
            </button>
            
            <div className="text-sm text-gray-500 flex items-center">
              <div className="w-2 h-2 bg-green-400 rounded-full mr-2 animate-pulse"></div>
              Usually takes 15-30 seconds
            </div>
          </div>
        </form>

        {isLoading && (
          <div className="mt-8 text-center">
            <div className="inline-flex items-center px-6 py-3 bg-blue-50 text-blue-700 rounded-lg">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-3"></div>
              Our AI is analyzing your requirements and searching our candidate database...
            </div>
          </div>
        )}
      </div>
    </section>
  );
};

export default JobForm;