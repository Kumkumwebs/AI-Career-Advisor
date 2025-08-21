from src.infer import Advisor

def test_basic_inference():
    adv = Advisor()
    text = "Python, Django, REST, PostgreSQL, Docker, Git, Linux."
    role = adv.predict_role(text)
    assert isinstance(role, str)
