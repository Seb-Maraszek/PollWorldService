def get_model_fields(model, excluded=None):
    if excluded is None:
        excluded = []
    return [field.name for field in type(model)._meta.fields if field.name not in excluded]


def correct_answer(question_id, option_ids):
    return [
        {
            "question": question_id,
            "options": option_ids,
            "text_answer": "text"
        }
    ]


def incorrect_answer_first(question_id, option_ids):
    return [
        {
            "question": ["Wrong data format"],
            "option": option_ids,
            "text_answer": "text"
        },
    ]


def incorrect_answer_second(question_id, option_ids):
    return [
        {
            "question": question_id,
            "wrong_text_here": option_ids,
            "text_answer": "text"
        },
    ]


mock_survey = {
    "name": "Name12",
    "description": "Dziwny opis ",
    "short_description": "Opais",
    "category": "SPORT",

    "questions": [
        {"required": False,
         "name": "single_first",
         "type": "SINGLE",
         "options": ["Opcja 1", "Opcja 2", "Opcja 3"]},

        {"required": True,
         "name": "multi_quest",
         "type": "MULTI",
         "options": ["Opcja 4", "Opcja 5", "Opcja 6"]},

        {"required": True,
         "name": "text",
         "type": "TEXT",
         "options": []}
    ]
}

mock_survey_incorrect_fields = {
    "nam": "Name",
    "description": "description ",
    "short_description": "short",
    "category": "SPORT",

    "questions": [
        {"required": False,
         "name": "single_first",
         "type": "SINGLE",
         "options": ["Opcja 1", "Opcja 2", "Opcja 3"]},

        {"required": True,
         "name": "multi_quest",
         "type": "MULTI",
         "options": ["Opcja 4", "Opcja 5", "Opcja 6"]},

        {"required": True,
         "name": "text",
         "type": "TEXT",
         "options": []}
    ]
}

mock_survey_incorrect_options_single = {
    "name": "Name",
    "description": "description ",
    "short_description": "short",
    "category": "SPORT",

    "questions": [
        {"required": False,
         "name": "single_first",
         "type": "SINGLE",
         "options": []},

        {"required": True,
         "name": "multi_quest",
         "type": "MULTI",
         "options": ["Opcja 4", "Opcja 5", "Opcja 6"]},

        {"required": True,
         "name": "text",
         "type": "TEXT",
         "options": []}
    ]
}

mock_survey_incorrect_options_text = {
    "name": "Name",
    "description": "description ",
    "short_description": "short",
    "category": "SPORT",

    "questions": [
        {"required": False,
         "name": "single_first",
         "type": "SINGLE",
         "options": ["Opcja 1"]},

        {"required": True,
         "name": "multi_quest",
         "type": "MULTI",
         "options": ["Opcja 4", "Opcja 5", "Opcja 6"]},

        {"required": True,
         "name": "text",
         "type": "TEXT",
         "options": ["Opcja 4"]}
    ]
}
