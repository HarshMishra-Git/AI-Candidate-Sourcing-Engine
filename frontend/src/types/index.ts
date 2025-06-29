export interface Candidate {
  id: string;
  name: string;
  title: string;
  linkedinUrl: string;
  fitScore: number;
  scoreBreakdown: {
    skills: number;
    experience: number;
    education: number;
    culture: number;
  };
  outreachMessage: string;
  avatar: string;
}

export interface JobFormData {
  description: string;
}