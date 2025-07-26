from google.ai.generativelanguage import FunctionDeclaration, Tool, Schema, Type


generate_and_save_declaration = FunctionDeclaration(
    name="generate_and_save",
    description="""This function generates interview questions for one or more topics with specific requirements for each topic.
You MUST call this function ONLY AFTER the user has provided ALL required information for each topic.
Each topic specification must include: topic name, number of MCQ questions, and number of descriptive questions.

IMPORTANT: You must extract and structure the user's requirements into topic specifications. For example:
- If user says "5 MCQ for Excel Formulas and 2 descriptive for VBA", create separate specifications
- If user says "10 questions on Pivot Tables, mixed types", ask for clarification on MCQ vs descriptive breakdown
- Always ensure each topic has clear counts for both MCQ and descriptive questions (can be 0 for either type)

This function handles the complete generation and saving process for all specified topics.""",
    parameters=Schema(
        type_=Type.OBJECT,
        description="Topic specifications for question generation",
        properties={
            "topic_specifications": Schema(
                type_=Type.ARRAY,
                description="Array of topic specifications",
                items=Schema(
                    type_=Type.OBJECT,
                    description="Individual topic specification",
                    properties={
                        "topic": Schema(
                            type_=Type.STRING,
                            description="The topic name for questions"
                        ),
                        "mcq_count": Schema(
                            type_=Type.NUMBER,
                            description="Number of multiple choice questions to generate"
                        ),
                        "descriptive_count": Schema(
                            type_=Type.NUMBER,
                            description="Number of descriptive questions to generate"
                        )
                    },
                    required=["topic", "mcq_count", "descriptive_count"]
                )
            )
        },
        required=["topic_specifications"]
    )
)

generate_web_research_declaration = FunctionDeclaration(
    name="web_research_and_save",
    description="""This function uses Perplexity AI to crawl the web and generate interview questions based on the latest information for one or more topics.
You MUST call this function ONLY AFTER the user has provided ALL required information for each topic.
Each topic specification must include: topic name, number of MCQ questions, and number of descriptive questions.

IMPORTANT: You must extract and structure the user's requirements into topic specifications. For example:
- If user says "5 MCQ for Latest React Features and 2 descriptive for Next.js Updates", create separate specifications
- If user says "10 questions on Current AI Trends, mixed types", ask for clarification on MCQ vs descriptive breakdown
- Always ensure each topic has clear counts for both MCQ and descriptive questions (can be 0 for either type)

This function leverages web crawling to ensure questions are based on current information and industry trends.""",
    parameters=Schema(
        type_=Type.OBJECT,
        description="Topic specifications for web-research based question generation",
        properties={
            "topic_specifications": Schema(
                type_=Type.ARRAY,
                description="Array of topic specifications",
                items=Schema(
                    type_=Type.OBJECT,
                    description="Individual topic specification",
                    properties={
                        "topic": Schema(
                            type_=Type.STRING,
                            description="The topic name for questions"
                        ),
                        "mcq_count": Schema(
                            type_=Type.NUMBER,
                            description="Number of multiple choice questions to generate"
                        ),
                        "descriptive_count": Schema(
                            type_=Type.NUMBER,
                            description="Number of descriptive questions to generate"
                        )
                    },
                    required=["topic", "mcq_count", "descriptive_count"]
                )
            )
        },
        required=["topic_specifications"]
    )
)

# Create Tool objects
generate_and_save_tool = Tool(function_declarations=[generate_and_save_declaration])
generate_web_research_tool = Tool(function_declarations=[generate_web_research_declaration])