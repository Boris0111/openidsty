from datetime import date
from decimal import Decimal
import pytest
from app.payloads import encoded, raw_payload, decimal_text


def test_encoded_is_compact_sorted_and_keeps_exact_decimals():
    value={'b':Decimal('1.2500'),'a':[date(2026,10,23),None,True,3],'c':{'d':'文字'}}
    assert encoded(value)=='{"a":["2026-10-23",null,true,3],"b":"1.25","c":{"d":"文字"}}'
    assert decimal_text(Decimal('0.000'))=='0' and decimal_text(Decimal('100'))=='100'


@pytest.mark.parametrize('value',[1.5,{1:'x'},object(),Decimal('NaN')])
def test_encoded_rejects_values_without_an_exact_identity(value):
    with pytest.raises(ValueError):
        encoded(value)


def test_raw_payload_keeps_source_precision_but_rejects_non_finite():
    # Source cells beyond the canonical precision stay as exact evidence text.
    assert raw_payload({'cell':Decimal('1.00000000000000000001'),'rows':(Decimal('2'),)})=={'cell':'1.00000000000000000001','rows':['2']}
    with pytest.raises(ValueError):
        raw_payload({'cell':Decimal('Infinity')})
    with pytest.raises(ValueError):
        raw_payload({2:'x'})
