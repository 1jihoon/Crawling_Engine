import re
from bs4 import BeautifulSoup

def _clean(s: str | None) -> str:
    return re.sub(r"\s+", " ", s or "").strip()

def sanitize_text(txt: str) -> str:
    """
    텍스트 내부에 HTML 태그가 잔존할 경우 제거 (lxml 파서 활용)
    리눅스 환경에서의 데이터 오염을 원천 차단합니다.
    """
    if not txt: 
        return ""
    
    # <p, <br, <span 등 태그 기호가 보인다면 한 번 더 파싱하여 텍스트만 추출
    if "<" in txt and ">" in txt:
        try:
            # lxml을 사용하여 가장 강력하게 정화
            txt = BeautifulSoup(txt, "lxml").get_text(" ", strip=True)
        except Exception:
            # 혹시 모를 에러 발생 시 기본 bs4 파서로 fallback
            txt = BeautifulSoup(txt, "lxml").get_text(" ", strip=True)
            
    return _clean(txt)

def _as_list(x):
    if x is None: return []
    if isinstance(x, list): return x
    if isinstance(x, dict): return [x]
    return []

def _is_nonempty(x): return x not in (None, "", [], {})

def _coerce_images(v) -> list[str]:
    if v is None: return []
    if isinstance(v, str):
        v = v.strip()
        return [v] if v else []
    if isinstance(v, list):
        out = []
        for it in v:
            if isinstance(it, str) and it.strip():
                out.append(it.strip())
        return out
    return []

def _tuple_images(v) -> tuple[str, ...]:
    if not v: return ()
    if isinstance(v, list):
        return tuple([s.strip() for s in v if isinstance(s, str) and s.strip()])
    if isinstance(v, str):
        s = v.strip()
        return (s,) if s else ()
    return ()


def _prune(obj):
    """재귀적으로 None/''/[]/{ } 제거."""
    if isinstance(obj, dict):
        cleaned = {}
        for k, v in obj.items():
            pv = _prune(v)
            if pv not in (None, "", [], {}):
                cleaned[k] = pv
        return cleaned
    if isinstance(obj, list):
        arr = [_prune(v) for v in obj]
        return [v for v in arr if v not in (None, "", [], {})]
    return obj

