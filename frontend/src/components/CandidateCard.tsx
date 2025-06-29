import React, { useState, useEffect } from 'react';
import { Linkedin, Copy, Check, ChevronDown, ChevronUp, Star } from 'lucide-react';
import { Candidate } from '../types';

interface CandidateCardProps {
  candidate: Candidate;
  index: number;
}

const CandidateCard: React.FC<CandidateCardProps> = ({ candidate, index }) => {
  const [showBreakdown, setShowBreakdown] = useState(false);
  const [copied, setCopied] = useState(false);
  const [scoreAnimated, setScoreAnimated] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      setScoreAnimated(true);
    }, index * 200);

    return () => clearTimeout(timer);
  }, [index]);

  const handleCopyMessage = async () => {
    try {
      await navigator.clipboard.writeText(candidate.outreachMessage);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-600 bg-green-100';
    if (score >= 80) return 'text-blue-600 bg-blue-100';
    if (score >= 70) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getScoreBarColor = (score: number) => {
    if (score >= 90) return 'bg-green-500';
    if (score >= 80) return 'bg-blue-500';
    if (score >= 70) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const fitScoreDisplay = Math.round((candidate.fitScore * 10) * 100) / 100;
  const scoreBreakdownDisplay = Object.fromEntries(
    Object.entries(candidate.scoreBreakdown).map(([k, v]) => [k, Math.round((v * 10) * 100) / 100])
  );

  return (
    <div className="bg-white rounded-2xl shadow-sm hover:shadow-lg transition-all duration-300 p-6 
                    transform hover:-translate-y-1 border border-gray-100">
      <div className="flex items-start space-x-4 mb-6">
        <div className="relative">
          <img
            src={candidate.avatar}
            alt={candidate.name}
            className="w-16 h-16 rounded-full object-cover shadow-md"
          />
          <div className="absolute -top-1 -right-1">
            <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold
                          ${getScoreColor(fitScoreDisplay)}`}>
              <Star className="h-3 w-3" />
            </div>
          </div>
        </div>
        
        <div className="flex-1">
          <h3 className="text-xl font-bold text-gray-900 font-inter mb-1">
            {candidate.name}
          </h3>
          <p className="text-gray-600 mb-2">{candidate.title}</p>
          <a
            href={candidate.linkedinUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center text-blue-600 hover:text-blue-700 
                     transition-colors duration-200 text-sm font-medium"
          >
            <Linkedin className="h-4 w-4 mr-1" />
            View Profile
          </a>
        </div>
      </div>

      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">Fit Score</span>
          <span className={`text-2xl font-bold ${getScoreColor(fitScoreDisplay).split(' ')[0]}`}>
            {fitScoreDisplay}%
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
          <div
            className={`h-full transition-all duration-1000 ease-out ${getScoreBarColor(fitScoreDisplay)}`}
            style={{ width: scoreAnimated ? `${fitScoreDisplay}%` : '0%' }}
          ></div>
        </div>
      </div>

      <button
        onClick={() => setShowBreakdown(!showBreakdown)}
        className="w-full flex items-center justify-between p-3 bg-gray-50 rounded-lg 
                 hover:bg-gray-100 transition-colors duration-200 mb-4"
      >
        <span className="text-sm font-medium text-gray-700">Score Breakdown</span>
        {showBreakdown ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
      </button>

      {showBreakdown && (
        <div className="mb-6 space-y-3 animate-slide-down">
          {Object.entries(scoreBreakdownDisplay).map(([category, score]) => (
            <div key={category} className="flex items-center justify-between">
              <span className="text-sm text-gray-600 capitalize">{category}</span>
              <div className="flex items-center space-x-2">
                <div className="w-20 bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${getScoreBarColor(score)}`}
                    style={{ width: `${score}%` }}
                  ></div>
                </div>
                <span className="text-sm font-medium text-gray-700 w-8">{score}%</span>
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="mb-6">
        <h4 className="text-sm font-semibold text-gray-700 mb-3">Outreach Message</h4>
        <div className="bg-gray-50 rounded-lg p-4 border-l-4 border-blue-500">
          <pre className="text-sm text-gray-700 whitespace-pre-wrap font-open-sans leading-relaxed">
            {candidate.outreachMessage}
          </pre>
        </div>
      </div>

      <button
        onClick={handleCopyMessage}
        className={`w-full flex items-center justify-center px-4 py-3 rounded-lg font-medium
                  transition-all duration-300 focus:outline-none focus:ring-4 focus:ring-blue-300
                  ${copied 
                    ? 'bg-green-600 text-white' 
                    : 'bg-blue-600 text-white hover:bg-blue-700 hover:scale-105'
                  }`}
      >
        {copied ? (
          <>
            <Check className="h-4 w-4 mr-2" />
            Copied!
          </>
        ) : (
          <>
            <Copy className="h-4 w-4 mr-2" />
            Copy Message
          </>
        )}
      </button>
    </div>
  );
};

export default CandidateCard;