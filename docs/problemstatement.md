# Problem Statement: AI-Powered Restaurant Recommendation System (Zomato Use Case)

Build an AI-powered restaurant recommendation system inspired by Zomato. The system should combine structured restaurant data with a Large Language Model (LLM) to provide relevant, personalized, and easy-to-understand suggestions.

## Objective

Design and implement an application that can:

- Accept user preferences (location, budget, cuisine, minimum rating, and additional constraints).
- Use a real-world restaurant dataset.
- Generate personalized recommendations using an LLM.
- Present recommendations in a clear and user-friendly format.

## Data Source

- Dataset: [Zomato Restaurant Recommendation Dataset](https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation)
- Platform: Hugging Face

## Functional Requirements

### 1) Data Ingestion and Preprocessing

- Load the Zomato dataset.
- Clean and normalize key fields.
- Extract relevant attributes, including:
  - Restaurant name
  - Location
  - Cuisine
  - Cost/Budget range
  - Rating
  - Any useful metadata

### 2) User Preference Collection

Collect the following inputs:

- Location (for example: Delhi, Bangalore)
- Budget (low, medium, high)
- Preferred cuisine (for example: Italian, Chinese)
- Minimum acceptable rating
- Additional preferences (for example: family-friendly, quick service)

### 3) Recommendation Pipeline

- Apply rule-based filtering on structured data using user preferences.
- Prepare shortlisted restaurant records for LLM input.
- Build a robust prompt so the LLM can:
  - Rank restaurants based on relevance.
  - Explain why each option is a good fit.
  - Optionally provide a concise summary of top choices.

### 4) Output and Presentation

Display top recommendations with:

- Restaurant name
- Cuisine
- Rating
- Estimated cost
- AI-generated explanation for recommendation

## Expected Outcome

The final system should deliver recommendations that are:

- Relevant to user preferences
- Explainable (clear reasoning for each suggestion)
- Actionable (easy for users to compare and choose)
