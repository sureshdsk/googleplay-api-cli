import json
from dataclasses import dataclass
from enum import Enum

@dataclass(frozen=True)
class GooglePlayCredential:
    gsf_id: str
    auth_sub_token: str
    device_code_name: str


class AppAvailability(Enum):
    AVAILABLE = 1
    GEO_RESTRICTED = 2
    UNKNOWN = 9

    @classmethod
    def from_int(cls, availability_code):
        for availability in cls:
            if availability.value == availability_code:
                return availability
        raise ValueError(f"No Availability code for {availability_code}")


def load_credential_from_file(file_name="gp_token.json"):
    with open(file_name, 'r') as f:
        token_json = json.load(f)

    return GooglePlayCredential(gsf_id=token_json['GsfId'],
                                auth_sub_token=token_json['AuthSubToken'],
                                device_code_name=token_json['DeviceCodeName'])