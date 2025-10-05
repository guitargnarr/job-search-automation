# Job Search Management System

A comprehensive job search tracking and automation system designed to streamline the application process, track progress, and improve success rates.

## Directory Structure

```
Job_Search/
├── applications/           # Individual application packages by date and company
├── documents/              # All job search documents
│   ├── resumes/           # Resume versions and templates
│   ├── cover_letters/     # Cover letter templates and sent versions
│   └── references/        # Reference documents
├── tracking/              # Application tracking and analytics
│   ├── database/         # SQLite database files
│   ├── exports/          # CSV/Excel exports
│   └── reports/          # Generated analytics reports
├── automation/            # Automation scripts and tools
│   ├── generators/       # Document generation scripts
│   ├── scrapers/        # Job board scrapers
│   ├── analyzers/       # Job fit analysis tools
│   └── notifiers/       # Reminder and notification systems
├── research/             # Company and industry research
├── interview_prep/       # Interview preparation materials
└── config/              # Configuration files
```

## Quick Start

1. **Track a new application**: Use the tracking database to log new applications
2. **Generate documents**: Run scripts in `automation/generators/` to create tailored resumes/cover letters
3. **Review analytics**: Check `tracking/reports/` for insights on your job search progress

## Key Features

- **Version Control**: All documents are tracked with git
- **Automated Document Generation**: Python scripts for creating tailored application materials
- **Comprehensive Tracking**: Database-backed tracking of all applications and interactions
- **Analytics Dashboard**: Visual insights into application success rates and patterns
- **Follow-up Management**: Automated reminders for application follow-ups

## Current Resume Templates

1. **Template 1**: Full comprehensive version
2. **Template 2**: Healthcare-focused
3. **Template 3**: AI/Tech transition emphasis
4. **Template 4**: Business analysis focus
5. **Template 5**: General purpose

## Cover Letter Tiers

- **Tier 1**: Healthcare and clinical positions
- **Tier 2**: General business analyst roles
- **Tier 3**: AI/Tech transition positions

## Database Schema

The tracking database includes:
- Job listings with full details
- Application status and history
- Company research data
- Contact information for recruiters/hiring managers
- Document version tracking
- Success metrics and analytics

## Automation Scripts

Located in `automation/generators/`:
- `create_cover_letters.py` - Generate cover letters from templates
- `create_resume_docx.py` - Create Word resumes
- Various template creation scripts

## Git Workflow

```bash
# Regular commits for document changes
git add .
git commit -m "Updated resume for [Company] application"

# Branch strategy
main         # Stable versions of all documents
dev          # Work in progress
templates    # Template development
```

## Security Notes

- Sensitive information is excluded via .gitignore
- Personal details should be stored in environment variables
- API keys go in `config/api_keys.env` (not tracked)

## Next Steps

- [ ] Set up SQLite database
- [ ] Create job aggregator script
- [ ] Build analytics dashboard
- [ ] Implement follow-up reminder system

---

*Last Updated: October 2025*