from app.evaluation import calculate_bleu

text = "Hello"

translated_text = "Bonjour, comment allez-vous"
reference_text = "Bonjour, comment vas-tu"

def test_evaluation():
    output = calculate_bleu(translated_text, reference_text)

    if output == 1:
        "Successful test"
    else:
        "unsuccessful test"


