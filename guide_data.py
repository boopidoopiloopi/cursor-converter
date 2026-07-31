#!/usr/bin/env python3
from translations import get_lang

CURSOR_GUIDE_DATA = {
    'en': {
        "Alternate (Alternate Select)": (
            "Appearance: Typically a bold arrow pointing straight up.\n"
            "When it appears: Rarely used in everyday browsing; appears in specific programs when selecting whole columns of text or executing specialized modifier actions."
        ),
        "Busy (Wait)": (
            "Appearance: A spinning blue circle, hourglass, or beach ball.\n"
            "When it appears: When a program or system is fully occupied processing a heavy task."
        ),
        "Cross (Precision Select / Crosshair)": (
            "Appearance: Simple cross sign (+), sometimes with a center dot.\n"
            "When it appears: When precise clicking is needed (graphic design, cropping, aiming)."
        ),
        "Default (Normal Select)": (
            "Appearance: Standard diagonal arrow pointing up-left.\n"
            "When it appears: Standard navigation over desktop and desktop UI."
        ),
        "Dgn1 (Diagonal Resize 1)": (
            "Appearance: Diagonal double-ended arrow (Top-Left to Bottom-Right).\n"
            "When it appears: Hovering over top-left or bottom-right window corners."
        ),
        "Dgn2 (Diagonal Resize 2)": (
            "Appearance: Diagonal double-ended arrow (Bottom-Left to Top-Right).\n"
            "When it appears: Hovering over bottom-left or top-right window corners."
        ),
        "Hand (Grab / Panning)": (
            "Appearance: Open flat hand or closed fist.\n"
            "When it appears: Click and drag to move view (panning maps or large documents)."
        ),
        "Help (Help Select)": (
            "Appearance: Standard arrow with a question mark.\n"
            "When it appears: When triggering 'What's this?' context help."
        ),
        "Horizontal (Horizontal Resize)": (
            "Appearance: Double-ended arrow pointing left and right.\n"
            "When it appears: Hovering over left/right window edges to stretch width."
        ),
        "Link (Link Select)": (
            "Appearance: Hand with index finger pointing up.\n"
            "When it appears: Hovering over clickable hyperlinks, images, or buttons."
        ),
        "Move (Size All)": (
            "Appearance: Four-way arrow pointing up, down, left, and right.\n"
            "When it appears: Dragging objects or window title bars."
        ),
        "Text (Text Select / I-Beam)": (
            "Appearance: Capital letter 'I' with tiny crossbars.\n"
            "When it appears: Hovering over editable or selectable text."
        ),
        "Unavailable (Not Allowed / No)": (
            "Appearance: Circle with a diagonal slash.\n"
            "When it appears: Drag-and-drop targets that do not accept files."
        ),
        "Vertical (Vertical Resize)": (
            "Appearance: Double-ended arrow pointing straight up and down.\n"
            "When it appears: Hovering over top/bottom window edges."
        ),
        "Work (Working in Background)": (
            "Appearance: Standard arrow with small spinning circle.\n"
            "When it appears: Background task processing while system remains interactive."
        )
    },
    'ru': {
        "Alternate (Выбор альтернативного режима)": (
            "Внешний вид: Обычно жирная стрелка, направленная прямо вверх.\n"
            "Когда появляется: Редко используется при обычном просмотре; появляется в специальных программах при выделении столбцов текста или выполнении особых действий."
        ),
        "Busy (Ожидание)": (
            "Внешний вид: Вращающийся синий круг или песочные часы.\n"
            "Когда появляется: Когда программа или система полностью занята обработкой ресурсоемкой задачи."
        ),
        "Cross (Точный выбор / Крестик)": (
            "Внешний вид: Простой крестик (+), иногда с точкой в центре.\n"
            "Когда появляется: Когда требуется точный клик (графические редакторы, обрезка, прицеливание в играх)."
        ),
        "Default (Основной выбор)": (
            "Внешний вид: Стандартная диагональная стрелка, указывающая вверх и влево.\n"
            "Когда появляется: Отображается большую часть времени при навигации по ОС и рабочему столу."
        ),
        "Dgn1 (Диагональное изменение 1)": (
            "Внешний вид: Диагональная двусторонняя стрелка (сверху-слева вниз-вправо).\n"
            "Когда появляется: При наведении на верхний левый или нижний правый угол окна."
        ),
        "Dgn2 (Диагональное изменение 2)": (
            "Внешний вид: Диагональная двусторонняя стрелка (снизу-слева вверх-вправо).\n"
            "Когда появляется: При наведении на нижний левый или верхний правый угол окна."
        ),
        "Hand (Перемещение / Рука)": (
            "Внешний вид: Открытая ладонь или сжатый кулак.\n"
            "Когда появляется: При нажатии и перетаскивании для перемещения вида (панорамирование карт или просмотр документов)."
        ),
        "Help (Выбор справки)": (
            "Внешний вид: Стандартная стрелка с вопросительным знаком рядом.\n"
            "Когда появляется: При вызове режима контекстной справки 'Что это?'."
        ),
        "Horizontal (Горизонтальное изменение)": (
            "Внешний вид: Двусторонняя стрелка влево-вправо.\n"
            "Когда появляется: При наведении на левую или правую границу окна."
        ),
        "Link (Выбор ссылки)": (
            "Внешний вид: Рука с поднятым указательным пальцем.\n"
            "Когда появляется: При наведении на кликабельные ссылки, изображения или кнопки."
        ),
        "Move (Перемещение объекта)": (
            "Внешний вид: Четырехнаправленная стрелка (вверх, вниз, влево, вправо).\n"
            "Когда появляется: При перетаскивании объектов или окон за заголовок."
        ),
        "Text (Выбор текста / Курсор I-Beam)": (
            "Внешний вид: В виде заглавной буквы 'I' с засечками.\n"
            "Когда появляется: При наведении на текст, доступный для выделения или редактирования."
        ),
        "Unavailable (Недоступно)": (
            "Внешний вид: Перечеркнутый круг.\n"
            "Когда появляется: При перетаскивании объекта в область, где действие запрещено."
        ),
        "Vertical (Вертикальное изменение)": (
            "Внешний вид: Двусторонняя стрелка вверх-вниз.\n"
            "Когда появляется: При наведении на верхнюю или нижнюю границу окна."
        ),
        "Work (Фоновый режим)": (
            "Внешний вид: Стандартная стрелка с вращающимся кругом рядом.\n"
            "Когда появляется: Когда система загружает что-то в фоне, но пользователь может продолжать работу."
        )
    }
}

def get_current_guide_data():
    lang = get_lang()
    return CURSOR_GUIDE_DATA.get(lang, CURSOR_GUIDE_DATA['en'])
