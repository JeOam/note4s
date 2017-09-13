# -*- coding: utf-8 -*-

"""
    test_utils.py
    ~~~~~~~
"""
import pytest
from note4s.utils import sent_mail, random_with_N_digits

@pytest.mark.webtest
def test_mail():
    with open('note4s/utils/registration_code.html') as f:
        content = f.read()
        content = content.replace('registration_code', '123456')
        result = sent_mail(
            from_mail="admin <admin@mg.note4s.com>",
            to_mail="jeoamlx@icloud.com",
            title="Test",
            content=content
        )
        assert result is True


def test_random_with_N_digits():
    code1 = random_with_N_digits(6)
    code2 = random_with_N_digits(6)
    assert len(str(code1)) == 6
    assert len(str(code2)) == 6
    assert code1 != code2
