"""
Job matching service using machine learning
"""

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Any, Tuple
import logging

from app.models.job import JobDetail
from app.core.config import settings

logger = logging.getLogger(__name__)


class JobMatchingService:
    """
    Service for matching resumes to job listings using ML algorithms
    """
    
    def __init__(self):
        self.similarity_threshold = settings.SIMILARITY_THRESHOLD
        self.max_jobs = settings.MAX_MATCHED_JOBS
        self.max_features = 1000
        self.vectorizer = None
    
    def calculate_job_similarity(self, resume_text: str, job_descriptions: List[str]) -> List[float]:
        """
        Calculate similarity between resume and job descriptions using TF-IDF and cosine similarity
        
        Args:
            resume_text: The resume text
            job_descriptions: List of job descriptions
            
        Returns:
            List of similarity scores (0-1) for each job
        """
        try:
            if not job_descriptions:
                return []
            
            # Combine resume text with job descriptions
            documents = [resume_text] + job_descriptions
            
            # Create TF-IDF vectors
            self.vectorizer = TfidfVectorizer(
                max_features=self.max_features,
                stop_words='english',
                ngram_range=(1, 2),  # Use unigrams and bigrams
                lowercase=True,
                min_df=1,  # Minimum document frequency
                max_df=0.95,  # Maximum document frequency
                sublinear_tf=True  # Apply sublinear tf scaling
            )
            
            tfidf_matrix = self.vectorizer.fit_transform(documents)
            
            # Calculate cosine similarity between resume (first document) and each job
            resume_vector = tfidf_matrix[0:1]
            job_vectors = tfidf_matrix[1:]
            
            similarities = cosine_similarity(resume_vector, job_vectors)[0]
            
            # Ensure similarities are in valid range
            similarities = np.clip(similarities, 0, 1)
            
            return similarities.tolist()
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {str(e)}")
            return [0.0] * len(job_descriptions)
    
    def match_jobs_to_resume(
        self, 
        resume_text: str, 
        jobs: List[Dict[str, Any]], 
        extracted_skills: List[str] = None
    ) -> List[JobDetail]:
        """
        Match jobs to resume and return ranked results
        
        Args:
            resume_text: The resume text
            jobs: List of job dictionaries
            extracted_skills: Optional list of extracted skills for bonus scoring
            
        Returns:
            List of JobDetail objects sorted by similarity score
        """
        if not jobs:
            return []
        
        try:
            # Extract job descriptions
            job_descriptions = [job.get('description', '') for job in jobs]
            
            # Calculate base similarity scores
            similarity_scores = self.calculate_job_similarity(resume_text, job_descriptions)
            
            # Apply skill-based bonus scoring if skills are provided
            if extracted_skills:
                similarity_scores = self._apply_skill_bonus(
                    similarity_scores, jobs, extracted_skills
                )
            
            # Create JobDetail objects with similarity scores
            matched_jobs = []
            
            for i, job in enumerate(jobs):
                similarity_score = similarity_scores[i] if i < len(similarity_scores) else 0.0
                
                # Only include jobs above threshold
                if similarity_score >= self.similarity_threshold:
                    try:
                        job_detail = JobDetail(
                            title=job.get('title', 'Unknown Title'),
                            company=job.get('company', 'Unknown Company'),
                            location=job.get('location', 'Unknown Location'),
                            description=self._truncate_description(job.get('description', '')),
                            url=job.get('url', ''),
                            similarity_score=similarity_score,
                            posted_date=job.get('posted_date'),
                            salary_range=job.get('salary_range'),
                            job_type=job.get('job_type'),
                            remote_allowed=job.get('remote_allowed')
                        )
                        matched_jobs.append(job_detail)
                    except Exception as e:
                        logger.warning(f"Error creating JobDetail for job {i}: {e}")
                        continue
            
            # Sort by similarity score (highest first)
            matched_jobs.sort(key=lambda x: x.similarity_score, reverse=True)
            
            # Limit to maximum number of matches
            return matched_jobs[:self.max_jobs]
            
        except Exception as e:
            logger.error(f"Error in match_jobs_to_resume: {str(e)}")
            return []
    
    def _apply_skill_bonus(
        self, 
        similarity_scores: List[float], 
        jobs: List[Dict[str, Any]], 
        extracted_skills: List[str]
    ) -> List[float]:
        """
        Apply bonus scoring based on skill matches
        
        Args:
            similarity_scores: Base similarity scores
            jobs: List of job dictionaries
            extracted_skills: List of extracted skills from resume
            
        Returns:
            Updated similarity scores with skill bonuses
        """
        if not extracted_skills:
            return similarity_scores
        
        skills_lower = [skill.lower() for skill in extracted_skills]
        updated_scores = similarity_scores.copy()
        
        for i, job in enumerate(jobs):
            if i >= len(updated_scores):
                break
            
            job_text = (
                job.get('title', '') + ' ' + 
                job.get('description', '') + ' ' + 
                job.get('company', '')
            ).lower()
            
            # Count skill matches
            skill_matches = sum(1 for skill in skills_lower if skill in job_text)
            
            if skill_matches > 0:
                # Apply bonus: 5% per matching skill, max 25% bonus
                bonus = min(skill_matches * 0.05, 0.25)
                updated_scores[i] = min(updated_scores[i] + bonus, 1.0)
        
        return updated_scores
    
    def _truncate_description(self, description: str, max_length: int = 500) -> str:
        """
        Truncate job description to specified length
        
        Args:
            description: Job description text
            max_length: Maximum length
            
        Returns:
            Truncated description
        """
        if len(description) <= max_length:
            return description
        
        # Try to truncate at sentence boundary
        truncated = description[:max_length]
        last_period = truncated.rfind('.')
        last_space = truncated.rfind(' ')
        
        if last_period > max_length - 100:  # If period is reasonably close to end
            return description[:last_period + 1]
        elif last_space > max_length - 50:  # If space is reasonably close to end
            return description[:last_space] + "..."
        else:
            return description[:max_length - 3] + "..."
    
    def get_feature_importance(self, resume_text: str, job_description: str) -> Dict[str, float]:
        """
        Get feature importance for a specific job match
        
        Args:
            resume_text: Resume text
            job_description: Job description
            
        Returns:
            Dictionary of important features and their weights
        """
        try:
            if not self.vectorizer:
                # Create vectorizer if not already created
                documents = [resume_text, job_description]
                self.vectorizer = TfidfVectorizer(
                    max_features=self.max_features,
                    stop_words='english',
                    ngram_range=(1, 2),
                    lowercase=True
                )
                self.vectorizer.fit(documents)
            
            # Get feature names
            feature_names = self.vectorizer.get_feature_names_out()
            
            # Transform texts
            resume_vector = self.vectorizer.transform([resume_text])
            job_vector = self.vectorizer.transform([job_description])
            
            # Get non-zero features for both texts
            resume_features = resume_vector.toarray()[0]
            job_features = job_vector.toarray()[0]
            
            # Calculate feature importance based on presence in both texts
            feature_importance = {}
            
            for i, feature_name in enumerate(feature_names):
                if resume_features[i] > 0 and job_features[i] > 0:
                    # Feature appears in both texts
                    importance = min(resume_features[i], job_features[i])
                    feature_importance[feature_name] = float(importance)
            
            # Sort by importance and return top features
            sorted_features = dict(
                sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:20]
            )
            
            return sorted_features
            
        except Exception as e:
            logger.error(f"Error calculating feature importance: {str(e)}")
            return {}