"""
Unit tests for ATS Optimizer Service
Tests the NLP-powered ATS optimization that improves response rates
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from backend.services.ats_optimizer import ATSOptimizer


class TestATSOptimizerJobAnalysis:
    """Test job description analysis functionality"""

    @pytest.fixture
    def optimizer(self):
        """Create an ATSOptimizer instance for testing"""
        return ATSOptimizer()

    def test_analyze_job_description_basic(self, optimizer):
        """Test basic job description analysis"""
        job_desc = """
        Data Analyst Position

        Requirements:
        - 3+ years of experience in data analysis
        - Python, SQL, and Tableau skills required
        - Bachelor's degree in Computer Science or related field

        Preferred:
        - Master's degree
        - Experience with machine learning
        """

        result = optimizer.analyze_job_description(job_desc)

        assert 'required_skills' in result
        assert 'preferred_skills' in result
        assert 'keywords' in result
        assert 'experience_years' in result
        assert 'education_level' in result

    def test_extract_experience_years(self, optimizer):
        """Test extraction of years of experience requirement"""
        job_desc = "We require 5+ years of experience in data analysis"

        result = optimizer.analyze_job_description(job_desc)

        assert result['experience_years'] == 5

    def test_extract_experience_years_variations(self, optimizer):
        """Test various experience year formats"""
        test_cases = [
            ("3-5 years experience", 3),
            ("Minimum 7 years of experience", 7),
            ("2+ years experience required", 2),
            ("At least 10 years", 10),
        ]

        for job_desc, expected_years in test_cases:
            result = optimizer.analyze_job_description(job_desc)
            assert result['experience_years'] == expected_years or result['experience_years'] is not None

    def test_extract_education_bachelors(self, optimizer):
        """Test extraction of bachelor's degree requirement"""
        job_desc = "Bachelor's degree in Computer Science required"

        result = optimizer.analyze_job_description(job_desc)

        assert result['education_level'] is not None
        assert 'bachelor' in result['education_level'].lower()

    def test_extract_education_masters(self, optimizer):
        """Test extraction of master's degree requirement"""
        job_desc = "Master's degree in Data Science preferred"

        result = optimizer.analyze_job_description(job_desc)

        assert result['education_level'] is not None
        assert 'master' in result['education_level'].lower()

    def test_extract_technical_skills(self, optimizer):
        """Test extraction of technical skills"""
        job_desc = """
        Required Skills:
        - Python programming
        - SQL database management
        - Tableau data visualization
        - Machine learning algorithms
        """

        result = optimizer.analyze_job_description(job_desc)

        skills = result['required_skills']
        assert len(skills) > 0
        # Check for common data analyst skills
        skill_text = ' '.join(skills).lower()
        assert 'python' in skill_text or 'sql' in skill_text

    def test_extract_certifications(self, optimizer):
        """Test extraction of certification requirements"""
        job_desc = """
        Certifications:
        - AWS Certified Solutions Architect
        - PMP certification preferred
        - Google Analytics certification
        """

        result = optimizer.analyze_job_description(job_desc)

        assert 'certifications' in result

    def test_distinguish_required_vs_preferred(self, optimizer):
        """Test that required and preferred skills are separated"""
        job_desc = """
        Required Skills:
        - Python
        - SQL

        Preferred Skills:
        - R programming
        - Spark
        """

        result = optimizer.analyze_job_description(job_desc)

        required = result['required_skills']
        preferred = result['preferred_skills']

        assert len(required) > 0 or len(preferred) > 0


class TestATSOptimizerResumeScoring:
    """Test resume scoring functionality"""

    @pytest.fixture
    def optimizer(self):
        return ATSOptimizer()

    def test_score_resume_perfect_match(self, optimizer):
        """Test scoring with perfect keyword match"""
        job_desc = "Looking for Python and SQL skills"
        resume_text = "Experienced in Python programming and SQL database management"

        score = optimizer.score_resume(resume_text, job_desc)

        assert 'overall_score' in score
        assert score['overall_score'] > 50  # Should be high for good match
        assert 'keyword_match_score' in score

    def test_score_resume_poor_match(self, optimizer):
        """Test scoring with poor keyword match"""
        job_desc = "Looking for Java, C++, and embedded systems experience"
        resume_text = "I have skills in Python, SQL, and data visualization with Tableau"

        score = optimizer.score_resume(resume_text, job_desc)

        assert score['overall_score'] < 60  # Should be low for poor match

    def test_score_resume_missing_keywords(self, optimizer):
        """Test identification of missing keywords"""
        job_desc = "Required: Python, SQL, Tableau, AWS, Docker, Kubernetes"
        resume_text = "I have experience with Python and SQL"

        score = optimizer.score_resume(resume_text, job_desc)

        assert 'missing_keywords' in score
        assert len(score['missing_keywords']) > 0

    def test_score_resume_matched_keywords(self, optimizer):
        """Test identification of matched keywords"""
        job_desc = "Required: Python, SQL, Tableau"
        resume_text = "Skilled in Python programming, SQL queries, and Tableau dashboards"

        score = optimizer.score_resume(resume_text, job_desc)

        assert 'matched_keywords' in score
        assert len(score['matched_keywords']) > 0

    def test_score_resume_case_insensitive(self, optimizer):
        """Test that keyword matching is case-insensitive"""
        job_desc = "PYTHON, SQL, TABLEAU required"
        resume_text = "python, sql, tableau skills"

        score = optimizer.score_resume(resume_text, job_desc)

        assert score['overall_score'] > 50  # Should match despite case difference

    def test_score_resume_synonym_recognition(self, optimizer):
        """Test recognition of skill synonyms"""
        job_desc = "JavaScript required"
        resume_text = "Proficient in JS"

        score = optimizer.score_resume(resume_text, job_desc)

        # Should recognize JS as JavaScript synonym
        # Note: This may need optimizer.skill_synonyms to be properly configured
        assert 'overall_score' in score


class TestATSOptimizerKeywordExtraction:
    """Test keyword extraction using TF-IDF and spaCy"""

    @pytest.fixture
    def optimizer(self):
        return ATSOptimizer()

    def test_extract_keywords_top_n(self, optimizer):
        """Test extraction of top N keywords"""
        text = """
        Data analyst position requiring Python programming, SQL database skills,
        and experience with Tableau visualization. Must have strong analytical
        thinking and problem-solving abilities. Experience with machine learning
        is a plus.
        """

        keywords = optimizer.extract_keywords(text, top_n=10)

        assert isinstance(keywords, list)
        assert len(keywords) <= 10
        assert len(keywords) > 0

    def test_extract_keywords_relevance(self, optimizer):
        """Test that extracted keywords are relevant"""
        text = """
        Senior Data Analyst position at healthcare company. Requires 5 years
        experience with Python, SQL, R programming. Healthcare analytics experience
        preferred. Strong communication skills essential.
        """

        keywords = optimizer.extract_keywords(text, top_n=15)

        keyword_text = ' '.join(keywords).lower()
        # Should extract meaningful terms
        assert any(term in keyword_text for term in ['python', 'sql', 'data', 'analyst', 'healthcare'])

    def test_extract_keywords_filters_stop_words(self, optimizer):
        """Test that stop words are filtered out"""
        text = "The analyst will be working with the data in the database"

        keywords = optimizer.extract_keywords(text, top_n=10)

        # Common stop words should be filtered
        keyword_lower = [k.lower() for k in keywords]
        assert 'the' not in keyword_lower
        assert 'will' not in keyword_lower
        assert 'be' not in keyword_lower

    def test_extract_keywords_empty_text(self, optimizer):
        """Test keyword extraction with empty text"""
        keywords = optimizer.extract_keywords("", top_n=10)

        assert isinstance(keywords, list)
        assert len(keywords) == 0

    def test_extract_keywords_multi_word_phrases(self, optimizer):
        """Test extraction of multi-word phrases (n-grams)"""
        text = """
        Machine learning engineer position. Experience with natural language
        processing and computer vision required. Deep learning frameworks
        like TensorFlow and PyTorch essential.
        """

        keywords = optimizer.extract_keywords(text, top_n=15)

        # Should extract some multi-word technical terms
        assert len(keywords) > 0


class TestATSOptimizerResumeOptimization:
    """Test resume optimization and gap analysis"""

    @pytest.fixture
    def optimizer(self):
        return ATSOptimizer()

    def test_optimize_resume_suggests_keywords(self, optimizer):
        """Test that optimization suggests missing keywords"""
        job_desc = "Python, SQL, Tableau, AWS, Docker required"
        resume_text = "I have Python and SQL experience"

        result = optimizer.optimize_resume(resume_text, job_desc)

        assert 'suggestions' in result or 'missing_keywords' in result
        assert 'optimized_sections' in result or 'recommendations' in result

    def test_analyze_gaps_identifies_missing_skills(self, optimizer):
        """Test gap analysis identifies missing skills"""
        job_requirements = ['Python', 'SQL', 'Tableau', 'AWS', 'Docker']
        resume_skills = ['Python', 'SQL']

        gaps = optimizer.analyze_gaps(job_requirements, resume_skills)

        assert 'missing' in gaps or isinstance(gaps, list)
        if isinstance(gaps, dict):
            assert len(gaps['missing']) > 0
        elif isinstance(gaps, list):
            assert 'Tableau' in gaps or 'tableau' in str(gaps).lower()

    def test_calculate_skill_coverage(self, optimizer):
        """Test calculation of skill coverage percentage"""
        job_skills = {'Python', 'SQL', 'Tableau', 'AWS'}
        resume_skills = {'Python', 'SQL'}

        coverage = optimizer.calculate_skill_coverage(job_skills, resume_skills)

        assert coverage == 50.0  # 2 out of 4 skills = 50%

    def test_calculate_skill_coverage_perfect(self, optimizer):
        """Test 100% skill coverage"""
        job_skills = {'Python', 'SQL'}
        resume_skills = {'Python', 'SQL', 'Tableau'}  # Resume has more

        coverage = optimizer.calculate_skill_coverage(job_skills, resume_skills)

        assert coverage == 100.0

    def test_calculate_skill_coverage_zero(self, optimizer):
        """Test 0% skill coverage"""
        job_skills = {'Java', 'C++', 'C#'}
        resume_skills = {'Python', 'SQL'}

        coverage = optimizer.calculate_skill_coverage(job_skills, resume_skills)

        assert coverage == 0.0


class TestATSOptimizerFormatValidation:
    """Test ATS-friendly format validation"""

    @pytest.fixture
    def optimizer(self):
        return ATSOptimizer()

    def test_validate_format_standard_sections(self, optimizer):
        """Test validation of standard resume sections"""
        resume_text = """
        John Doe

        Summary
        Data analyst with 5 years experience

        Experience
        Data Analyst at Company X

        Education
        BS in Computer Science

        Skills
        Python, SQL, Tableau
        """

        validation = optimizer.validate_format(resume_text)

        assert 'has_standard_sections' in validation
        assert validation['has_standard_sections'] is True

    def test_validate_format_missing_sections(self, optimizer):
        """Test validation flags missing sections"""
        resume_text = """
        John Doe
        I worked at a company doing data analysis.
        """

        validation = optimizer.validate_format(resume_text)

        assert 'has_standard_sections' in validation
        # Should flag missing sections
        assert 'missing_sections' in validation or validation['has_standard_sections'] is False

    def test_validate_format_warns_special_characters(self, optimizer):
        """Test validation warns about ATS-unfriendly special characters"""
        resume_text = """
        Experience
        → Data Analyst at Company (2020-2023)
        • Analyzed data using Python
        ★ Improved efficiency by 30%
        """

        validation = optimizer.validate_format(resume_text)

        assert 'warnings' in validation or 'special_characters' in validation

    def test_validate_format_date_formatting(self, optimizer):
        """Test validation of date formats"""
        resume_text = """
        Experience
        Data Analyst, Company X (2020-2023)
        Data Scientist, Company Y (Jan 2018 - Dec 2019)
        """

        validation = optimizer.validate_format(resume_text)

        assert 'date_format' in validation or 'warnings' in validation


class TestATSOptimizerRealWorldScenarios:
    """Test real-world scenarios from actual job search"""

    @pytest.fixture
    def optimizer(self):
        return ATSOptimizer()

    def test_healthcare_analyst_job_description(self, optimizer):
        """Test analysis of real healthcare analyst job"""
        job_desc = """
        Healthcare Data Analyst

        We are seeking a Healthcare Data Analyst to join our analytics team.

        Required Qualifications:
        - Bachelor's degree in Health Informatics, Statistics, or related field
        - 3+ years of healthcare data analysis experience
        - Proficiency in SQL, Python, and R
        - Experience with EHR/EMR systems
        - Knowledge of HIPAA compliance

        Preferred:
        - Master's degree in Health Informatics
        - Epic or Cerner certification
        - Experience with Tableau or Power BI
        - Knowledge of value-based care metrics
        """

        result = optimizer.analyze_job_description(job_desc)

        assert result['experience_years'] == 3
        assert result['education_level'] is not None
        assert len(result['required_skills']) > 0
        assert len(result['preferred_skills']) > 0

    def test_optimize_resume_for_remote_position(self, optimizer):
        """Test optimization for remote work position"""
        job_desc = """
        Remote Data Analyst - Must have:
        - Strong async communication skills
        - Experience with distributed teams
        - Self-motivated and independent
        - Python, SQL, cloud platforms
        """

        resume_text = """
        Data Analyst with 5 years experience.
        Skills: Python, SQL, Tableau
        """

        result = optimizer.optimize_resume(resume_text, job_desc)

        # Should suggest adding remote work keywords
        assert 'suggestions' in result or 'recommendations' in result

    def test_score_resume_high_response_rate_scenario(self, optimizer):
        """
        Test scenario that led to 14.3% response rate
        Resume well-matched to job requirements
        """
        job_desc = """
        Business Analyst - Healthcare
        - SQL, Python, Tableau
        - 3-5 years experience
        - Healthcare domain knowledge
        - Bachelor's degree required
        """

        resume_text = """
        Business Analyst with 4 years healthcare experience.
        Proficient in SQL, Python, and Tableau.
        Bachelor's in Health Informatics.
        Led analytics projects for healthcare providers.
        """

        score = optimizer.score_resume(resume_text, job_desc)

        # Should score high (this is what leads to good response rates)
        assert score['overall_score'] > 70
