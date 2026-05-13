export interface Candidate {
  id: number
  name: string
  matchScore: number
  keySkills: string[]
  location: string
  experience: string
  email: string
  phone: string
  address: string
  education: string
  linkedin: string
  cvUrl: string
  skills: Array<{
    name: string
    years: number
  }>
  workExperience: Array<{
    company: string
    position: string
    duration: string
    description: string
  }>
  aiAnalysis: string
}

// Mock data for candidates
const mockCandidates: Candidate[] = [
  {
    id: 1,
    name: "Sarah Johnson",
    matchScore: 95,
    keySkills: ["React", "TypeScript", "Tailwind CSS", "Next.js"],
    location: "San Francisco, CA",
    experience: "6 years",
    email: "sarah.johnson@email.com",
    phone: "+1 (555) 123-4567",
    address: "123 Main St, San Francisco, CA 94102",
    education: "BS Computer Science, Stanford University",
    linkedin: "https://linkedin.com/in/sarahjohnson",
    cvUrl: "/cvs/sarah-johnson.pdf",
    skills: [
      { name: "React", years: 5 },
      { name: "TypeScript", years: 4 },
      { name: "JavaScript", years: 6 },
      { name: "Next.js", years: 3 },
      { name: "Tailwind CSS", years: 4 },
      { name: "Node.js", years: 3 }
    ],
    workExperience: [
      {
        company: "TechCorp Inc.",
        position: "Senior Frontend Developer",
        duration: "2021 - Present",
        description: "Led development of multiple React applications, mentored junior developers, and implemented best practices for code quality."
      },
      {
        company: "StartupXYZ",
        position: "Frontend Developer",
        duration: "2019 - 2021",
        description: "Built responsive web applications using React and TypeScript, collaborated with design and backend teams."
      },
      {
        company: "WebSolutions",
        position: "Junior Developer",
        duration: "2018 - 2019",
        description: "Developed and maintained client websites, worked with HTML, CSS, and JavaScript."
      }
    ],
    aiAnalysis: "Sarah shows exceptional React and TypeScript skills with 5+ years of experience. Her portfolio demonstrates modern development practices and she has strong leadership experience. Perfect match for senior frontend role."
  },
  {
    id: 2,
    name: "Michael Chen",
    matchScore: 88,
    keySkills: ["React", "JavaScript", "CSS", "Vue.js"],
    location: "Oakland, CA",
    experience: "4 years",
    email: "michael.chen@email.com",
    phone: "+1 (555) 234-5678",
    address: "456 Oak Ave, Oakland, CA 94611",
    education: "BS Software Engineering, UC Berkeley",
    linkedin: "https://linkedin.com/in/michaelchen",
    cvUrl: "/cvs/michael-chen.pdf",
    skills: [
      { name: "React", years: 3 },
      { name: "JavaScript", years: 4 },
      { name: "Vue.js", years: 2 },
      { name: "CSS", years: 4 },
      { name: "HTML", years: 4 },
      { name: "Git", years: 3 }
    ],
    workExperience: [
      {
        company: "DesignStudio",
        position: "Frontend Developer",
        duration: "2020 - Present",
        description: "Developed user interfaces for web applications, collaborated with designers and backend developers."
      },
      {
        company: "CreativeWeb",
        position: "Web Developer",
        duration: "2019 - 2020",
        description: "Built responsive websites and e-commerce platforms using modern web technologies."
      }
    ],
    aiAnalysis: "Michael has solid frontend development skills with good React experience. Shows versatility with Vue.js knowledge. Good problem-solving abilities and clean code practices."
  },
  {
    id: 3,
    name: "Emily Rodriguez",
    matchScore: 92,
    keySkills: ["React", "TypeScript", "GraphQL", "Testing"],
    location: "San Jose, CA",
    experience: "5 years",
    email: "emily.rodriguez@email.com",
    phone: "+1 (555) 345-6789",
    address: "789 Tech Blvd, San Jose, CA 95112",
    education: "MS Computer Science, San Jose State University",
    linkedin: "https://linkedin.com/in/emilyrodriguez",
    cvUrl: "/cvs/emily-rodriguez.pdf",
    skills: [
      { name: "React", years: 4 },
      { name: "TypeScript", years: 4 },
      { name: "GraphQL", years: 3 },
      { name: "Jest", years: 4 },
      { name: "Testing Library", years: 3 },
      { name: "Node.js", years: 3 }
    ],
    workExperience: [
      {
        company: "CloudTech",
        position: "Senior Frontend Developer",
        duration: "2021 - Present",
        description: "Led testing initiatives and implemented comprehensive test suites. Mentored team on TypeScript best practices."
      },
      {
        company: "DataFlow",
        position: "Frontend Developer",
        duration: "2019 - 2021",
        description: "Developed data visualization dashboards and implemented GraphQL APIs for frontend consumption."
      },
      {
        company: "WebApps Inc.",
        position: "Junior Developer",
        duration: "2018 - 2019",
        description: "Built and tested React components, participated in code reviews and agile development processes."
      }
    ],
    aiAnalysis: "Emily demonstrates excellent TypeScript skills and strong testing practices. Her attention to detail and code quality focus make her an ideal candidate for quality-focused teams."
  },
  {
    id: 4,
    name: "David Kim",
    matchScore: 85,
    keySkills: ["React", "JavaScript", "Node.js", "MongoDB"],
    location: "Berkeley, CA",
    experience: "3 years",
    email: "david.kim@email.com",
    phone: "+1 (555) 456-7890",
    address: "321 University Ave, Berkeley, CA 94704",
    education: "BS Computer Science, UC Berkeley",
    linkedin: "https://linkedin.com/in/davidkim",
    cvUrl: "/cvs/david-kim.pdf",
    skills: [
      { name: "React", years: 2 },
      { name: "JavaScript", years: 3 },
      { name: "Node.js", years: 3 },
      { name: "MongoDB", years: 2 },
      { name: "Express.js", years: 2 },
      { name: "Git", years: 3 }
    ],
    workExperience: [
      {
        company: "FullStack Solutions",
        position: "Full Stack Developer",
        duration: "2020 - Present",
        description: "Developed full-stack applications using React frontend and Node.js backend with MongoDB database."
      },
      {
        company: "StartupHub",
        position: "Junior Developer",
        duration: "2019 - 2020",
        description: "Built web applications and APIs, worked in agile development environment."
      }
    ],
    aiAnalysis: "David is a full-stack developer with good React skills and valuable backend experience. His MongoDB knowledge could be beneficial for full-stack projects."
  },
  {
    id: 5,
    name: "Lisa Wang",
    matchScore: 90,
    keySkills: ["React", "TypeScript", "Redux", "Jest"],
    location: "Palo Alto, CA",
    experience: "7 years",
    email: "lisa.wang@email.com",
    phone: "+1 (555) 567-8901",
    address: "654 Innovation Dr, Palo Alto, CA 94301",
    education: "MS Computer Science, Stanford University",
    linkedin: "https://linkedin.com/in/lisawang",
    cvUrl: "/cvs/lisa-wang.pdf",
    skills: [
      { name: "React", years: 6 },
      { name: "TypeScript", years: 5 },
      { name: "Redux", years: 5 },
      { name: "Jest", years: 5 },
      { name: "Next.js", years: 4 },
      { name: "Leadership", years: 3 }
    ],
    workExperience: [
      {
        company: "TechCorp Inc.",
        position: "Lead Frontend Developer",
        duration: "2020 - Present",
        description: "Led a team of 8 developers, established coding standards, and mentored junior developers. Implemented CI/CD pipelines."
      },
      {
        company: "Innovation Labs",
        position: "Senior Frontend Developer",
        duration: "2017 - 2020",
        description: "Developed complex React applications, implemented state management solutions, and conducted technical interviews."
      },
      {
        company: "WebSolutions",
        position: "Frontend Developer",
        duration: "2016 - 2017",
        description: "Built responsive web applications and collaborated with cross-functional teams."
      }
    ],
    aiAnalysis: "Lisa is a senior developer with extensive React experience and strong leadership skills. Her mentoring experience and technical depth make her perfect for senior roles."
  }
]

export function getMatchedCandidates(): Candidate[] {
  // In a real application, this would fetch candidates based on position requirements
  return mockCandidates.sort((a, b) => b.matchScore - a.matchScore)
} 