import json
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.questions import Questions
from app.models.user_details import UserDetails
from datetime import datetime, timezone


async def add_daily_journal(user_id: int, summary: str, gpt_summary: str, db: Session):
    try:
        user_details = db.query(UserDetails).filter(
            UserDetails.user_id == user_id).first()
        current_date = datetime.now(timezone.utc).strftime(
            "%A, %B %d, %Y %H:%M:%S")

        def stripped_summary(s): return s.strip("Hello! Here is the summary:")

        if user_details:
            if user_details.journal_summary:
                current_summary = json.loads(user_details.to_dict()["journal_summary"])
                if current_summary.get(current_date):
                    current_summary[current_date].append(stripped_summary(summary))
                else:
                    current_summary[current_date] = [stripped_summary(summary)]
                user_details.journal_summary = json.dumps(current_summary)
                db.commit()
                return
            new_summary = json.dumps({
                current_date: [stripped_summary(summary)]
            })
            user_details.journal_summary = new_summary
            user_details.js_lastupdated = datetime.now(timezone.utc)
            db.commit()
    except Exception as e:
        print(e)


async def validate_and_insert_data(
    session: Session, user_id: int, data: list, source: str
):
    def is_valid_format(item):
        required_keys = {"questions", "options", "hint"}
        if not all(key in item for key in required_keys):
            return False
        if len(item["options"]) <= 2:
            return False
        if not all(
            "option" in option and "is_correct" in option for option in item["options"]
        ):
            return False
        return True

    def correct_format(item):
        # Ensure all required keys are present and rename incorrect keys
        correct_keys = {"questions": "questions", "options": "options", "hint": "hint"}
        required_keys = ["questions", "options", "hint"]
        i = 0
        for k, v in item.items():
            if k not in correct_keys:
                correct_keys[required_keys[i]] = v
            else:
                correct_keys[k] = v
            i = i + 1

        if "options" in correct_keys:
            for i in correct_keys["options"]:
                k, v = list(i.items())[0]  # Extract the key-value pair
                k1, v1 = list(i.items())[1]
                new_key = "option" if k != "option" else k
                new_key1 = "is_correct" if k1 != "is_correct" else k1
                i[new_key] = v  # Rename the key
                i[new_key1] = v1  # Rename the value


        return correct_keys

    try:
        for item in data:
            if not is_valid_format(item):
                item = correct_format(item)

            question_text = item["questions"]
            hint = item["hint"]

            # Create a new question instance
            question = Questions(
                user_id=user_id,
                question=question_text,
                hint=hint,
                source=source,  # Assuming 'profile' as the source, change as needed
            )

            # Add question to session
            session.add(question)
            session.commit()
            session.refresh(question)

            try:
                # Insert options for the question
                for option in item["options"]:
                    answer_option = AnswersOptions(
                        question_id=question.id,
                        option=option["option"],
                        is_correct=option["is_correct"],
                    )
                    session.add(answer_option)

                # Commit after adding all options for the question
                session.commit()
            except SQLAlchemyError as e:
                session.rollback()
                print(f"Error inserting options for question ID {question.id}: {e}")
                raise

    except SQLAlchemyError as e:
        session.rollback()
        print(f"Error inserting question: {e}")
        raise
