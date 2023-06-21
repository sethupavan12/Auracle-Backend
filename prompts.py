



EXAMPLE_CONTEXT : str = """Software Description:  mobile application aimed at supporting student mental health. 
key technologies such as React Native, TypeScript, MongoDB, and Django (Wagtail CMS), the application offering a host of tools to aid mental well-being.
Target Audience: University students. Key Features: Daily motivational quotes, a mood tracking system, a personal self-reflection journal, 
mood-based activity suggestions, a community center for anonymous sharing and support, mental health resources, and self-assessment quizzes 
Constraints and Requirements: None."""


template = """You are a Software Development analysis bot. 
You need to analyse all the information given to you here {context}
Based on the analysis, you should generate functional requirements and non functional requirements.
You should also identify USPs (unique selling points) this software should have to compete in the market.

These are requirements and USPs for given software description:
"""

