
import re

BLOCK_ORDER = ("personal_numbers", "general", "recommendations")

EMPTY_ANSWER = "지금은 답변을 만들지 못했습니다. 잠시 후 다시 시도해 주세요."

UNITS = ("mg/dL", "mmHg", "mmol/L", "kg/m²", "kg", "cm")

def merge(results: list) -> str:
    ordered = sorted(
        results,
        key=lambda r: BLOCK_ORDER.index(r.metadata.get("block_type", "general"))
        if r.metadata.get("block_type", "general") in BLOCK_ORDER
        else len(BLOCK_ORDER),
    )
    return "\n\n".join(r.text.strip() for r in ordered if r.text.strip())

def _strip_headers(text: str) -> str:
    return re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)

def _space_units(text: str) -> str:
    pattern = r"(\d)\s*(" + "|".join(re.escape(u) for u in UNITS) + r")\b"
    return re.sub(pattern, r"\1 \2", text)

def _soften_assertions(text: str) -> str:
    return re.sub(r"(반드시|무조건|확실히)\s*(진단|처방|치료)", r"전문의 상담을 통해 \2", text)


def guard(text: str) -> str:
    text = _strip_headers(text)
    text = _space_units(text)
    text = _soften_assertions(text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text or EMPTY_ANSWER