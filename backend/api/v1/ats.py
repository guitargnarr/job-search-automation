"""
ATS Optimization API endpoints
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from typing import Dict, Any, Optional
import tempfile
import os
from pathlib import Path

from backend.services.ats_optimizer import ats_optimizer
from backend.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()

@router.post("/analyze-job")
async def analyze_job_description(
    job_description: str = Form(...)
) -> Dict[str, Any]:
    """
    Analyze a job description to extract keywords and requirements
    This is the foundation for ATS optimization
    """
    try:
        analysis = ats_optimizer.analyze_job_description(job_description)

        return {
            "status": "success",
            "analysis": analysis,
            "top_keywords": analysis['keywords'][:20],
            "required_skills": analysis['required_skills'],
            "message": f"Found {len(analysis['keywords'])} keywords and {len(analysis['required_skills'])} required skills"
        }

    except Exception as e:
        logger.error(f"Job analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/optimize-resume")
async def optimize_resume(
    resume_file: UploadFile = File(...),
    job_description: str = Form(...)
) -> Dict[str, Any]:
    """
    Optimize resume for specific job description
    Returns ATS score and recommendations
    """
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=resume_file.filename) as tmp:
            content = await resume_file.read()
            tmp.write(content)
            tmp_path = tmp.name

        # Analyze job description
        job_analysis = ats_optimizer.analyze_job_description(job_description)

        # Optimize resume
        optimization_report = ats_optimizer.optimize_resume(
            tmp_path,
            job_analysis
        )

        # Clean up temp file
        os.unlink(tmp_path)

        return {
            "status": "success",
            "current_score": optimization_report['current_score'],
            "missing_keywords": optimization_report['missing_keywords'][:10],
            "recommendations": optimization_report['recommendations'],
            "keyword_density": optimization_report['keyword_density'],
            "format_issues": optimization_report['format_issues'],
            "message": f"Current ATS score: {optimization_report['current_score']}/100"
        }

    except Exception as e:
        logger.error(f"Resume optimization failed: {e}")
        if 'tmp_path' in locals():
            os.unlink(tmp_path)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-optimized")
async def generate_optimized_resume(
    resume_file: UploadFile = File(...),
    job_description: str = Form(...)
):
    """
    Generate an optimized version of the resume
    Returns downloadable optimized resume
    """
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=resume_file.filename) as tmp:
            content = await resume_file.read()
            tmp.write(content)
            tmp_path = tmp.name

        # Generate output path
        output_path = tmp_path.replace('.', '_optimized.')

        # Analyze job description
        job_analysis = ats_optimizer.analyze_job_description(job_description)

        # Create optimized resume
        optimization_report = ats_optimizer.optimize_resume(
            tmp_path,
            job_analysis,
            output_path
        )

        # Check if optimized file was created
        if not Path(output_path).exists():
            raise HTTPException(status_code=500, detail="Failed to create optimized resume")

        # Return file
        return FileResponse(
            output_path,
            media_type='application/octet-stream',
            filename=f"optimized_{resume_file.filename}"
        )

    except Exception as e:
        logger.error(f"Resume generation failed: {e}")
        if 'tmp_path' in locals():
            os.unlink(tmp_path)
        if 'output_path' in locals() and Path(output_path).exists():
            os.unlink(output_path)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/score")
async def calculate_ats_score(
    resume_file: UploadFile = File(...),
    job_description: str = Form(...)
) -> Dict[str, Any]:
    """
    Calculate ATS compatibility score for resume
    """
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=resume_file.filename) as tmp:
            content = await resume_file.read()
            tmp.write(content)
            tmp_path = tmp.name

        # Analyze both
        job_analysis = ats_optimizer.analyze_job_description(job_description)
        resume_text = ats_optimizer._read_resume(tmp_path)
        resume_analysis = ats_optimizer._analyze_resume(resume_text)

        # Calculate score
        score = ats_optimizer._calculate_ats_score(resume_analysis, job_analysis)

        # Clean up
        os.unlink(tmp_path)

        return {
            "ats_score": score,
            "pass_likelihood": "High" if score >= 70 else "Medium" if score >= 50 else "Low",
            "message": f"ATS Score: {score}/100 - {'Good chance of passing' if score >= 70 else 'Needs improvement'}"
        }

    except Exception as e:
        logger.error(f"ATS scoring failed: {e}")
        if 'tmp_path' in locals():
            os.unlink(tmp_path)
        raise HTTPException(status_code=500, detail=str(e))