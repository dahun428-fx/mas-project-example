
import re

NO_DATA_ANSWER = "말씀하신 연도의 검진 기록이 없어 답변드리기 어렵습니다. 보유한 검진 연도는 {years} 입니다."


def find_unknown_years(text: str, allowed: list[str]) -> list[str]:
    mentioned = set(re.findall(r"(20\d{2})\s*년", text))
    return sorted(mentioned - set(allowed))


def guard_years(text: str, allowed: list[str]) -> tuple[str, list[str]]:
    unknown = find_unknown_years(text, allowed)
    if not unknown:
        return text, []
    return NO_DATA_ANSWER.format(years=", ".join(sorted(allowed, reverse=True))), unknown
