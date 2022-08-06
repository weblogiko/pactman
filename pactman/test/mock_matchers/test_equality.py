import pytest
import requests
from pactman import Consumer, Equals, Like, Provider


@pytest.mark.parametrize("object", [None, [], {}, 1, 1.0, "string"])
def test_valid_types(object):
    Equals(object)


@pytest.mark.parametrize("object", [set(), b"bytes"])
def test_invalid_types(object):
    with pytest.raises(AssertionError) as e:
        Equals(object)

    assert "matcher must be one of " in str(e.value)


def test_basic_type():
    assert Equals(123).generate_matching_rule_v3() == {"matchers": [{"match": "equality"}]}


def test_v2_not_allowed():
    with pytest.raises(Equals.NotAllowed):
        Consumer("C").has_pact_with(Provider("P"), version="2.0.0").given("g").upon_receiving(
            "r"
        ).with_request("post", "/foo", body=Equals("bee")).will_respond_with(200)


def test_mock_usage_pass_validation():
    pact = (
        Consumer("C")
        .has_pact_with(Provider("P"), version="3.0.0")
        .given("g")
        .upon_receiving("r")
        .with_request("post", "/foo", body=Like({"a": "spam", "b": Equals("bee")}))
        .will_respond_with(200)
    )

    with pact:
        requests.post(f"{pact.uri}/foo", json={"a": "ham", "b": "bee"})


def test_mock_usage_fail_validation():
    pact = (
        Consumer("C")
        .has_pact_with(Provider("P"), version="3.0.0")
        .given("g")
        .upon_receiving("r")
        .with_request("post", "/foo", body=Like({"a": "spam", "b": Equals("bee")}))
        .will_respond_with(200)
    )

    with pytest.raises(AssertionError), pact:
        requests.post(f"{pact.uri}/foo", json={"a": "ham", "b": "wasp"})
