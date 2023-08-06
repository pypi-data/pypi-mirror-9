import pytest
import functools
from bobtemplates.pypbr.hooks import validate_name
from mrbob.bobexceptions import ValidationError


def test_validate_name():

    validate = functools.partial(validate_name, None, None)

    with pytest.raises(ValidationError):
        validate('123')

    with pytest.raises(TypeError):
        validate(123)

    ret = validate('test')
    assert ret == 'test'

    ret = validate('test_me')
    assert ret == 'test_me'

    ret = validate('t3st_m3')
    assert ret == 't3st_m3'
