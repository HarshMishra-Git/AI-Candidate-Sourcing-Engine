import React, { useState } from 'react';
import Header from './components/Header';
import HeroSection from './components/HeroSection';
import JobForm from './components/JobForm';
import ResultsDisplay from './components/ResultsDisplay';
import Footer from './components/Footer';
import { Candidate } from './types';
import { fetchCandidates } from './api';

function App() {
  const [showResults, setShowResults] = useState(false);
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleJobSubmit = async (jobDescription: string) => {
    setIsLoading(true);
    setError(null);
    setCandidates([]);
    setShowResults(false);
    try {
      const realCandidates = await fetchCandidates(jobDescription);
      setCandidates(realCandidates);
      setShowResults(true);
      setTimeout(() => {
        const resultsElement = document.getElementById('results-section');
        if (resultsElement) {
          resultsElement.scrollIntoView({ behavior: 'smooth' });
        }
      }, 100);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Something went wrong.');
    }
    setIsLoading(false);
  };

  const handleBackToForm = () => {
    setShowResults(false);
    setCandidates([]);
    setError(null);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <Header />
      <main>
        <HeroSection />
        <JobForm 
          onSubmit={handleJobSubmit} 
          isLoading={isLoading}
          showResults={showResults}
        />
        {(showResults || isLoading) && (
          <ResultsDisplay 
            candidates={candidates}
            isLoading={isLoading}
            onBackToForm={handleBackToForm}
          />
        )}
        {error && (
          <div className="max-w-2xl mx-auto mt-8 p-4 bg-red-100 text-red-700 rounded-lg text-center">
            <strong>Error:</strong> {error}
          </div>
        )}
      </main>
      <Footer />
    </div>
  );
}

export default App;