import React, { useState } from 'react';
import { ArrowLeft, Filter, SortAsc } from 'lucide-react';
import { Candidate } from '../types';
import CandidateCard from './CandidateCard';

interface ResultsDisplayProps {
  candidates: Candidate[];
  isLoading: boolean;
  onBackToForm: () => void;
}

const ResultsDisplay: React.FC<ResultsDisplayProps> = ({ candidates, isLoading, onBackToForm }) => {
  const [sortBy, setSortBy] = useState<'score' | 'name'>('score');
  const [filterMinScore, setFilterMinScore] = useState(0);

  const filteredAndSortedCandidates = candidates
    .filter(candidate => candidate.fitScore >= filterMinScore)
    .sort((a, b) => {
      if (sortBy === 'score') {
        return b.fitScore - a.fitScore;
      }
      return a.name.localeCompare(b.name);
    });

  if (isLoading) {
    return (
      <section id="results-section" className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mx-auto mb-6"></div>
            <h2 className="text-3xl font-bold text-gray-900 font-inter mb-4">
              Sourcing Candidates...
            </h2>
            <p className="text-lg text-gray-600">
              Our AI is analyzing thousands of profiles to find your perfect matches.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="bg-white p-6 rounded-2xl shadow-sm animate-pulse">
                <div className="flex items-center mb-4">
                  <div className="w-16 h-16 bg-gray-200 rounded-full mr-4"></div>
                  <div>
                    <div className="h-4 bg-gray-200 rounded w-32 mb-2"></div>
                    <div className="h-3 bg-gray-200 rounded w-24"></div>
                  </div>
                </div>
                <div className="h-2 bg-gray-200 rounded mb-4"></div>
                <div className="space-y-2">
                  <div className="h-3 bg-gray-200 rounded"></div>
                  <div className="h-3 bg-gray-200 rounded w-3/4"></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    );
  }

  return (
    <section id="results-section" className="py-20 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col sm:flex-row items-center justify-between mb-8">
          <div>
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 font-inter mb-2">
              Found {filteredAndSortedCandidates.length} Perfect Matches
            </h2>
            <p className="text-lg text-gray-600">
              Ranked by AI fit score and ready for outreach
            </p>
          </div>
          
          <button
            onClick={onBackToForm}
            className="flex items-center px-6 py-3 bg-white text-gray-700 rounded-lg border
                     hover:bg-gray-50 transition-colors duration-200 focus:outline-none focus:ring-4 focus:ring-gray-300"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            New Search
          </button>
        </div>

        <div className="flex flex-col sm:flex-row gap-4 mb-8 p-4 bg-white rounded-lg shadow-sm">
          <div className="flex items-center space-x-2">
            <SortAsc className="h-4 w-4 text-gray-500" />
            <span className="text-sm font-medium text-gray-700">Sort by:</span>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as 'score' | 'name')}
              className="border border-gray-300 rounded px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="score">Fit Score</option>
              <option value="name">Name</option>
            </select>
          </div>
          
          <div className="flex items-center space-x-2">
            <Filter className="h-4 w-4 text-gray-500" />
            <span className="text-sm font-medium text-gray-700">Min Score:</span>
            <select
              value={filterMinScore}
              onChange={(e) => setFilterMinScore(Number(e.target.value))}
              className="border border-gray-300 rounded px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value={0}>All</option>
              <option value={70}>70+</option>
              <option value={80}>80+</option>
              <option value={90}>90+</option>
            </select>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {filteredAndSortedCandidates.map((candidate, index) => (
            <CandidateCard
              key={candidate.id}
              candidate={candidate}
              index={index}
            />
          ))}
        </div>

        {filteredAndSortedCandidates.length === 0 && (
          <div className="text-center py-12">
            <p className="text-lg text-gray-600">
              No candidates match your current filters. Try lowering the minimum score.
            </p>
          </div>
        )}
      </div>
    </section>
  );
};

export default ResultsDisplay;