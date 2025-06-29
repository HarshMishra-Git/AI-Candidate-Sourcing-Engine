import axios from 'axios';
import { Candidate } from './types';

const BASE_URL = 'http://localhost:5000';

export async function fetchCandidates(jobDescription: string): Promise<Candidate[]> {
  const res = await axios.post(`${BASE_URL}/huggingface`, {
    job_description: jobDescription,
    top_candidates: 10,
    use_cache: true
  });
  // Map backend response to frontend Candidate type
  return (res.data.top_candidates || []).map((c: any, idx: number) => ({
    id: idx.toString(),
    name: c.name || '',
    title: c.headline || '',
    linkedinUrl: c.linkedin_url || c.url || '',
    fitScore: c.fit_score || 0,
    scoreBreakdown: c.score_breakdown || {},
    outreachMessage: c.outreach_message || c.message || '',
    avatar: `https://api.dicebear.com/7.x/identicon/svg?seed=${encodeURIComponent(c.name || 'candidate')}`
  }));
} 