"""
Natural Language Processing service
"""

import re
import spacy
from typing import List, Dict, Set
import logging

from app.models.resume import ExtractedSkills
from app.core.config import settings

logger = logging.getLogger(__name__)


class NLPService:
    """
    Service for NLP operations including skill extraction
    """
    
    def __init__(self):
        self.nlp = self._load_spacy_model()
        self.technical_skills = self._get_technical_skills()
        self.job_title_patterns = self._get_job_title_patterns()
        self.soft_skills = self._get_soft_skills()
    
    def _load_spacy_model(self):
        """Load spacy model"""
        try:
            nlp = spacy.load(settings.SPACY_MODEL)
            logger.info(f"Loaded spacy model: {settings.SPACY_MODEL}")
            return nlp
        except OSError:
            logger.error(f"Spacy model '{settings.SPACY_MODEL}' not found. "
                        f"Please install it using: python -m spacy download {settings.SPACY_MODEL}")
            return None
    
    def _get_technical_skills(self) -> Set[str]:
        """Get set of technical skills to search for"""
        return {
            # Programming Languages
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust',
            'swift', 'kotlin', 'scala', 'r', 'matlab', 'perl', 'shell', 'bash', 'powershell',
            
            # Frontend Technologies
            'react', 'angular', 'vue', 'vue.js', 'svelte', 'ember', 'backbone', 'jquery',
            'html', 'html5', 'css', 'css3', 'sass', 'scss', 'less', 'bootstrap', 'tailwind',
            'material-ui', 'chakra-ui', 'webpack', 'vite', 'parcel',
            
            # Backend Technologies
            'node.js', 'express', 'express.js', 'django', 'flask', 'fastapi', 'spring', 'spring boot',
            'hibernate', 'laravel', 'symfony', 'rails', 'ruby on rails', 'asp.net', '.net core',
            
            # Databases
            'sql', 'mysql', 'postgresql', 'sqlite', 'mongodb', 'redis', 'elasticsearch',
            'cassandra', 'dynamodb', 'neo4j', 'oracle', 'sql server', 'mariadb',
            
            # Cloud Platforms
            'aws', 'amazon web services', 'azure', 'microsoft azure', 'gcp', 'google cloud',
            'google cloud platform', 'heroku', 'digitalocean', 'linode', 'vultr',
            
            # DevOps & Tools
            'docker', 'kubernetes', 'jenkins', 'gitlab ci', 'github actions', 'circleci',
            'travis ci', 'ansible', 'terraform', 'vagrant', 'git', 'svn', 'mercurial',
            
            # Machine Learning & Data Science
            'machine learning', 'deep learning', 'artificial intelligence', 'ai', 'ml',
            'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'pandas', 'numpy', 'matplotlib',
            'seaborn', 'plotly', 'jupyter', 'anaconda', 'spark', 'hadoop', 'kafka',
            
            # Mobile Development
            'ios', 'android', 'react native', 'flutter', 'xamarin', 'ionic', 'cordova',
            
            # Other Technologies
            'rest api', 'restful', 'graphql', 'grpc', 'microservices', 'serverless',
            'blockchain', 'ethereum', 'solidity', 'web3', 'api', 'json', 'xml', 'yaml',
            'oauth', 'jwt', 'ssl', 'tls', 'https', 'websockets', 'tcp/ip', 'http'
        }
    
    def _get_soft_skills(self) -> Set[str]:
        """Get set of soft skills to search for"""
        return {
            'leadership', 'teamwork', 'communication', 'problem solving', 'analytical thinking',
            'critical thinking', 'creativity', 'adaptability', 'time management', 'project management',
            'collaboration', 'mentoring', 'coaching', 'presentation', 'public speaking',
            'negotiation', 'conflict resolution', 'decision making', 'strategic thinking'
        }
    
    def _get_job_title_patterns(self) -> List[str]:
        """Get regex patterns for job titles"""
        return [
            r'software engineer', r'software developer', r'full stack developer', r'fullstack developer',
            r'frontend developer', r'front-end developer', r'backend developer', r'back-end developer',
            r'web developer', r'mobile developer', r'ios developer', r'android developer',
            r'data scientist', r'data analyst', r'data engineer', r'machine learning engineer',
            r'ai engineer', r'devops engineer', r'site reliability engineer', r'sre',
            r'system administrator', r'network administrator', r'database administrator',
            r'product manager', r'project manager', r'technical lead', r'team lead',
            r'senior developer', r'junior developer', r'principal engineer', r'staff engineer',
            r'architect', r'solution architect', r'technical architect', r'cloud architect',
            r'security engineer', r'cybersecurity analyst', r'qa engineer', r'test engineer',
            r'ui/ux designer', r'ux designer', r'ui designer', r'product designer'
        ]
    
    def extract_skills_and_titles(self, text: str) -> ExtractedSkills:
        """
        Extract skills and job titles from resume text using NLP
        
        Args:
            text: Resume text to analyze
            
        Returns:
            ExtractedSkills object with categorized skills and information
        """
        if not self.nlp:
            raise RuntimeError("Spacy model not loaded")
        
        text_lower = text.lower()
        
        # Extract technical skills
        technical_skills = self._extract_technical_skills(text_lower)
        
        # Extract soft skills
        soft_skills = self._extract_soft_skills(text_lower)
        
        # Extract job titles
        job_titles = self._extract_job_titles(text_lower)
        
        # Extract years of experience
        experience_years = self._extract_experience_years(text_lower)
        
        # Extract education level
        education_level = self._extract_education_level(text_lower)
        
        # Use NLP to find additional skills from entities
        additional_skills = self._extract_entity_skills(text)
        technical_skills.update(additional_skills)
        
        # Categorize technical skills
        programming_languages, frameworks, tools = self._categorize_technical_skills(technical_skills)
        
        return ExtractedSkills(
            technical_skills=list(technical_skills)[:settings.MAX_SKILLS_EXTRACT],
            soft_skills=list(soft_skills)[:10],
            programming_languages=programming_languages,
            frameworks=frameworks,
            tools=tools,
            job_titles=job_titles[:settings.MAX_JOB_TITLES_EXTRACT],
            experience_years=experience_years,
            education_level=education_level
        )
    
    def _extract_technical_skills(self, text_lower: str) -> Set[str]:
        """Extract technical skills from text"""
        found_skills = set()
        for skill in self.technical_skills:
            if skill in text_lower:
                found_skills.add(skill)
        return found_skills
    
    def _extract_soft_skills(self, text_lower: str) -> Set[str]:
        """Extract soft skills from text"""
        found_skills = set()
        for skill in self.soft_skills:
            if skill in text_lower:
                found_skills.add(skill)
        return found_skills
    
    def _extract_job_titles(self, text_lower: str) -> List[str]:
        """Extract job titles using regex patterns"""
        found_titles = []
        for pattern in self.job_title_patterns:
            matches = re.findall(pattern, text_lower)
            found_titles.extend(matches)
        return list(set(found_titles))
    
    def _extract_experience_years(self, text_lower: str) -> int:
        """Extract years of experience using regex"""
        patterns = [
            r'(\d+)\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp)',
            r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:in|with|of)',
            r'(?:experience|exp).*?(\d+)\s*(?:years?|yrs?)',
        ]
        
        all_matches = []
        for pattern in patterns:
            matches = re.findall(pattern, text_lower)
            all_matches.extend([int(match) for match in matches])
        
        return max(all_matches) if all_matches else None
    
    def _extract_education_level(self, text_lower: str) -> str:
        """Extract education level"""
        education_patterns = {
            'phd': r'(?:phd|ph\.d|doctorate|doctoral)',
            'masters': r'(?:masters?|master\'s|m\.s|m\.a|mba|m\.eng)',
            'bachelors': r'(?:bachelors?|bachelor\'s|b\.s|b\.a|b\.eng|b\.tech)',
            'associates': r'(?:associates?|associate\'s|a\.s|a\.a)',
            'high_school': r'(?:high school|secondary school|diploma)'
        }
        
        for level, pattern in education_patterns.items():
            if re.search(pattern, text_lower):
                return level
        
        return None
    
    def _extract_entity_skills(self, text: str) -> Set[str]:
        """Extract additional skills using NLP entity recognition"""
        doc = self.nlp(text)
        additional_skills = set()
        
        for ent in doc.ents:
            if ent.label_ in ['ORG', 'PRODUCT', 'LANGUAGE'] and len(ent.text) > 2:
                skill_candidate = ent.text.lower().strip()
                # Filter out common non-skill entities
                if (any(char.isalpha() for char in skill_candidate) and 
                    skill_candidate not in {'university', 'college', 'company', 'inc', 'llc', 'corp'}):
                    additional_skills.add(skill_candidate)
        
        return additional_skills
    
    def _categorize_technical_skills(self, skills: Set[str]) -> tuple:
        """Categorize technical skills into programming languages, frameworks, and tools"""
        programming_languages = {
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'php', 'ruby', 
            'go', 'rust', 'swift', 'kotlin', 'scala', 'r', 'matlab'
        }
        
        frameworks = {
            'react', 'angular', 'vue', 'django', 'flask', 'fastapi', 'spring', 
            'express', 'laravel', 'rails', 'bootstrap', 'tailwind'
        }
        
        languages = [skill for skill in skills if skill in programming_languages]
        frameworks_found = [skill for skill in skills if skill in frameworks]
        tools = [skill for skill in skills if skill not in programming_languages and skill not in frameworks]
        
        return languages[:10], frameworks_found[:10], tools[:15]