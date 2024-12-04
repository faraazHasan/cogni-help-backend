from collections.abc import AsyncGenerator
import json
from typing import Any

import openai
from app.utils.openai import start_openai
from app.features.aws.secretKey import get_secret_keys

keys = get_secret_keys()


class ResponseCreator:
    def __init__(self):
        self.client = start_openai()
        self.default_model = "gpt-4-0125-preview"
        self.fallback_model = "gpt-3.5-turbo"
        self.final_model = "gpt-3.5-turbo-instruct"
        self.max_tokens_gpt4 = 4096
        self.max_tokens_gpt3 = 4096
        self.max_tokens_final = 2049
        self.retry_attempts = 3  # Number of retries for each model
        self.openai_key = keys["OPEN_AI_KEY"]

    async def generate_response(
        self, messages: list[dict[str, str]]
    ) -> AsyncGenerator[str, Any]:
        model = "gpt-4"
        chat_completion_kwargs = {
            "model": model,
            "messages": messages,
            "max_tokens": 8192,
            "stream": True,
        }

        completion = None

        for _ in range(5):
            try:
                chat_completion_kwargs.update(
                    {
                        "model": (model := "gpt-4-0125-preview"),
                        "max_tokens": 4096,
                    }
                )
                completion = await self.client.chat.completions.create(
                    **chat_completion_kwargs
                )

            except openai.OpenAIError:
                chat_completion_kwargs.update(
                    {
                        "model": (model := "gpt-3.5-turbo"),
                        "max_tokens": 4096,
                    }
                )
                try:
                    completion = await self.client.chat.completions.create(
                        **chat_completion_kwargs
                    )
                except openai.OpenAIError:
                    model = "gpt-3.5-turbo-instruct"
                    try:
                        completion = await self.client.chat.completions.create(
                            model=model,
                            messages=messages,
                            temperature=0.3,
                            max_tokens=2049,
                            frequency_penalty=0,
                            presence_penalty=0.6,
                            stream=True,
                            stop=["Bot:"],
                        )
                    except openai.OpenAIError:
                        continue
                    else:
                        break
                else:
                    break
            else:
                break

        if completion is None:
            raise Exception("Failed to get completion")

        async def text_generator() -> AsyncGenerator[str, Any]:
            if completion is None:
                raise Exception("Failed to get completion")

            output_text = ""

            async for chunk in completion:
                choice = chunk.choices[0].delta
                # assistant or GPT-3
                content = choice.content or ""
                output_text += content
                yield content

        return text_generator()

    async def gpt_response_without_stream(self, chat_messages) -> str:
        model = "gpt-4"
        chat_completion_kwargs = {
            "model": model,
            "messages": chat_messages,
            "max_tokens": 8192,
        }

        text = ""
        for _ in range(5):
            try:
                chat_completion_kwargs.update(
                    {
                        "model": (model := "gpt-4-0125-preview"),
                        "max_tokens": 4096,
                    }
                )
                completion = await self.client.chat.completions.create(
                    **chat_completion_kwargs
                )
                text = completion.choices[0].message.content

            except openai.OpenAIError as e:
                print(e)
                chat_completion_kwargs.update(
                    {
                        "model": "gpt-3.5-turbo",
                        "max_tokens": 4096,
                    }
                )
                try:
                    completion = await self.client.chat.completions.create(
                        **chat_completion_kwargs
                    )
                    text = completion.choices[0].message.content

                except openai.OpenAIError as e:
                    print(e)
                    engine = "gpt-3.5-turbo-instruct"
                    try:
                        completion = await self.client.chat.completions.create(
                            engine=engine,
                            messages=chat_messages,
                            temperature=0.1,
                            max_tokens=2049,
                            top_p=1,
                            frequency_penalty=0,
                            presence_penalty=0.6,
                            stop=["Bot:"],
                        )
                    except openai.OpenAIError as e:
                        print(e)
                        continue
                    else:
                        text = completion.choices[0].message.content
                        break
                else:
                    break
            else:
                break

        return text

    async def user_input_summary_generator_prompt(
        self, *, user_summary: str
    ) -> list[dict[str, str]]:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an expert summarizer bot. "
                    "Your task is to generate a concise and meaningful summary based on the user's daily story. The summary should capture the key points and main events of the user's story.\n"
                    "The summary should be provided in easy-to-understand language, and it should be short and simple without directly copying the user's content.\n"
                    "If the user provides content that does not relate to a daily story or lacks sufficient detail for a summary, respond with: 'Sorry, we cannot generate a summary.'\n"
                    f"Here is the current user input: {user_summary}\n"
                    "If generating a summary, please provide it as follows: 'Hello! Here is the summary: <summary_text>' in easy-to-understand language."
                ),
            },
        ]

        return messages

    async def generate_summary(self, user_summary: str) -> AsyncGenerator[str, None]:
        """Gets chat-based GPT response"""
        prompt = await self.user_input_summary_generator_prompt(
            user_summary=user_summary
        )

        return await self.generate_response(prompt)

    async def profile_details_questions_generator_prompt(
        self, *, user_details: dict, time_offset: int
    ) -> list[dict[str, str]]:
        profile_summary = ""
        journal_summary = user_details["journal_summary"] if user_details["journal_summary"] else ""
        quiz_summary = json.dumps(
            user_details["quiz_summary"]) if user_details["quiz_summary"] else ""
        if user_details["profile_summary"]:
            profile_summary = json.loads(user_details["profile_summary"])
            profile_questions = []
            for field_ar in profile_summary:
                for field in field_ar:
                    profile_questions.append({field['field_name']: field["value"]})
            profile_summary = json.dumps(profile_questions)
        messages = [
            {
                "role": "system",
                "content": (
                    "[prose]"
                    "[Output only JSON ARRAY]"
                    "You are an advanced question-generating prompt. "
                    "Your task is to create multiple-choice questions (MCQs) based on the provided user's details and daily journals. "
                    "You will also be provided already created questions to compare with new ones to make sure no duplicate question gets generated."
                    "We aim to help users remember their personal information by asking questions about them. "
                    f"Generate {user_details['question_set'] if user_details['question_set'] else 5} MCQs from the details. "
                    "Each question should be simple, unique, and have only four options with one correct option. "
                    "Each question should include a hint that is easy and clear. "
                    "You will also be provided the offset of local time of user. The journal have array of objects in which the keys are dates you will add that offset in the date to match the users timezone before generating any question in which date is specified and if the date is yesterday's, tomorrow's or todays than use words 'yesterday' or 'tomorrow' 'today'"
                    "Do not give date in this format: 'YYYY-MM-DD' instead be more creative"
                    "Do not pick the field which value is empty and make sure every option in options have values"
                    "Output a JSON array where each element strictly follows this schema: "
                    '[{"questions": "string", "options":[{"option":"string", "is_correct":boolean}], "hint":"string"}]. '
                    "Here is the explanation of the schema: "
                    '- "questions": This key will store the question as a string. It must be in the form of a question related to the user\'s details. '
                    '- "options": This key will be an array containing four option objects. Each object must have: '
                    '  - "option": A string representing one of the four possible answers. '
                    '  - "is_correct": A boolean indicating if this option is the correct answer (true for correct, false for incorrect). '
                    '- "hint": This key will store a hint as a string to help the user answer the question. The hint should be clear and related to the question. '
                    "Do not add any keys or change any key names from the provided schema. "
                    "Ensure to escape any double quotes in the text. "
                    "Provide output in the schema provided only, without any introductory text or code fences. "
                    "Generate questions in the second person, addressing the user directly. "
                    "After generating the result, confirm that the keys are the same as the schema provided and that each question always has four options and a hint. "
                    "Here is an example: "
                    '[{"questions": "Where did you work before ?", '
                    '"options": [{"option": "Company A", "is_correct": true}, '
                    '{"option": "Company B", "is_correct": false}, '
                    '{"option": "Company C", "is_correct": false}, '
                    '{"option": "Company D", "is_correct": false}], '
                    '"hint": "Think about your previous employment."}]'
                ),
            },
            {
                "role": "user",
                "content": (
                    f"User details: {profile_summary}\n"
                    f"Daily journals: {journal_summary}\n"
                    f"Already created questions: {quiz_summary}\n"
                    f"offset: {time_offset}"
                ),
            },
        ]
        return messages

    async def generate_questions_from_profile_details(
        self, user_details: dict, time_offset: int
    ) -> AsyncGenerator[str, None]:
        """Gets chat-based GPT response"""
        prompt = await self.profile_details_questions_generator_prompt(
            user_details=user_details,
            time_offset=time_offset
        )
        gpt_response = await self.gpt_response_without_stream(prompt)
        return gpt_response

    async def modify_and_regenerate_questions(
        self, user_details: dict, error_message: str
    ) -> str:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an advanced question-generating prompt. "
                    "Your task is to create multiple-choice questions (MCQs) based on the provided user's details, including education, family details, personal preferences, and work history. "
                    "We aim to help users remember their personal information by asking questions about them. "
                    "Generate 10 MCQs from the user's details. "
                    "Each question should be simple, unique, and have only four options with one correct option. "
                    "Each question should include a hint that is easy and clear. "
                    "Output a JSON array where each element strictly follows this schema: "
                    '[{"questions": "string", "options":[{"option":"string", "is_correct":boolean}], "hint":"string"}]. '
                    "Here is the explanation of the schema: "
                    '- "questions": This key will store the question as a string. It must be in the form of a question related to the user\'s details. '
                    '- "options": This key will be an array containing four option objects. Each object must have: '
                    '  - "option": A string representing one of the four possible answers. '
                    '  - "is_correct": A boolean indicating if this option is the correct answer (true for correct, false for incorrect). '
                    '- "hint": This key will store a hint as a string to help the user answer the question. The hint should be clear and related to the question. '
                    "Do not add any keys or change any key names from the provided schema. "
                    "Ensure to escape any double quotes in the text. "
                    "Provide output in the schema provided only, without any introductory text or code fences. "
                    "Generate questions in the second person, addressing the user directly. "
                    "After generating the result, confirm that the keys are the same as the schema provided and that each question always has four options and a hint. "
                    "If an error occurs, modify the prompt and try again. "
                    "Here is an example: "
                    '[{"questions": "Where did you work before?", '
                    '"options": [{"option": "Company A", "is_correct": true}, '
                    '{"option": "Company B", "is_correct": false}, '
                    '{"option": "Company C", "is_correct": false}, '
                    '{"option": "Company D", "is_correct": false}], '
                    '"hint": "Think about your previous employment."}]'
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Education: {user_details.get('education', [])}\n"
                    f"Family Details: {user_details.get('family_details', [])}\n"
                    f"Personal Preferences: {user_details.get('personal_preferences', {})}\n"
                    f"Work History: {user_details.get('work_history', [])}\n"
                    f"Error Message: {error_message}\n"
                    "Modify the prompt to handle this error and generate the questions again."
                ),
            },
        ]
        return await self.gpt_response_without_stream(messages)

    async def profile_details_questions_generator(
        self, user_details: dict, source: str
    ) -> list[dict[str, str]]:
        messages = [
            {
                "role": "system",
                "content": (
                    "[prose]"
                    "[Output only JSON ARRAY]"
                    "You are an advanced question-generating prompt. "
                    f"Your task is to create multiple-choice questions (MCQs) based on the provided user's  {source} details. "
                    "We aim to help users remember their personal information by asking questions about them. "
                    "Generate 5 MCQs from the user's details. "
                    "Each question should be simple, unique, and have only four options with one correct option. "
                    "Each question should include a hint that is easy and clear. "
                    "Output a JSON array where each element strictly follows this schema: "
                    '[{"questions": "string", "options":[{"option":"string", "is_correct":boolean}], "hint":"string"}]. '
                    "Here is the explanation of the schema: "
                    '- "questions": This key will store the question as a string. It must be in the form of a question related to the user\'s details. '
                    '- "options": This key will be an array containing four option objects. Each object must have: '
                    '  - "option": A string representing one of the four possible answers. '
                    '  - "is_correct": A boolean indicating if this option is the correct answer (true for correct, false for incorrect). '
                    '- "hint": This key will store a hint as a string to help the user answer the question. The hint should be clear and related to the question. '
                    "Do not add any keys or change any key names from the provided schema. "
                    "Ensure to escape any double quotes in the text. "
                    "Provide output in the schema provided only, without any introductory text or code fences. "
                    "Generate questions in the second person, addressing the user directly. "
                    "After generating the result, confirm that the keys are the same as the schema provided and that each question always has four options and a hint. "
                    "Here is an example: "
                    '[{"questions": "Where did you work before ?", '
                    '"options": [{"option": "Company A", "is_correct": true}, '
                    '{"option": "Company B", "is_correct": false}, '
                    '{"option": "Company C", "is_correct": false}, '
                    '{"option": "Company D", "is_correct": false}], '
                    '"hint": "Think about your previous employment."}]'
                ),
            },
            {
                "role": "user",
                "content": (f"{source}: {user_details}\n"),
            },
        ]
        return await self.gpt_response_without_stream(messages)

    async def journal_questions_generator_prompt(
        self, *, user_summary: str
    ) -> list[dict[str, str]]:
        messages = [
            {
                "role": "system",
                "content": (
                    "[prose]"
                    "[Output only JSON ARRAY]"
                    "Imagine you're a quiz master creating multiple-choice questions from a user's daily journal entries. "
                    "Your goal is to help the user recall their last day by crafting 10 simple, distinct MCQs based on their activities described. "
                    "Each question should have four choices with only one correct answer and include an easy-to-understand hint. "
                    "Output a JSON array with each element like this: "
                    '[{"question": "string", "options":[{"option":"string", "is_correct":boolean}], "hint":"string"}]. '
                    "Do not add any keys or change any key names from the provided schema. "
                    "Ensure to escape any double quotes in the text. "
                    "Provide output in the schema provided only, without any introductory text or code fences. "
                    "Generate questions in the second person, addressing the user directly. "
                    "After generating the result, confirm that the keys are the same as the schema provided and that each question always has four options and a hint. "
                    "For example: "
                    '[{"question": "What was your first activity this morning?", '
                    '"options": [{"option": "Went for a run", "is_correct": true}, '
                    '{"option": "Slept in", "is_correct": false}, '
                    '{"option": "Had coffee", "is_correct": false}, '
                    '{"option": "Checked emails", "is_correct": false}], '
                    '"hint": "Recall your morning routine."}]'
                ),
            },
            {
                "role": "user",
                "content": user_summary,
            },
        ]
        return messages

    async def generate_questions_from_journal(
        self, user_summary: list[str]
    ) -> AsyncGenerator[str, None]:
        """Gets chat-based GPT response"""
        prompt = await self.journal_questions_generator_prompt(
            user_summary=user_summary
        )

        return await self.gpt_response_without_stream(prompt)
