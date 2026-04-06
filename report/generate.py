"""ChinaGuard — PDF report generator.

Uses Jinja2 for template rendering and WeasyPrint for PDF output.
"""

from __future__ import annotations

import os
from pathlib import Path

from jinja2 import Environment, FileSystemLoader


TEMPLATE_DIR = Path(__file__).resolve().parent


def generate_report(
    report_type: str,
    report_number: str,
    subject: str,
    doc_type: str,
    description: str,
    risks: list[dict],
    comparisons: list[dict],
    recommendations: list[str],
    output_path: str | Path,
    date: str | None = None,
) -> Path:
    """Render an HTML report and convert it to PDF.

    Parameters
    ----------
    report_type : str
        E.g. "Отчёт о проверке договора" or "Анализ правовой ситуации".
    report_number : str
        Unique report identifier.
    subject : str
        Subject of the review.
    doc_type : str
        Document type being reviewed.
    description : str
        Brief description of the subject.
    risks : list[dict]
        Each dict: title, level (high/medium/low), level_label, article,
        description, recommendation.
    comparisons : list[dict]
        Each dict: topic, china, russia, conclusion.
    recommendations : list[str]
        List of recommendation strings.
    output_path : str | Path
        Destination path for the generated PDF.
    date : str | None
        Report date string. Defaults to today.

    Returns
    -------
    Path
        Absolute path to the generated PDF file.
    """
    from weasyprint import HTML  # imported here to keep module importable without weasyprint

    if date is None:
        from datetime import datetime
        date = datetime.now().strftime("%d.%m.%Y")

    output_path = Path(output_path).resolve()

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        autoescape=True,
    )
    template = env.get_template("template.html")

    html_string = template.render(
        report_type=report_type,
        report_number=report_number,
        date=date,
        subject=subject,
        doc_type=doc_type,
        description=description,
        risks=risks,
        comparisons=comparisons,
        recommendations=recommendations,
    )

    HTML(
        string=html_string,
        base_url=str(TEMPLATE_DIR),
    ).write_pdf(str(output_path))

    return output_path


# ── Test data & CLI entry point ──────────────────────────────────────────────

if __name__ == "__main__":
    test_risks = [
        {
            "title": "Отсутствие арбитражной оговорки",
            "level": "high",
            "level_label": "Высокий",
            "article": "Ст. 271–272 Гражданского процессуального кодекса КНР",
            "description": (
                "В договоре не указан порядок разрешения споров. "
                "Без арбитражной оговорки спор будет рассматриваться "
                "в китайском суде по месту нахождения ответчика, что "
                "существенно снижает шансы российской стороны на "
                "благоприятный исход."
            ),
            "recommendation": (
                "Добавить арбитражную оговорку с указанием CIETAC "
                "(Китайская международная экономическая и торговая "
                "арбитражная комиссия) или ICC в качестве арбитражного "
                "института."
            ),
        },
        {
            "title": "Нечёткие требования к качеству товара",
            "level": "medium",
            "level_label": "Средний",
            "article": "Ст. 615–617 Гражданского кодекса РФ",
            "description": (
                "Спецификация качества товара описана общими фразами "
                "без ссылок на конкретные стандарты (GB, ГОСТ). "
                "Это затрудняет предъявление претензий при поставке "
                "некачественного товара."
            ),
            "recommendation": (
                "Указать конкретные стандарты качества (GB/T для Китая, "
                "ГОСТ Р для России), допустимые отклонения и порядок "
                "проведения входного контроля."
            ),
        },
    ]

    test_comparisons = [
        {
            "topic": "Сроки исковой давности",
            "china": (
                "Общий срок — 3 года (ст. 188 ГК КНР). "
                "Для международной купли-продажи — 4 года (Венская конвенция)."
            ),
            "russia": (
                "Общий срок — 3 года (ст. 196 ГК РФ). "
                "Максимальный срок — 10 лет с момента нарушения."
            ),
            "conclusion": (
                "Сроки сопоставимы. Рекомендуется зафиксировать "
                "применимое право в договоре для определённости."
            ),
        },
    ]

    test_recommendations = [
        "Включить арбитражную оговорку с указанием CIETAC или ICC.",
        "Детализировать спецификацию качества со ссылками на стандарты GB/T и ГОСТ Р.",
        "Предусмотреть инспекцию товара до отгрузки (pre-shipment inspection) силами независимой организации.",
    ]

    output = generate_report(
        report_type="Отчёт о проверке договора",
        report_number="CG-2026-0042",
        subject="Договор поставки электроники Shenzhen HiTech Co. → ООО «Импорт-Трейд»",
        doc_type="Договор международной купли-продажи товаров",
        description=(
            "Договор на поставку партии электронных компонентов "
            "из Шэньчжэня (КНР) в Москву (РФ) на сумму $120 000."
        ),
        risks=test_risks,
        comparisons=test_comparisons,
        recommendations=test_recommendations,
        output_path="test_report.pdf",
        date="06.04.2026",
    )

    print(f"Report generated: {output}")
