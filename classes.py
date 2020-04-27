text = """
Мой дядя самых честных правил,
Когда не в шутку занемог,
Он уважать себя заставил
И лучше выдумать не мог.
"""


def word_gen(text):
    splited_text = text.split(' ')
    for word in splited_text:
        yield word


for item in range(5):

