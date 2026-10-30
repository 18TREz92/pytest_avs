import uuid
import random
import rstr
from typing import Any, get_type_hints, Annotated, get_origin, get_args
from src.main.api.generators.creation_rule import CreationRule


class RandomModelGenerator:
    @staticmethod
    def generate(cls: type) -> Any:
        type_hints = get_type_hints(cls, include_extras=True)
        init_data = {}

        for field_name, annotated_type in type_hints.items():
            rule = None
            actual_type = annotated_type

            if get_origin(annotated_type) is Annotated:
                actual_type, *annotations = get_args(annotated_type)
                for ann in annotations:
                    if isinstance(ann, CreationRule):
                        rule = ann

            if rule:
                value = RandomModelGenerator._generate_from_regex(rule.regex, actual_type)
            else:
                value = RandomModelGenerator._generate_value(actual_type)

            init_data[field_name] = value
        return cls(**init_data)

    @staticmethod
    def _generate_from_regex(regex: str, field_type: type) -> Any:
        generated = rstr.xeger(regex)
        if field_type is int:
            return int(generated)
        if field_type is float:
            return float(generated)
        return generated

    @staticmethod
    def _generate_value(field_type: type) -> Any:
        if field_type is str:
            return str(uuid.uuid4())[:8]
        elif field_type is int:
            return random.randint(1, 9999)
        elif field_type is float:
            return round(random.uniform(0, 100), 2)
        elif field_type is bool:
            return random.choice([True, False])
        elif field_type is list:
            return [str(uuid.uuid4())[:5]]
        elif isinstance(field_type, type):
            return RandomModelGenerator.generate(field_type)
        return None

    @staticmethod
    def generate_deposit_amount(min_amount: int = 1000) -> int:
        return random.randint(min_amount, 9000)

    @staticmethod
    def generate_transfer_amount(available_balance: float) -> int:
        return random.randint(500, min(10000, int(available_balance)))

    @staticmethod
    def generate_deposit_amount_for_transfer() -> int:
        return random.randint(6000, 9000)

    @staticmethod
    def generate_credit_amount() -> int:
        return random.randint(5000, 15000)

    @staticmethod
    def generate_credit_term_months() -> int:
        return random.randint(1, 60)

    @staticmethod
    def generate_partial_repay_amount(credit_amount: float) -> int:
        return random.randint(1, int(credit_amount) - 1)