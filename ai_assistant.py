import os
def ask_ai(question, context=""):
    api=os.getenv("GEMINI_API_KEY")
    if not api:
        return ("AI API key is not configured. Set GEMINI_API_KEY and restart Streamlit.\n\n"
                "Demo response: I can help with campus information, study planning, "
                "announcements, complaints and academic questions.")
    try:
        from google import genai
        client=genai.Client(api_key=api)
        prompt=f"""You are AI Campus Connect, a helpful college assistant.
Use the context when relevant. Do not invent college-specific facts.
Context:
{context[:12000]}
Question: {question}
Answer clearly and briefly."""
        r=client.models.generate_content(model="gemini-3.8-flash", contents=prompt)
        return r.text
    except Exception as e:
        return f"AI service error: {e}"
