#!/usr/bin/env python3
"""
Application Package Generator
Analyzes job descriptions and creates tailored application materials
"""

import os
import sys
import sqlite3
import shutil
import argparse
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import json

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))


class ApplicationPackageGenerator:
    """Generate complete application packages with tailored documents"""

    def __init__(self, db_path: str = None):
        """Initialize generator with database connection"""
        if db_path is None:
            db_path = Path(__file__).parent.parent.parent / 'tracking/database/job_tracker.db'

        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

        # Load configuration
        self.config = self.load_config()

    def load_config(self) -> Dict:
        """Load generator configuration"""
        config_path = Path(__file__).parent.parent.parent / 'config/generator_config.json'

        # Default configuration
        default_config = {
            'resume_templates': {
                1: 'Full comprehensive - general purpose',
                2: 'Healthcare/clinical focus',
                3: 'AI/Tech transition emphasis',
                4: 'Business analysis focus',
                5: 'General purpose - streamlined'
            },
            'cover_letter_tiers': {
                1: 'Healthcare and clinical positions',
                2: 'General business analyst roles',
                3: 'AI/Tech transition positions'
            },
            'keyword_weights': {
                'exact_match': 3,
                'stem_match': 2,
                'synonym_match': 1
            },
            'skills_categories': {
                'technical': ['Python', 'SQL', 'data analysis', 'Excel', 'Tableau', 'Power BI'],
                'healthcare': ['Epic', 'clinical', 'patient care', 'healthcare', 'medical'],
                'business': ['business analysis', 'requirements', 'stakeholder', 'project management'],
                'ai_ml': ['AI', 'machine learning', 'LLM', 'NLP', 'data science', 'artificial intelligence']
            }
        }

        if config_path.exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
            # Create default config
            config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config

    def analyze_job_description(self, job_description: str) -> Dict:
        """Analyze job description for keywords and requirements"""
        analysis = {
            'keywords': [],
            'skills_required': [],
            'experience_level': '',
            'industry': '',
            'job_type': '',
            'key_responsibilities': [],
            'nice_to_haves': []
        }

        # Convert to lowercase for analysis
        desc_lower = job_description.lower()

        # Extract skills from each category
        for category, skills in self.config['skills_categories'].items():
            found_skills = []
            for skill in skills:
                if skill.lower() in desc_lower:
                    found_skills.append(skill)
                    analysis['skills_required'].append(skill)

            if found_skills:
                analysis['keywords'].extend(found_skills)

        # Determine experience level
        if any(term in desc_lower for term in ['senior', 'lead', 'principal', 'manager']):
            analysis['experience_level'] = 'Senior'
        elif any(term in desc_lower for term in ['junior', 'entry', 'associate']):
            analysis['experience_level'] = 'Entry'
        else:
            analysis['experience_level'] = 'Mid'

        # Determine industry
        if any(term in desc_lower for term in ['healthcare', 'clinical', 'hospital', 'patient']):
            analysis['industry'] = 'Healthcare'
        elif any(term in desc_lower for term in ['tech', 'software', 'saas', 'startup']):
            analysis['industry'] = 'Technology'
        elif any(term in desc_lower for term in ['finance', 'banking', 'insurance']):
            analysis['industry'] = 'Finance'
        else:
            analysis['industry'] = 'General Business'

        # Extract key phrases for responsibilities
        responsibility_patterns = [
            r'responsible for (.*?)[.]',
            r'you will (.*?)[.]',
            r'duties include (.*?)[.]'
        ]

        for pattern in responsibility_patterns:
            matches = re.findall(pattern, desc_lower, re.IGNORECASE)
            analysis['key_responsibilities'].extend(matches[:3])  # Top 3 matches

        # Find nice-to-haves
        nice_patterns = [
            r'preferred[:](.*?)[.]',
            r'nice to have[:](.*?)[.]',
            r'bonus[:](.*?)[.]'
        ]

        for pattern in nice_patterns:
            matches = re.findall(pattern, desc_lower, re.IGNORECASE)
            analysis['nice_to_haves'].extend(matches)

        return analysis

    def calculate_skills_match(self, job_analysis: Dict, resume_skills: List[str]) -> int:
        """Calculate percentage match between job requirements and resume skills"""
        if not job_analysis['skills_required']:
            return 75  # Default if no specific skills found

        required_skills = set(skill.lower() for skill in job_analysis['skills_required'])
        resume_skills_lower = set(skill.lower() for skill in resume_skills)

        matched = required_skills.intersection(resume_skills_lower)

        if required_skills:
            return int((len(matched) / len(required_skills)) * 100)
        return 0

    def select_best_resume_template(self, job_analysis: Dict) -> int:
        """Select the most appropriate resume template based on job analysis"""
        scores = {}

        # Score each template
        for template_id, description in self.config['resume_templates'].items():
            score = 0

            # Healthcare focus
            if job_analysis['industry'] == 'Healthcare':
                if template_id == 2:  # Healthcare template
                    score += 10

            # Tech/AI focus
            elif job_analysis['industry'] == 'Technology':
                if template_id == 3:  # AI/Tech template
                    score += 10
                elif template_id == 5:  # General streamlined
                    score += 5

            # Business analysis
            elif 'business analysis' in ' '.join(job_analysis['keywords']).lower():
                if template_id == 4:  # Business analysis template
                    score += 10

            # Default scoring
            if template_id == 1:  # Comprehensive template as fallback
                score += 3

            scores[template_id] = score

        # Return template with highest score
        return max(scores.items(), key=lambda x: x[1])[0]

    def select_cover_letter_tier(self, job_analysis: Dict) -> int:
        """Select appropriate cover letter tier based on job analysis"""
        if job_analysis['industry'] == 'Healthcare':
            return 1
        elif job_analysis['industry'] == 'Technology' or 'AI' in ' '.join(job_analysis['keywords']):
            return 3
        else:
            return 2

    def create_application_folder(self, job_id: int, company_name: str) -> Path:
        """Create folder structure for application package"""
        date_str = datetime.now().strftime('%Y-%m-%d')
        folder_name = f"{date_str}_{company_name.replace(' ', '_').replace('/', '-')}"

        base_path = Path(__file__).parent.parent.parent / 'applications'
        folder_path = base_path / folder_name

        folder_path.mkdir(parents=True, exist_ok=True)

        return folder_path

    def copy_resume_template(self, template_id: int, destination: Path, job_analysis: Dict) -> Path:
        """Copy and customize resume template"""
        template_path = (Path(__file__).parent.parent.parent /
                        f'documents/resumes/templates/Matthew_Scott_Resume_Template{template_id}_Full.docx')

        if not template_path.exists():
            print(f"⚠️  Template {template_id} not found, using Template 1")
            template_id = 1
            template_path = (Path(__file__).parent.parent.parent /
                           'documents/resumes/templates/Matthew_Scott_Resume_Template1_Full.docx')

        resume_name = f"Matthew_Scott_Resume_Tailored.docx"
        resume_path = destination / resume_name

        shutil.copy(template_path, resume_path)

        # TODO: Add keyword injection into resume using python-docx

        return resume_path

    def copy_cover_letter_tier(self, tier: int, destination: Path, job_analysis: Dict) -> Path:
        """Copy and customize cover letter template"""
        tier_names = {
            1: 'Tier1_Healthcare',
            2: 'Tier2_GeneralBA',
            3: 'Tier3_AI_Transition'
        }

        template_name = f"Cover_Letter_{tier_names[tier]}.docx"
        template_path = (Path(__file__).parent.parent.parent /
                        f'documents/cover_letters/templates/{template_name}')

        cover_letter_name = f"Matthew_Scott_Cover_Letter.docx"
        cover_letter_path = destination / cover_letter_name

        shutil.copy(template_path, cover_letter_path)

        # TODO: Add customization using python-docx

        return cover_letter_path

    def create_application_notes(self, destination: Path, job_data: Dict,
                                job_analysis: Dict, template_id: int, tier: int) -> Path:
        """Create notes file with application details and keywords"""
        notes_path = destination / 'application_notes.md'

        with open(notes_path, 'w') as f:
            f.write(f"# Application Notes\n\n")
            f.write(f"**Company:** {job_data['company']}\n")
            f.write(f"**Position:** {job_data['title']}\n")
            f.write(f"**Applied Date:** {datetime.now().strftime('%Y-%m-%d')}\n")
            f.write(f"**Job URL:** {job_data['job_url']}\n\n")

            f.write(f"## Document Selection\n\n")
            f.write(f"- **Resume Template:** Template {template_id} - {self.config['resume_templates'][template_id]}\n")
            f.write(f"- **Cover Letter Tier:** Tier {tier} - {self.config['cover_letter_tiers'][tier]}\n\n")

            f.write(f"## Job Analysis\n\n")
            f.write(f"- **Industry:** {job_analysis['industry']}\n")
            f.write(f"- **Experience Level:** {job_analysis['experience_level']}\n")
            f.write(f"- **Skills Match:** {job_data.get('skills_match', 'TBD')}%\n\n")

            f.write(f"### Key Skills Identified\n\n")
            for skill in job_analysis['skills_required'][:10]:
                f.write(f"- {skill}\n")

            if job_analysis['key_responsibilities']:
                f.write(f"\n### Key Responsibilities\n\n")
                for resp in job_analysis['key_responsibilities']:
                    f.write(f"- {resp}\n")

            if job_analysis['nice_to_haves']:
                f.write(f"\n### Nice to Have\n\n")
                for item in job_analysis['nice_to_haves']:
                    f.write(f"- {item}\n")

            f.write(f"\n## Application Checklist\n\n")
            f.write(f"- [ ] Customize resume with job keywords\n")
            f.write(f"- [ ] Update cover letter with company name and position\n")
            f.write(f"- [ ] Review for grammar and formatting\n")
            f.write(f"- [ ] Save as PDF if required\n")
            f.write(f"- [ ] Submit application\n")
            f.write(f"- [ ] Update tracking database\n")
            f.write(f"- [ ] Set follow-up reminder for 7 days\n")

        return notes_path

    def generate_package(self, job_id: int) -> Tuple[bool, str, Path]:
        """Generate complete application package for a job"""
        try:
            # Get job details from database
            self.cursor.execute('''
                SELECT j.id, j.title, c.name as company, j.job_url, j.job_description,
                       j.skills_required, j.requirements, j.priority
                FROM jobs j
                LEFT JOIN companies c ON j.company_id = c.id
                WHERE j.id = ?
            ''', (job_id,))

            job_data = self.cursor.fetchone()

            if not job_data:
                return False, f"Job ID {job_id} not found", None

            job_dict = {
                'id': job_data[0],
                'title': job_data[1],
                'company': job_data[2] or 'Unknown',
                'job_url': job_data[3] or '',
                'job_description': job_data[4] or '',
                'skills_required': job_data[5] or '',
                'requirements': job_data[6] or '',
                'priority': job_data[7]
            }

            # Analyze job description
            description_text = job_dict['job_description'] + ' ' + job_dict['requirements']
            if not description_text.strip():
                description_text = job_dict['title']  # Fallback to title

            job_analysis = self.analyze_job_description(description_text)

            # Select best templates
            template_id = self.select_best_resume_template(job_analysis)
            cover_tier = self.select_cover_letter_tier(job_analysis)

            # Create application folder
            folder_path = self.create_application_folder(job_dict['id'], job_dict['company'])

            # Copy and customize documents
            resume_path = self.copy_resume_template(template_id, folder_path, job_analysis)
            cover_path = self.copy_cover_letter_tier(cover_tier, folder_path, job_analysis)
            notes_path = self.create_application_notes(folder_path, job_dict, job_analysis,
                                                      template_id, cover_tier)

            # Update database with document tracking
            self.cursor.execute('''
                SELECT id FROM applications WHERE job_id = ?
            ''', (job_id,))

            app_result = self.cursor.fetchone()
            if app_result:
                app_id = app_result[0]

                # Update application record
                self.cursor.execute('''
                    UPDATE applications
                    SET resume_version = ?, cover_letter_tier = ?
                    WHERE id = ?
                ''', (f"Template {template_id}", f"Tier {cover_tier}", app_id))

                # Add document records
                self.cursor.execute('''
                    INSERT INTO documents (application_id, document_type, filename,
                                         version, file_path, is_tailored)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (app_id, 'Resume', resume_path.name, f"Template {template_id}",
                     str(resume_path), True))

                self.cursor.execute('''
                    INSERT INTO documents (application_id, document_type, filename,
                                         version, file_path, is_tailored)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (app_id, 'Cover Letter', cover_path.name, f"Tier {cover_tier}",
                     str(cover_path), True))

                self.conn.commit()

            message = f"✅ Package created for {job_dict['company']} - {job_dict['title']}"
            return True, message, folder_path

        except Exception as e:
            return False, f"Error generating package: {str(e)}", None

    def close(self):
        """Close database connection"""
        self.conn.close()


def main():
    """Main function for CLI usage"""
    parser = argparse.ArgumentParser(description='Generate application package for a job')
    parser.add_argument('job_id', type=int, help='Job ID from database')
    parser.add_argument('--db', type=str, help='Path to database file')

    args = parser.parse_args()

    generator = ApplicationPackageGenerator(args.db)

    print(f"🚀 Generating application package for Job ID: {args.job_id}")
    print("=" * 50)

    success, message, folder_path = generator.generate_package(args.job_id)

    print(f"\n{message}")

    if success and folder_path:
        print(f"📁 Package location: {folder_path}")
        print(f"\n📋 Next steps:")
        print(f"  1. Open the folder: {folder_path}")
        print(f"  2. Customize the resume and cover letter")
        print(f"  3. Review the application notes")
        print(f"  4. Submit your application")
        print(f"  5. Update the tracking database")

    generator.close()


if __name__ == "__main__":
    main()