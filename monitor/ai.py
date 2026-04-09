import aiohttp
from config import AITUNNEL_API_KEY, AITUNNEL_BASE_URL, AI_MODEL

SYSTEM_PROMPT = """Ты — эксперт по китайскому праву и ВЭД. Ты помогаешь российским предпринимателям решать проблемы с китайскими партнёрами.

Человек написал на форуме/в чате:
"{post_text}"

Напиши экспертный комментарий (3-5 предложений):
1. Кратко квалифицируй ситуацию по ГК КНР (укажи конкретную статью)
2. Дай практическую рекомендацию
3. Заверши фразой: "Для детальной проверки вашей ситуации — @chinaguard_bot"

Тон: профессиональный, уверенный, без воды. Не используй эмодзи. Пиши на русском."""


async def generate_draft(post_text: str) -> str:
    prompt = SYSTEM_PROMPT.replace("{post_text}", post_text[:1000])

    headers = {
        "Authorization": f"Bearer {AITUNNEL_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": AI_MODEL,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": post_text[:1000]},
        ],
        "max_tokens": 500,
        "temperature": 0.7,
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{AITUNNEL_BASE_URL}/chat/completions",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as resp:
                if resp.status != 200:
                    error = await resp.text()
                    return f"[Ошибка AI: {resp.status}] {error[:200]}"
                data = await resp.json()
                return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[Ошибка AI: {e}]"
