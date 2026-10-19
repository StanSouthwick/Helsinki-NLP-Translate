from app.evaluation import calculate_bleu

text = "Hello"

def test_evaluation():
    output = calculate_bleu(text, text)

    if output == 1:
        "Successful test"
    else:
        "unsuccessful test"


