#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''SelectX - easy eXtendable text editor for developers writed on Python. Licensed by GPL3.'''
#!/usr/bin/python -m cProfile -s time ./selectx.py |less -o ./pof.log     #<<<<profiler run
import sys, os, re, encodings
import ast, getopt, struct, array
import codecs

import gettext, locale

    
from os.path import expanduser
__baseDir__ = expanduser('~')

__version__ = '''0.7.1.22'''

#msgmerge ./locale/ru_UA/LC_MESSAGES/SelectX.po ./messages.pot     #<<<<po merge
#python setup.py sdist upload        #<<<<pypi upload


    
def gluePath(elementsList):
    '''gluePath(elementsList) - glue path from elementsList and create if not 
    exist'''
    newPath = os.path.sep.join(elementsList)
    if not os.path.isdir(newPath):
        os.makedirs(newPath)
    return newPath

def writeStringToFile(fileName, writeString):
    fileN = open(fileName, "w")
    fileN.write(writeString)
    fileN.close()
    return True
    

def writeIfNotSame(fileName, writeString):
    if os.path.isfile(fileName):
        if os.path.getsize(fileName)<>len(writeString):
            fff1 = open(fileName, "r")
            sssfff = fff1.read()
            fff1.close()
            if sssfff<>writeString:
                fff = open(fileName, "w")
                writeStringToFile(fileName, writeString)
                fff.close()
                return True
            else:
                #fff.close()
                return False
        #else:
            #print 'not write - same text'
            #print 'not write - same size'
    else:
        writeStringToFile(fileName, writeString)
        return True
    return False


def localGettextX():
    po_dict = {'ru': r'''# SelectX.
# Copyright (C) 2014 10
# This file is distributed under the same license as the PACKAGE package (GPL3).
# 10 <1_0@usa.com>, 2014.
msgid ""
msgstr ""
"Project-Id-Version: SelectX 0.6.2.16\n"
"Report-Msgid-Bugs-To: \n"
"POT-Creation-Date: 2014-12-22 16:22+0200\n"
"PO-Revision-Date: 2014-12-22 16:28+0300\n"
"Last-Translator: 10 <1_0@usa.com>\n"
"Language-Team: 10\n"
"Language: ru\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8bit\n"
"Plural-Forms: nplurals=3; plural=(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n"
"%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2);\n"
"X-Generator: Poedit 1.5.4\n"
"X-Poedit-SourceCharset: UTF-8\n"

#: selectx.py:848
msgid ""
"Try to use PyQt4\n"
"(license - http://www.riverbankcomputing.co.uk/software/pyqt/license )\n"
"instead of PySide\n"
"(license - LGPL - http://www.gnu.org/copyleft/lesser.html )"
msgstr ""
"Попытка использовать PyQt4\n"
"(лицензия - http://www.riverbankcomputing.co.uk/software/pyqt/license )\n"
"вместо PySide\n"
"(лицензия - LGPL - http://www.gnu.org/copyleft/lesser.html )"

#: selectx.py:860
msgid ""
"Keypresses:  Action:\n"
"Backspace  Deletes the character to the left of the cursor.\n"
"Delete     Deletes the character to the right of the cursor.\n"
"Ctrl+C     Copy the selected text to the clipboard.\n"
"Ctrl+Insert    Copy the selected text to the clipboard.\n"
"Ctrl+K     Deletes to the end of the line.\n"
"Ctrl+V     Pastes the clipboard text into text edit.\n"
"Shift+Insert   Pastes the clipboard text into text edit.\n"
"Ctrl+X     Deletes the selected text and copies it to the clipboard.\n"
"Shift+Delete   Deletes the selected text and copies it to the clipboard.\n"
"Ctrl+Z     Undoes the last operation.\n"
"Ctrl+Y     Redoes the last operation.\n"
"LeftArrow  Moves the cursor one character to the left.\n"
"Ctrl+LeftArrow     Moves the cursor one word to the left.\n"
"RightArrow     Moves the cursor one character to the right.\n"
"Ctrl+RightArrow    Moves the cursor one word to the right.\n"
"UpArrow    Moves the cursor one line up.\n"
"Ctrl+UpArrow   Moves the cursor one word up.\n"
"DownArrow  Moves the cursor one line down.\n"
"Ctrl+Down Arrow    Moves the cursor one word down.\n"
"PageUp     Moves the cursor one page up.\n"
"PageDown   Moves the cursor one page down.\n"
"Home   Moves the cursor to the beginning of the line.\n"
"Ctrl+Home  Moves the cursor to the beginning of the text.\n"
"End    Moves the cursor to the end of the line.\n"
"Ctrl+End   Moves the cursor to the end of the text.\n"
"Alt+Wheel  Scrolls the page horizontally (the Wheel is the mouse wheel).\n"
"Ctrl+Wheel     Zooms the text."
msgstr ""
"Нажатая клавиша:  Действие:\n"
"Backspace  Удаляет символ слева от курсора.\n"
"Delete     Удаляет символ справа от курсора.\n"
"Ctrl+C     Копирует выбранный текст в буфер обмена.\n"
"Ctrl+Insert    Копирует выбранный текст в буфер обмена.\n"
"Ctrl+K     Удаляет до конца строки.\n"
"Ctrl+V     Вставляет текст в текстовый редактор.\n"
"Shift+Insert   Вставляет текст в текстовый редактор.\n"
"Ctrl+X     Удаляет выбранный текст и копирует его в буфер обмена.\n"
"Shift+Delete   Удаляет выбранный текст и копирует его в буфер обмена.\n"
"Ctrl+Z     Отменяет последнее действие.\n"
"Ctrl+Y     Выполняет последнее действие.\n"
"СтрелкаВлево  Передвигает курсор на один символ влево.\n"
"Ctrl+СтрелкаВлево     Передвигает курсор на одно слово влево.\n"
"СтрелкаВправо     Передвигает курсор на один символ вправо.\n"
"Ctrl+СтрелкаВправо    Передвигает курсор на одно слово вправо.\n"
"СтрелкаВверх    Передвигает курсор на одну строку вверх.\n"
"Ctrl+СтрелкаВверх   Передвигает курсор на одно слово вверх.\n"
"СтрелкаВниз  Передвигает курсор на одну строку вниз.\n"
"Ctrl+СтрелкаВниз   Передвигает курсор на одно слово вниз.\n"
"PageUp     Передвигает курсор на одну страницу вверх.\n"
"PageDown   Передвигает курсор на одну страницу вниз.\n"
"Home   Передвигает курсор в начало строки.\n"
"Ctrl+Home  Передвигает курсор в начало текста.\n"
"End    Передвигает курсор в конец строки.\n"
"Ctrl+End   Передвигает курсор в конец текста.\n"
"Alt+Колесо  Прокручивает страницу горизонтально (Колесо - колесо мышки).\n"
"Ctrl+Колесо     Масштабирует текст."

#: selectx.py:889
msgid ""
"\n"
"[KEY]...[FILE]\n"
"Keys:\n"
"--ForceEmbededIcons         Use embeded icons theme\n"
"-h, --help                  Print this help message\n"
"--version                   Print version info\n"
msgstr ""
"\n"
"[КЛЮЧ]...[ФАЙЛ]\n"
"Ключи:\n"
"--ForceEmbededIcons         Использовать встроенную тему иконок\n"
"-h, --help                  Вывести это сообщение помощь\n"
"--version                  Вывести информацию о версии\n"

#: selectx.py:897 selectx.py:1745
#, python-format
msgid "SelectX. Text editor licensed by GPL3. Ver. %s"
msgstr "SelectX. Текстовый редактор лицензированный по GPL3. Версия %s."

#: selectx.py:1036
#, python-format
msgid "Try Open This File -> %s"
msgstr "Попытка открыть этот файл -> %s"

#: selectx.py:1039
msgid "Too many args"
msgstr "Слишком много параметров"

#: selectx.py:1057 selectx.py:1313
msgid "SelectX"
msgstr "SelectX"

#: selectx.py:1063 selectx.py:1312
msgid "New Text"
msgstr "Новый текст"

#: selectx.py:1093
msgid "File"
msgstr "Файл"

#: selectx.py:1096
msgid "&File"
msgstr "&Файл"

#: selectx.py:1099
msgid "New Tab"
msgstr "Новая вкладка"

#: selectx.py:1099
msgid "Create new tab"
msgstr "Создать новую вкладку"

#: selectx.py:1103
msgid "Open"
msgstr "Открыть"

#: selectx.py:1103
msgid "Open a file"
msgstr "Открыть файл"

#: selectx.py:1105
msgid "Save"
msgstr "Сохранить"

#: selectx.py:1105
msgid "Save current file"
msgstr "Сохранить текущий файл"

#: selectx.py:1107
msgid "Save As..."
msgstr "Сохранить как..."

#: selectx.py:1107
msgid "Save as new file"
msgstr "Сохранить как новый файл"

#: selectx.py:1110
msgid "Preview"
msgstr "Предпросмотр"

#: selectx.py:1110
msgid "File Preview"
msgstr "Предпросмотр файла"

#: selectx.py:1112
msgid "Print"
msgstr "Печать"

#: selectx.py:1112
msgid "File Print"
msgstr "Пачать файла"

#: selectx.py:1115
msgid "Close Tab"
msgstr "Закрыть вкладку"

#: selectx.py:1115
msgid "Close current tab"
msgstr "Закрыть текущую вкладку"

#: selectx.py:1117
msgid "Exit"
msgstr "Выход"

#: selectx.py:1117
msgid "Exit SelectX"
msgstr "Выйти из SelectX"

#: selectx.py:1120
msgid "Edit"
msgstr "Редактировать"

#: selectx.py:1122
msgid "&Edit"
msgstr "&Редактировать"

#: selectx.py:1123
msgid "Undo"
msgstr "Отменить"

#: selectx.py:1123
msgid "Undo last text edit"
msgstr "Отменить последнюю правку текста"

#: selectx.py:1125
msgid "Redo"
msgstr "Вернуть"

#: selectx.py:1125
msgid "Redo last text edit"
msgstr "Вернуть последнюю отмену правки текста"

#: selectx.py:1128
msgid "Copy"
msgstr "Копировать"

#: selectx.py:1128
msgid "Copy selected text"
msgstr "Копировать выделенный текст"

#: selectx.py:1130
msgid "Cut"
msgstr "Вырезать"

#: selectx.py:1130
msgid "Cut selected text"
msgstr "Вырезать выделенный текст"

#: selectx.py:1132
msgid "Paste"
msgstr "Вставить"

#: selectx.py:1132
msgid "Paste text"
msgstr "Вставить текст"

#: selectx.py:1137
msgid "Find and replace"
msgstr "Найти и заменить"

#: selectx.py:1137
msgid "Find and replace words in your document"
msgstr "Найти и заменить слова в Вашем документе"

#: selectx.py:1140
msgid "Select"
msgstr "Выбрать"

#: selectx.py:1142
msgid "&Select"
msgstr "Вы&брать"

#: selectx.py:1143
msgid "Select All"
msgstr "Выбрать всё"

#: selectx.py:1143
msgid "Select all text in editor"
msgstr "Выбрать весь текст в редакторе"

#: selectx.py:1145
msgid "Select For Copy By Words"
msgstr "Выбор для копирования по-словам"

#: selectx.py:1145
msgid "Set Select For Copy By Words"
msgstr "Задать выбор для копирования по-словам"

#: selectx.py:1148
msgid "View"
msgstr "Вид"

#: selectx.py:1150
msgid "&View"
msgstr "&Вид"

#: selectx.py:1153
msgid "&Highlighter"
msgstr "&Подсветка синтаксиса"

#: selectx.py:1156
msgid "None"
msgstr "Отсутствует"

#: selectx.py:1156
msgid "None Highlighter"
msgstr "Отсутствует подсветка синтаксиса"

#: selectx.py:1159
msgid "Cpp"
msgstr "С++"

#: selectx.py:1159
msgid "Cpp Highlighter"
msgstr "Подсветка синтаксиса С++"

#: selectx.py:1162
msgid "Python"
msgstr "Python"

#: selectx.py:1162
msgid "Python Highlighter"
msgstr "Подсветка синтаксиса Python"

#: selectx.py:1167
msgid "&Zoom"
msgstr "&Масштаб"

#: selectx.py:1169
msgid "Zoom In"
msgstr "Увеличить масштаб"

#: selectx.py:1169
msgid "Zoom In text in editor"
msgstr "Увеличить масштаб текста в редакторе"

#: selectx.py:1171
msgid "Zoom Out"
msgstr "Уменьшить масштаб"

#: selectx.py:1171
msgid "Zoom Out text in editor"
msgstr "Уменьшить масштаб текста в редакторе"

#: selectx.py:1173
msgid "Zoom Original"
msgstr "Начальный масштаб"

#: selectx.py:1173
msgid "Zoom original text in editor"
msgstr "Начальный масштаб текста в редакторе"

#: selectx.py:1176
msgid "Font"
msgstr "Шрифт"

#: selectx.py:1176
msgid "Font select dialog"
msgstr "Диалог выбора шрифта"

#: selectx.py:1179
msgid "Show/Hide non-printabale"
msgstr "Отобразить/спрятать непечатаемые"

#: selectx.py:1179
msgid "Show/Hide non-printabale symbols"
msgstr "Отобразить/спрятать непечатаемые символы"

#: selectx.py:1181
msgid "Pythonic Enter"
msgstr "\"Pythonic\" новой строки"

#: selectx.py:1181
msgid "On/Off Pythonic Enter Style"
msgstr "Включить/выключить \"Pythonic\" стиль новой строки"

#: selectx.py:1183
msgid "Line Numbers"
msgstr "Номерация строк"

#: selectx.py:1183
msgid "On/Off PLine Numbers"
msgstr "Включить/Выключить номерацию строк"

#: selectx.py:1186 selectx.py:1189
msgid "Help"
msgstr "Помощь"

#: selectx.py:1188
msgid "&Help"
msgstr "&Помощь"

#: selectx.py:1189
msgid "Keys Help"
msgstr "Помощь по клавишам"

#: selectx.py:1191
msgid "About"
msgstr "О программе"

#: selectx.py:1191
msgid "About editor"
msgstr "О редакторе"

#: selectx.py:1193
msgid "About &Qt"
msgstr "О версии &Qt"

#: selectx.py:1193
msgid "About current QT"
msgstr "О текущей версии QT"

#: selectx.py:1195
msgid "Ok Player"
msgstr "Ok проигрыватель"

#: selectx.py:1195
msgid "On/Off Ok Player"
msgstr "Включить/выключить Ok проигрыватель"

#: selectx.py:1199
msgid "Ok Volume"
msgstr "Ok громкость"

#: selectx.py:1199
msgid "Volume Ok Player"
msgstr "Громкость Ok проигрывателя"

#: selectx.py:1257
msgid "Hide Py Enter"
msgstr "Выключить \"Pythonic\" новые строки"

#: selectx.py:1260
msgid "Add Py Enter"
msgstr "Включить \"Pythonic\" новые строки"

#: selectx.py:1319
#, python-format
msgid "New text - %s"
msgstr "Новый текст - %s"

#: selectx.py:1354
#, python-format
msgid "Selected Tab #%s"
msgstr "Выбрана вкладка №%s"

#: selectx.py:1376 selectx.py:1406 selectx.py:1417
#, python-format
msgid "Save Text: %s"
msgstr "Сохранение текста: %s"

#: selectx.py:1387
msgid "Save File"
msgstr "Сохранение файла"

#: selectx.py:1397 selectx.py:1426
msgid "Stop Save Text"
msgstr "Прекращено сохранение текста"

#: selectx.py:1418 selectx.py:1516
#, python-format
msgid "SelectX - %s"
msgstr "SelectX - %s"

#: selectx.py:1437
msgid "Open File"
msgstr "Открыть файл"

#: selectx.py:1439
msgid ""
"All Files (*);;Text Files (*.txt *.log *.TXT *.LOG);;Python Files (*.py *.PY "
"*.py3 *.PY3);;C/C++ Files (*.c *.cc *.cpp *.c++ *.cxx *.h *.hh *.hpp *.hxx *."
"CPP *.H *.c *.C)"
msgstr ""
"Все файлы (*);;Текстовые файлы (*.txt *.log *.TXT *.LOG);;Python файлы (*.py "
"*.PY *.py3 *.PY3);;C/C++ файлы(*.c *.cc *.cpp *.c++ *.cxx *.h *.hh *.hpp *."
"hxx *.CPP *.H *.c *.C)"

#: selectx.py:1450 selectx.py:1476
#, python-format
msgid "Start reading: %s"
msgstr "Начато чтение: %s"

#: selectx.py:1455
msgid "Stop Open Text"
msgstr "Прекращено открытие текста"

#: selectx.py:1511
#, python-format
msgid "Open Text: %s"
msgstr "Открыть текст: %s"

#: selectx.py:1535
msgid "Confirm Exit SelectX"
msgstr "Подтвердить выход из SelectX"

#: selectx.py:1536
msgid "Are you sure to Exit?"
msgstr "Вы уверенны, что хотите выйти?"

#: selectx.py:1540
msgid "Close Stoped"
msgstr "Закрытие прекращено"

#: selectx.py:1543
msgid "Confirm Close Tab"
msgstr "Подтвердите закрытие вкладки"

#: selectx.py:1544
msgid "Are you sure to Close Tab?"
msgstr "Вы уверенны, что хотите закрыть вкладку?"

#: selectx.py:1552
msgid "Undo Text"
msgstr "Отмена текста"

#: selectx.py:1556
msgid "Redo Text"
msgstr "Возврат текста"

#: selectx.py:1561
msgid "Enter words number"
msgstr "Введите число слов"

#: selectx.py:1561
msgid "Enter words number for copy:"
msgstr "Введите число слов для копирования"

#: selectx.py:1623
msgid "Copy Text"
msgstr "Копирование текста"

#: selectx.py:1627
msgid "Cut Text"
msgstr "Вырезание текста"

#: selectx.py:1631
msgid "Paste Text"
msgstr "Вставка текста"

#: selectx.py:1639
msgid "Hide Non Printabale"
msgstr "Спрятать непечатаемые"

#: selectx.py:1642
msgid "Show Non Printabale"
msgstr "Показать непечатаемые"

#: selectx.py:1649
msgid "Show Line Numbers"
msgstr "Показать номера линий"

#: selectx.py:1651
msgid "Hide Line Numbers"
msgstr "Спрятать номера линий"

#: selectx.py:1658
msgid "SelectX Find Dialog"
msgstr "SelectX Диалог поиска"

#: selectx.py:1658
msgid "Enter text to find:"
msgstr "Введите текст для поиска:"

#: selectx.py:1661
#, python-format
msgid "Found: %s"
msgstr "Найдено: %s"

#: selectx.py:1664
#, python-format
msgid "Not found: %s"
msgstr "Не найдено: %s"

#: selectx.py:1667
msgid "Find Canceled"
msgstr "Поиск отменен"

#: selectx.py:1683 selectx.py:1689 selectx.py:1695
#, python-format
msgid "Zoom Rate: %s"
msgstr "Коэффициент масштабирования: %s"

#: selectx.py:1713
msgid "Enter media URL"
msgstr "Введите URL мультимедиа"

#: selectx.py:1714
msgid "Enter you favorit on-line radio URL:"
msgstr "Введите URL Вашей любимой он-лайн радиостанции"

#: selectx.py:1737
#, python-format
msgid "okPlayer play: %s"
msgstr "okPlayer проигрывает: %s"

#: selectx.py:1741
msgid "okPlayer stop"
msgstr "okPlayer остановлен"

#: selectx.py:1744
msgid "About SelectX"
msgstr "О SelectX"

#: selectx.py:1753 selectx.py:2281
msgid "Ok"
msgstr "Ok"

#: selectx.py:1756
msgid "Keys SelectX"
msgstr "Клавиши SelectX"

#: selectx.py:1837
msgid "Symbols: {} | Rows: {} | Line: {} | Column: {} | Selected: {}"
msgstr "Символы: {} | Строки: {} | Строка: {} | Колонка: {} | Выбрано: {}"

#: selectx.py:1839
msgid "Symbols: {} | Rows: {} | Line: {} | Column: {}"
msgstr "Символы: {} | Строки: {} | Строка: {} | Колонка: {}"

#: selectx.py:2288
msgid "Set Ok"
msgstr "Установите Ok"

#: selectx.py:2307
msgid "Find"
msgstr "Найти"

#: selectx.py:2309
msgid "Replace"
msgstr "Заменить"

#: selectx.py:2311
msgid "Replace all"
msgstr "Заменить всё"

#: selectx.py:2313
msgid "Normal"
msgstr "Обычный"

#: selectx.py:2315
msgid "RegEx"
msgstr "RegEx"

#: selectx.py:2325
msgid "Options: "
msgstr "Параметры: "

#: selectx.py:2326
msgid "Case sensitive"
msgstr "Чувствительно к регистру"

#: selectx.py:2327
msgid "Whole words"
msgstr "Целое слово"

#: selectx.py:2351
msgid "Find and Replace"
msgstr "Найти и заменить"

'''}
    
    current_locale, encoding = locale.getdefaultlocale()
    #print 'current_locale, encoding '+str((current_locale, encoding ))
    poString = None
    if current_locale and current_locale.lower() in po_dict.keys():
        poString = po_dict[current_locale[:2]]
    elif current_locale and current_locale[:2].lower() in po_dict.keys():
        poString = po_dict[current_locale[:2]]
    else:
        return gettext.gettext
    baseDirLocale = gluePath([__baseDir__, '.config', 'SelectX', 'locale',''])
    #if poString and (not os.path.isfile(gluePath([__baseDir__, '.config', 'SelectX', 'locale', current_locale, 'LC_MESSAGES', '']))):
    if poString:
        baseDirPo = gluePath([__baseDir__, '.config', 'SelectX', 'locale', current_locale, 'LC_MESSAGES', ''])
        if writeIfNotSame(baseDirPo+'SelectX.po', poString) or not os.path.isfile(baseDirPo + 'SelectX.mo'):
            makeMo(baseDirPo + 'SelectX.po', baseDirPo + 'SelectX.mo', current_locale)
        t = gettext.translation('SelectX', baseDirLocale, fallback=True, languages=[current_locale])
    else:
        t = gettext.translation('SelectX', baseDirLocale, fallback=True, languages=[current_locale])
    return t.ugettext

def makeMo(filename, outfile, current_locale):
# based on msgfmt.py Written by Martin v. Löwis <loewis@informatik.hu-berlin.de>
    def addToMo(id, str, fuzzy, MESSAGES):
        "Add a non-fuzzy translation to the dictionary."
        if not fuzzy and str:
            MESSAGES[id] = str
            
    MESSAGES = {}
    ID = 1
    STR = 2
    if filename.endswith('.po'):
        infile = filename
    else:
        infile = filename + '.po'
    if outfile is None:
        outfile = os.path.splitext(infile)[0] + '.mo'
    try:
        lines = open(infile).readlines()
    except IOError, msg:
        print >> sys.stderr, msg
        sys.exit(1)
    section = None
    fuzzy = 0
    lno = 0
    for l in lines:
        lno += 1
        if l[0] == '#' and section == STR:
            addToMo(msgid, msgstr, fuzzy, MESSAGES)
            section = None
            fuzzy = 0
        if l[:2] == '#,' and 'fuzzy' in l:
            fuzzy = 1
        if l[0] == '#':
            continue
        if l.startswith('msgid') and not l.startswith('msgid_plural'):
            if section == STR:
                addToMo(msgid, msgstr, fuzzy, MESSAGES)
            section = ID
            l = l[5:]
            msgid = msgstr = ''
            is_plural = False
        elif l.startswith('msgid_plural'):
            if section != ID:
                print >> sys.stderr, 'msgid_plural not preceded by msgid on %s:%d' %\
                    (infile, lno)
                sys.exit(1)
            l = l[12:]
            msgid += '\0'
            is_plural = True
        elif l.startswith('msgstr'):
            section = STR
            if l.startswith('msgstr['):
                if not is_plural:
                    print >> sys.stderr, 'plural without msgid_plural on %s:%d' %\
                        (infile, lno)
                    sys.exit(1)
                l = l.split(']', 1)[1]
                if msgstr:
                    msgstr += '\0'
            else:
                if is_plural:
                    print >> sys.stderr, 'indexed msgstr required for plural on  %s:%d' %\
                        (infile, lno)
                    sys.exit(1)
                l = l[6:]
        l = l.strip()
        if not l:
            continue
        l = ast.literal_eval(l)
        if section == ID:
            msgid += l
        elif section == STR:
            msgstr += l
        else:
            print >> sys.stderr, 'Syntax error on %s:%d' % (infile, lno), \
                  'before:'
            print >> sys.stderr, l
            sys.exit(1)
    if section == STR:
        addToMo(msgid, msgstr, fuzzy, MESSAGES)
    keys = MESSAGES.keys()
    keys.sort()
    offsets = []
    ids = strs = ''
    for id in keys:
        offsets.append((len(ids), len(id), len(strs), len(MESSAGES[id])))
        ids += id + '\0'
        strs += MESSAGES[id] + '\0'
    output = ''
    keystart = 7*4+16*len(keys)
    valuestart = keystart + len(ids)
    koffsets = []
    voffsets = []
    for o1, l1, o2, l2 in offsets:
        koffsets += [l1, o1+keystart]
        voffsets += [l2, o2+valuestart]
    offsets = koffsets + voffsets
    output = struct.pack("Iiiiiii",
                         0x950412deL,
                         0,
                         len(keys),
                         7*4,
                         7*4+len(keys)*8,
                         0, 0)
    output += array.array("i", offsets).tostring()
    output += ids
    output += strs
    
    try:
        open(outfile,"wb").write(output)
    except IOError,msg:
        print >> sys.stderr, msg

_ = gettext.gettext
#_ = localGettextX()

#from PySide import QtGui, QtCore
#LIB_USE = "PySide"

try:
    from PySide import QtGui, QtCore
    LIB_USE = "PySide"
except ImportError:
    print _(u"""Try to use PyQt4
(license - http://www.riverbankcomputing.co.uk/software/pyqt/license )
instead of PySide
(license - LGPL - http://www.gnu.org/copyleft/lesser.html )""")
    from PyQt4 import QtGui, QtCore
    LIB_USE = "PyQt4"
#Phonon = None

#from PyQt4 import QtGui, QtCore #for use in tests
#LIB_USE = "PyQt4"


KEYS_HELP = _(u'''Keypresses:  Action:
Backspace  Deletes the character to the left of the cursor.
Delete     Deletes the character to the right of the cursor.
Ctrl+C     Copy the selected text to the clipboard.
Ctrl+Insert    Copy the selected text to the clipboard.
Ctrl+K     Deletes to the end of the line.
Ctrl+V     Pastes the clipboard text into text edit.
Shift+Insert   Pastes the clipboard text into text edit.
Ctrl+X     Deletes the selected text and copies it to the clipboard.
Shift+Delete   Deletes the selected text and copies it to the clipboard.
Ctrl+Z     Undoes the last operation.
Ctrl+Y     Redoes the last operation.
LeftArrow  Moves the cursor one character to the left.
Ctrl+LeftArrow     Moves the cursor one word to the left.
RightArrow     Moves the cursor one character to the right.
Ctrl+RightArrow    Moves the cursor one word to the right.
UpArrow    Moves the cursor one line up.
Ctrl+UpArrow   Moves the cursor one word up.
DownArrow  Moves the cursor one line down.
Ctrl+Down Arrow    Moves the cursor one word down.
PageUp     Moves the cursor one page up.
PageDown   Moves the cursor one page down.
Home   Moves the cursor to the beginning of the line.
Ctrl+Home  Moves the cursor to the beginning of the text.
End    Moves the cursor to the end of the line.
Ctrl+End   Moves the cursor to the end of the text.
Alt+Wheel  Scrolls the page horizontally (the Wheel is the mouse wheel).
Ctrl+Wheel     Zooms the text.''')

CONSOLE_USAGE = _(u'''
[KEY]...[FILE]
Keys:
--ForceEmbededIcons         Use embeded icons theme
-h, --help                  Print this help message
--version                   Print version info
''')

VERSION_INFO = _(u"SelectX. Text editor licensed by GPL3. Ver. %s")
#VERSION_INFO = _(u"SelectX. Text editor licensed by GPL3. Ver. %s")

#icon theme for very soft and very micro os ;) (based on http://tango.freedesktop.org/Tango_Icon_Library)
TANGO_ICONS = {'applications_system':"""/* XPM */
static char * applications_system_xpm[] = {
"16 16 17 1", "     c None", ". c #457ABE", "+  c #BCCDE3", "@  c #86A7D2", "#  c #6490C7", "$  c #9DB8DA", "%  c #7CA1CF", "&  c #467ABA", "*  c #5686C3", "=  c #82A5D1", "-  c #426B9C", ";  c #3F638F", ">  c #497CBA", ",  c #4C7FBD", "'  c #5682B7", ")  c #436FA5", "!  c #8FAED5", "                ", "      ...       ", "   .. .+. ..    ", "  .+@.#$#.@+.   ", "  .@$$$$$$$@.   ", "   .$%&*&=$.    ", " ..#$&- ;>$#..  ", " .+$$*   *$$+.  ", " ..#$,' )&$#..  ", "   .+%,*&!$.    ", "  .@$$$$$$$@.   ", "  .+@.#$#.@+.   ", "   .. .+. ..    ", "      ...       ", "                ", "                "};
""",
'office_calendar':"""/* XPM */
static char * office_calendar_xpm[] = {
"16 16 79 1","  c None",".  c #555753","+   c #BCBCBC","@   c #C7C7C7","#   c #8D8D8D","$   c #8E8E8E","%   c #D3D3D3","&   c #BBBBBB","*   c #BDBDBD","=   c #BEBEBE","-   c #BFBFBF",";   c #C3C3C3",">   c #C5C5C5",",   c #888887","'   c #FFFFFF",")   c #E2E2E2","!   c #E3E3E3","~   c #E4E4E4","{   c #E5E5E5","]   c #E6E6E6","^   c #E7E7E7","/   c #EFEFEF","(   c #7F7F7F","_   c #EAEAEA",":   c #F1F1F1","<   c #787877","[   c #7B7B7B","}   c #1C1C1C","|   c #0C0C0C","1   c #525252","2   c #1A1A1A","3   c #000000","4   c #DFDFDF","5   c #EBEBEB","6   c #EEEEEE","7   c #090909","8   c #ADADAD","9   c #B6B6B6","0   c #171717","a   c #6D6D6D","b   c #B3B3B3","c   c #F3F3F3","d   c #F4F4F4","e   c #DADADA","f   c #8C8C8C","g   c #030303","h   c #B5B5B5","i   c #E8E8E8","j   c #F2F2F2","k   c #F9F9F9","l   c #515151","m   c #181818","n   c #111111","o   c #6A6A6A","p   c #ECECEC","q   c #0E0E0E","r   c #3C3C3C","s   c #A1A1A1","t   c #EDEDED","u   c #F6F6F6","v   c #FAFAFA","w   c #FBFBFB","x   c #F7F7F7","y   c #F0F0F0","z   c #808080","A   c #818181","B   c #828282","C   c #838383","D   c #848484","E   c #858585","F   c #868686","G   c #878787","H   c #888888","I   c #B1B1B1","J   c #C4C4C4","K   c #B7B7B7","L   c #B8B8B8","M   c #B9B9B9","N   c #BABABA","................",".+++++++++++++@.",".+##$$$$$$$$$$@.",".%&++++*====-;>.",",'))!!~{{]^^^/'(",",')!~~{]]^^^_:'<",",'![}|1]^23456'<",",'~4{#7~^83!::'<",",'{903a^^b3~cd'<",",'{e]fg~_h3ijk'<",",'{lmnop:qrs6k'<",",']_pt:/jccuvw'<",",'kxxddy:cjccc'<",",:zAABCDDEFGGHI<","BJKKLMNN&&&&**J<"," B<<<<<<<<<<<<< "};""",
'media_record':"""/* XPM */
static char * media_record_xpm[] = {
"16 16 104 2","     c None",".  c #CE0000","+   c #CB0000","@   c #D00E0E","#   c #E96363","$   c #F38C8C","%   c #F59898","&   c #EE7878","*   c #DD3939","=   c #CD0000","-   c #DB2D2D",";   c #F8A1A1",">   c #F49A9A",",   c #F08888","'   c #EE8181",")   c #F18A8A","!   c #F7A2A2","~   c #EE6F6F","{   c #CD0505","]   c #CF0F0F","^   c #F79A9A","/   c #EE7C7C","(   c #EB6E6E","_   c #EB6D6D",":   c #EB6C6C","<   c #EB6A6A","[   c #EB6767","}   c #F49191","|   c #E75454","1   c #EA5D5D","2   c #F28686","3   c #EA6262","4   c #EB6363","5   c #EB6464","6   c #EB6262","7   c #EB5F5F","8   c #EA5C5C","9   c #EA5F5F","0   c #F89393","a   c #D20E0E","b   c #F27979","c   c #EA5757","d   c #E73F3F","e   c #E84545","f   c #EB5757","g   c #EC5858","h   c #EC5656","i   c #EB5353","j   c #E94F4F","k   c #F48383","l   c #DA2B2B","m   c #CD0101","n   c #F57676","o   c #E42525","p   c #E31C1C","q   c #E51E1E","r   c #E72121","s   c #E92E2E","t   c #EA3B3B","u   c #EA4242","v   c #E83B3B","w   c #F16868","x   c #E03A3A","y   c #CA0000","z   c #EF6161","A   c #E93939","B   c #E51D1D","C   c #E72020","D   c #E92222","E   c #EA2323","F   c #E82121","G   c #E61F1F","H   c #F36969","I   c #D81F1F","J   c #E13A3A","K   c #F16464","L   c #E61E1E","M   c #EB2424","N   c #ED2626","O   c #EC2525","P   c #EB3737","Q   c #F47171","R   c #CE0707","S   c #CE0303","T   c #F06565","U   c #F05454","V   c #EA2424","W   c #EB2525","X   c #EE2727","Y   c #EC2626","Z   c #EC3535","`   c #F57171"," .  c #DA2727","..  c #D10C0C","+.  c #ED5959","@.  c #F25A5A","#.  c #F25353","$.  c #F36363","%.  c #F57474","&.  c #CD0202","*.  c #D51919","=.  c #DF3636","-.  c #E34242",";.  c #D10A0A","                                ","                                ","              . +               ","          @ # $ % & * =         ","        - ; > , ' ) ! ~ {       ","      ] ^ / ( _ : < [ } |       ","      1 2 3 4 5 6 7 8 9 0 a     ","    = b c d e f g h i j k l     ","    m n o p q r s t u v w x     ","    y z A B C D E E F G H I     ","      J K L F M N O E P Q R     ","      S T U V W X Y Z `  .      ","        ..+.` @.#.$.%.-         ","          &.*.=.-. .;.          ","                                ","                                "};
""",
'media_skip_backward':"""/* XPM */
static char * media_skip_backward_xpm[] = {
"16 16 68 1","  c None",".  c #535451","+   c #414140","@   c #FCFCFB","#   c #3D3F3B","$   c #494A47","%   c #3D3D3B","&   c #4A4B48","*   c #4E4F4C","=   c #747571","-   c #FCFCFC",";   c #4D4F4B",">   c #4C4C4A",",   c #696C68","'   c #F9F9F8",")   c #4D4E4B","!   c #5D5E5B","~   c #5B5E5A","{   c #6E6F6C","]   c #EEEFEE","^   c #FCFDFC","/   c #FBFBFB","(   c #595A57","_   c #646662",":   c #EBEBEA","<   c #575855","[   c #EBECEA","}   c #FAFAFA","|   c #F2F4F1","1   c #F1F1F0","2   c #BDBDBB","3   c #FAFAF9","4   c #626460","5   c #656663","6   c #D4D6D3","7   c #F1F2F0","8   c #E7E9E4","9   c #DFE2DD","0   c #B4B5B2","a   c #F2F3F0","b   c #E8EAE6","c   c #E0E2DD","d   c #6D6E6A","e   c #6C6D69","f   c #82837F","g   c #ABAEA8","h   c #F0F1EF","i   c #F9FAF9","j   c #FEFEFE","k   c #797B75","l   c #969791","m   c #EEEFED","n   c #767973","o   c #767772","p   c #838581","q   c #91928C","r   c #C9CBC6","s   c #838580","t   c #8D9089","u   c #AFB0AC","v   c #81837D","w   c #7E7F79","x   c #90938C","y   c #9C9E97","z   c #9A9D97","A   c #ADAFAA","B   c #7F817C","C   c #82837E","                ","                ","                "," ...     +    + "," .@.   #$$  %$& "," .@.  *=-; >,') "," !@!~{]^/(_:^/< "," !@![}|1/23|1/4 "," 5@56789@0abc@d "," e@efghijklm3jn "," o@o pqris tuiv "," w@w   xyz  AyB "," www     C    C ","                ","                ","                "};
""",
'edit-find-replace':"""/* XPM */
static char * edit_find_replace_xpm[] = {
"16 16 96 2","      c None",".  c #818380","+   c #AEBAC8","@   c #A2BAD4","#   c #A7B9CC","$   c #A7B7C8","%   c #8AACD1","&   c #C5D7EA","*   c #9BB9D9","=   c #90ACCB","-   c #858783",";   c #888A85",">   c #8D8F8A",",   c #A2AEBB","'   c #84A8CF",")   c #DCE6F2","!   c #E4ECF5","~   c #CADAEC","{   c #8DB1D8","]   c #97B0CB","^   c #FFFFFF","/   c #A2B8D0","(   c #A4C0DE","_   c #D9E4F1",":   c #DDE7F2","<   c #C3D5EA","[   c #A2BFDF","}   c #80A5D0","|   c #F0F0EF","1   c #8F5902","2   c #A7B5C2","3   c #88AAD0","4   c #BBD0E8","5   c #CDDCEE","6   c #DEE8F3","7   c #A8C1DC","8   c #94B0CE","9   c #C7C7C6","0   c #EEEAC6","a   c #CFAD71","b   c #9FB8D1","c   c #91B3D6","d   c #BBD0E6","e   c #A6BED8","f   c #97B5D3","g   c #D1D2D0","h   c #EFEBC7","i   c #D2AC6A","j   c #A18355","k   c #848482","l   c #A3A4A3","m   c #B3C8DD","n   c #7FA7D1","o   c #99B4D1","p   c #959693","q   c #A48757","r   c #B8B8B7","s   c #8D8E8C","t   c #B0B1AF","u   c #EDE6C5","v   c #CFAA69","w   c #A08356","x   c #EDE5C4","y   c #C89F64","z   c #A08457","A   c #89806A","B   c #898B86","C   c #EFEFEE","D   c #705B39","E   c #C2AB8A","F   c #A38555","G   c #E7DCCA","H   c #878984","I   c #FEFEFD","J   c #4C4226","K   c #6B5736","L   c #CCC1AF","M   c #EFEFEF","N   c #82847F","O   c #FAFAF9","P   c #EEEEED","Q   c #000000","R   c #B3A996","S   c #C2C2C2","T   c #CBCBCA","U   c #E2E2E2","V   c #7D7F7B","W   c #FEFEFE","X   c #F7F7F7","Y   c #E9E9E9","Z   c #E5E5E5","`   c #EAEAEA"," .  c #8C8E89","..  c #868883","+.  c #858782","@.  c #8B8D88","        . . .                   ","      . + @ # .                 ","    . $ % & * = . - ; ; ; >     ","  . , ' ) ! ~ { ] . ^ ^ ^ ;     ","  . / ( _ : < [ } . | | ^ 1 1   ","  . 2 3 4 5 6 7 8 . 9 | 1 0 a 1 ","    . b c d e f . g | 1 h i j 1 ","  k l . m n o . p 9 1 h i q 1   ","k l r s . . . t | 1 u v w 1     ","k r s ^ | 9 9 9 1 x y z 1 A     ","  s B ^ | | | C D E F 1 G H     ","    B I | | C 1 J K 1 L M N     ","    B O | | P Q 1 R S T U V     ","    B ^ ^ ^ W X Y U Z ` M N     ","     .B ; ; ; H ..+.......@.    ","                                "};
""",'zoom-original':
"""/* XPM */
static char * image_missing_xpm[] = {
"16 16 62 1","  c None",".  c #888A85","+   c #FEFEFE","@   c #FDFDFD","#   c #D2D2D2","$   c #F6F6F6","%   c #D3D7CF","&   c #D7DBD4","*   c #DBDED7","=   c #DEE1DB","-   c #E1E4DF",";   c #E5E8E3",">   c #E9EAE6",",   c #ECEEEB","'   c #EFF1EF",")   c #EEEEEC","!   c #EFEFED","~   c #F0EFEE","{   c #F2F3F1","]   c #EEEFEC","^   c #CC0000","/   c #F2F2F0","(   c #F1F2F0","_   c #F0F0EF",":   c #F4F5F3","<   c #F4F4F3","[   c #F4F4F2","}   c #F2F2F1","|   c #F6F7F5","1   c #F0F0ED","2   c #F1F1F0","3   c #F8F7F6","4   c #F6F6F5","5   c #F4F5F4","6   c #F7F8F7","7   c #F1F1EF","8   c #F3F2F2","9   c #F9F9F9","0   c #F8F8F7","a   c #F4F3F2","b   c #F9FBF9","c   c #D5D9D1","d   c #F4F3F3","e   c #F7F7F5","f   c #F8F9F8","g   c #FBFBFA","h   c #FDFCFC","i   c #FBFBFC","j   c #FAFAF9","k   c #F7F7F6","l   c #F5F5F3","m   c #FCFCFB","n   c #D6DAD3","o   c #DADED7","p   c #E2E4DF","q   c #E5E7E3","r   c #ECEEEA","s   c #F0F1EE","t   c #F3F4F2","u   c #F6F7F6","v   c #FAFBF9","w   c #FDFEFD","................",".++++++++++++++.",".@############$.",".+$$$$$$$$$$$$$.",".@%%%%&*=-;>,'$.",".@%)))!!~!!)){$.",".@%)]^^/^^(_!:$.",".@%)_/^^^<[}_|$.",".@%12[^^^345{6$.",".@%78^^9^^0|ab$.",".@c7defghijklm$.",".@no=pq>rstuvw$.",".@$$$$$$$$$$$$$.",".@############$.",".+$$$$$$$$$$$$@.","................"};
""",'help-contents':
"""/* XPM */
static char * help_browser_xpm[] = {
"16 16 153 2","     c None",".  c #204A87","+   c #2C548D","@   c #8CA1C1","#   c #BDC9DB","$   c #EBEFF4","%   c #8CA2C1","&   c #5B7AA7","*   c #E3E8F0","=   c #A9B9D0","-   c #6582AC",";   c #3B6096",">   c #AABAD1",",   c #E4E9F0","'   c #5C7BA7",")   c #617EAA","!   c #E7EBF2","~   c #5978A6","{   c #47699C","]   c #C2CEDE","^   c #F0F3F7","/   c #E6EAF1","(   c #A7B8D0","_   c #4D6FA0",":   c #6482AD","<   c #E8EDF3","[   c #5D7CA8","}   c #2D558E","|   c #E5EAF1","1   c #5878A5","2   c #6C88B0","3   c #FDFDFE","4   c #D6DEE9","5   c #EFF2F6","6   c #FFFFFF","7   c #BDCADC","8   c #386098","9   c #6B89B3","0   c #E6EBF2","a   c #2D558D","b   c #90A5C3","c   c #4B6E9F","d   c #325B94","e   c #597AA8","f   c #FBFCFD","g   c #466DA1","h   c #436A9F","i   c #B7C6DA","j   c #94A9C6","k   c #C0CCDD","l   c #27508B","m   c #2D5690","n   c #345C95","o   c #3A6299","p   c #89A1C2","q   c #E8ECF3","r   c #4B72A5","s   c #4D73A6","t   c #86A1C3","u   c #C6D2E1","v   c #234C89","w   c #EDF0F5","x   c #365C93","y   c #254F8A","z   c #345D95","A   c #3B639A","B   c #6D8BB5","C   c #F9FBFC","D   c #FEFEFE","E   c #829DC1","F   c #547AAC","G   c #567CAD","H   c #6C8DB7","I   c #EFF3F7","J   c #214B88","K   c #385E94","L   c #2A538E","M   c #335B94","N   c #42699F","O   c #A0B5D0","P   c #5A7FB0","Q   c #5E83B2","R   c #6085B4","S   c #7594BD","T   c #F0F3F8","U   c #224B88","V   c #6A86AF","W   c #2F5891","X   c #386097","Y   c #40679D","Z   c #5176A7","`   c #C8D4E4"," .  c #CAD6E5","..  c #6286B4","+.  c #6387B6","@.  c #678BB9","#.  c #6A8EBA","$.  c #9BB2D1","%.  c #CCD7E6","&.  c #244E8A","*.  c #ADBCD3","=.  c #335C94","-.  c #3C649A",";.  c #456CA1",">.  c #5278A9",",.  c #8FA8C8","'.  c #94ADCC",").  c #6589B7","!.  c #6B8FBB","~.  c #7093BF","{.  c #7396C1","].  c #C9D7E7","^.  c #A0B4CF","/.  c #6987B1","(.  c #496FA3","_.  c #6284B2",":.  c #6F92BD","<.  c #7296C1","[.  c #789BC5","}.  c #9DB7D6","|.  c #EDF1F7","1.  c #2F578F","2.  c #6381AB","3.  c #E9EEF3","4.  c #728FB7","5.  c #4C72A5","6.  c #6587B3","7.  c #7497C1","8.  c #A0B9D7","9.  c #F1F5F9","0.  c #6B88B2","a.  c #6482AC","b.  c #E9EDF3","c.  c #BAC9DD","d.  c #8BA5C7","e.  c #7191BB","f.  c #7999C1","g.  c #9FB7D5","h.  c #CDDAE9","i.  c #EFF3F8","j.  c #718DB5","k.  c #264F8B","l.  c #2E558F","m.  c #9BAFCB","n.  c #CBD6E5","o.  c #F1F4F8","p.  c #F2F5F9","q.  c #D1DBE8","r.  c #A6B9D3","s.  c #315891","t.  c #234D89","u.  c #224C88","v.  c #254F8B","          . . . . . .           ","        + @ # $ $ # % +         ","    . & * = - ; ; - > , ' .     ","    ) ! ~ { ] ^ / ( _ : < [     ","  } | 1 . 2 3 4 5 6 7 8 9 0 a   ",". b = . . c _ d e 6 f g h i j . ",". k - . l m n o p 6 q r s t u v ",". w x y m z A B C D E F G H I J ",". w K L M o N < 6 O P Q R S T U ",". k V W X Y Z `  ...+.@.#.$.%.&.",". b *.=.-.;.>.,.'.).!.~.{.].^.J ","  } 0 /.Y (._.6 6 :.<.[.}.|.1.  ","    2.3.4.5.6.6 6 7.[.8.9.0.    ","    . a.b.c.d.e.f.g.h.i.j.k.    ","        l.m.n.o.p.q.r.s.        ","          . t.u.u.v.J           "};
""",'zoom-out':
"""/* XPM */
static char * list_remove_xpm[] = {
"16 16 19 1","  c None",".  c #3465A4","+   c #C0D3E8","@   c #BBD1E7","#   c #BCD1E7","$   c #B7CEE6","%   c #B6CDE6","&   c #B5CCE6","*   c #B6CCE6","=   c #B4CCE5","-   c #95B7DB",";   c #94B6DB",">   c #92B4DA",",   c #90B3DA","'   c #86ADD9",")   c #83AAD8","!   c #7FA8D7","~   c #7DA6D7","{   c #9FBEE0","                ","                ","                ","                ","                ","                ","  ............  ","  .+@#$$$$%&*.  ","  .=-;>,')!~{.  ","  ............  ","                ","                ","                ","                ","                ","                "};
""",'zoom-in':
"""/* XPM */
static char * list_add_xpm[] = {
"16 16 19 1","  c None",".  c #3465A4","+   c #B7CEE6","@   c #C0D3E8","#   c #BBD1E7","$   c #BCD1E7","%   c #B6CDE6","&   c #B5CCE6","*   c #B6CCE6","=   c #B4CCE5","-   c #95B7DB",";   c #94B6DB",">   c #92B4DA",",   c #90B3DA","'   c #86ADD9",")   c #83AAD8","!   c #7FA8D7","~   c #7DA6D7","{   c #9FBEE0","                ","                ","      ....      ","      .++.      ","      .++.      ","      .++.      ","  .....++.....  ","  .@#$++++%&*.  ","  .=-;>,')!~{.  ","  .....''.....  ","      .+'.      ","      .+'.      ","      .++.      ","      ....      ","                ","                "};
""",'application-exit':
"""/* XPM */
static char * dialog_error_xpm[] = {
"16 16 118 2","     c None",".  c #A40000","+   c #B50D0D","@   c #DE3A3A","#   c #E65151","$   c #E95C5C","%   c #E85B5B","&   c #E44C4C","*   c #DB3434","=   c #B50B0B","-   c #D62D2D",";   c #EA6060",">   c #E42F2F",",   c #E11B1B","'   c #E11818",")   c #E01717","!   c #DE1817","~   c #E02829","{   c #E45252","]   c #D32626","^   c #E95252","/   c #E21C1C","(   c #E21919","_   c #E01716",":   c #DF1515","<   c #DE1414","[   c #DD1314","}   c #DC1514","|   c #E14242","1   c #D12323","2   c #EA5F5F","3   c #E11918","4   c #E01817","5   c #DF1717","6   c #DE1616","7   c #DC1314","8   c #DB1312","9   c #DA1111","0   c #D91212","a   c #E14949","b   c #B40A0A","c   c #DE3939","d   c #E11919","e   c #E11718","f   c #DF1617","g   c #DE1515","h   c #DD1414","i   c #DD1413","j   c #DB1213","k   c #DB1111","l   c #DA1010","m   c #D90F0F","n   c #D91F1F","o   c #D6292A","p   c #E6504F","q   c #E11A1A","r   c #E01718","s   c #FFFFFF","t   c #D80E0D","u   c #D60E0F","v   c #DB393A","w   c #E85A5B","x   c #DF1616","y   c #D60C0C","z   c #D50B0B","A   c #DC3F3F","B   c #E85758","C   c #DF1716","D   c #D60B0B","E   c #D40A0A","F   c #DB3E3D","G   c #E44949","H   c #DE1717","I   c #DC1313","J   c #DB1212","K   c #D80F0E","L   c #D70D0D","M   c #D30B0B","N   c #DA3333","O   c #DB3232","P   c #DF2627","Q   c #DC1312","R   c #DB1211","S   c #D70E0D","T   c #D50A0B","U   c #D30908","V   c #D51717","W   c #D32323","X   c #E44D4E","Y   c #DB1413","Z   c #D80E0E","`   c #D70D0C"," .  c #D50B0A","..  c #D20A09","+.  c #D93737","@.  c #B20707","#.  c #D22424","$.  c #E13E3E","%.  c #D91111","&.  c #D40909","*.  c #D30809","=.  c #D30A09","-.  c #D82E2E",";.  c #CD1A1A",">.  c #D12222",",.  c #E04545","'.  c #D91D1D",").  c #D60D0E","!.  c #D30909","~.  c #D41716","{.  c #DA3737","].  c #B30909","^.  c #D62727","/.  c #DB3636","(.  c #DC3D3D","_.  c #DB3B3B",":.  c #D83030","<.  c #D42222","          . . . . . .           ","      . + @ # $ % & * = .       ","    . - ; > , ' ) ! ~ { ] .     ","  . - ^ / ( ' _ : < [ } | 1 .   ","  + 2 / 3 4 5 6 < 7 8 9 0 a b   ",". c > d e f g h i j k l m n o . ",". p q r s s s s s s s s t u v . ",". w 4 x s s s s s s s s y z A . ",". B C g s s s s s s s s D E F . ",". G H i I J l m K L y D E M N . ",". O P Q R l m K S y T E U V W . ","  b X Y l m Z ` y  .E U ..+.@.  ","  . #.$.%.Z L D D &.*.=.-.;..   ","    . >.,.'.). .&.!.~.{.;..     ","      . ].^./.(._.:.<.@..       ","          . . . . . .           "};
""",'window-close':
"""/* XPM */
static char * emblem_unreadable_xpm[] = {
"16 16 130 2","     c None",".  c #A0A0A0","+   c #A6A6A6","@   c #CBCBCB","#   c #D4D4D4","$   c #D5D5D5","%   c #D0D0D0","&   c #B0B0B0","*   c #9F9F9F","=   c #D2D2D2","-   c #E79D9D",";   c #EB5D5D",">   c #EB5C5C",",   c #EC5D5D","'   c #E88D8D",")   c #DFDFDF","!   c #9E9E9E","~   c #9D9D9D","{   c #DEDEDE","]   c #ED3D3D","^   c #EE2828","/   c #EE2B2B","(   c #E4E4E4","_   c #A3A3A3",":   c #E0E0E0","<   c #EE3939","[   c #EE5756","}   c #EE3E3E","|   c #ED2727","1   c #ED3434","2   c #ED5F5F","3   c #EE3030","4   c #E6E6E6","5   c #E1E1E1","6   c #ED3838","7   c #EC2626","8   c #EC5252","9   c #EEEEEC","0   c #EEE6E4","a   c #EC5958","b   c #EC3534","c   c #EDCAC8","d   c #ED8F8E","e   c #EC2525","f   c #E8E8E8","g   c #E3E3E3","h   c #EB3636","i   c #EA2323","j   c #EA403F","k   c #EEE5E3","l   c #EEE7E4","m   c #EDD3D1","n   c #EA6A69","o   c #E92222","p   c #EAEAEA","q   c #E5E5E5","r   c #E83333","s   c #E72020","t   c #E71F1F","u   c #E84F4F","v   c #EEE4E2","w   c #EA8584","x   c #E61E1E","y   c #E61F1F","z   c #ECECEC","A   c #E63131","B   c #E51D1D","C   c #E41C1C","D   c #E42D2C","E   c #EDD2D0","F   c #EEEBE9","G   c #E65251","H   c #E31B1B","I   c #EDEDED","J   c #A4A4A4","K   c #E7E7E7","L   c #E42E2E","M   c #E31A1A","N   c #E22020","O   c #ECC8C6","P   c #EDE8E6","Q   c #E44949","R   c #E11919","S   c #E21A1A","T   c #EFEFEF","U   c #E32D2D","V   c #E01818","W   c #E34F4E","X   c #E57C7B","Y   c #E04444","Z   c #EDE2E0","`   c #E78F8E"," .  c #DF1616","..  c #F0F0F0","+.  c #E9E9E9","@.  c #E12B2B","#.  c #DE1515","$.  c #DD1717","%.  c #E5807F","&.  c #E36665","*.  c #DA1111","=.  c #DE3838","-.  c #E68A89",";.  c #DF3130",">.  c #DD1313",",.  c #F1F1F1","'.  c #DF2929",").  c #DC1313","!.  c #D91010","~.  c #D80E0E","{.  c #D90F0F","].  c #DC1212","^.  c #E46E6E","/.  c #DB1717","(.  c #D91616","_.  c #D81414",":.  c #D71313","<.  c #D61212","[.  c #D61111","}.  c #D71212","|.  c #D91515","1.  c #E15454","2.  c #B9B9B9","3.  c #F2F2F2","4.  c #F5F5F5","5.  c #F7F7F7","6.  c #F9F9F9","7.  c #FBFBFB","8.  c #FCFCFC","9.  c #CACACA","    . . . . . . . . . . . .     ","  + @ # $ $ $ $ $ $ $ $ $ % & * ","* = - ; > , , , , , , , > ' ) ! ","~ { ] ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ / ( _ ","~ : < ^ ^ [ } | | 1 2 3 ^ ^ 4 _ ","~ 5 6 7 8 9 0 a b c 9 d e 7 f _ ","~ g h i j k 9 l m 9 9 n o i p _ ","~ q r s t u v 9 9 9 w x y s z _ ","~ 4 A B C D E 9 9 F G H C B I J ","~ K L M N O 9 9 P 9 0 Q R S T J ","~ f U V W 9 9 X Y Z 9 `  .V ..J ","~ +.@.#.$.%.&.*.*.=.-.;.>.#.,.J ","~ +.'.).*.!.~.~.~.~.~.{.*.].,.J ","! g ^./.(._.:.<.[.<.}._.|.1.... ","* 2.p 3.4.5.6.7.8.7.6.5.4.,.9.. ","  . ~ ! ! ! ! ! ! ! ! ! ! ~ .   "};
""",'list-add':
"""/* XPM */
static char * list_add_xpm[] = {
"16 16 19 1","  c None",".  c #3465A4","+   c #B7CEE6","@   c #C0D3E8","#   c #BBD1E7","$   c #BCD1E7","%   c #B6CDE6","&   c #B5CCE6","*   c #B6CCE6","=   c #B4CCE5","-   c #95B7DB",";   c #94B6DB",">   c #92B4DA",",   c #90B3DA","'   c #86ADD9",")   c #83AAD8","!   c #7FA8D7","~   c #7DA6D7","{   c #9FBEE0","                ","                ","      ....      ","      .++.      ","      .++.      ","      .++.      ","  .....++.....  ","  .@#$++++%&*.  ","  .=-;>,')!~{.  ","  .....''.....  ","      .+'.      ","      .+'.      ","      .++.      ","      ....      ","                ","                "};
""",'preferences-desktop-font':
"""/* XPM */
static char * preferences_desktop_font_xpm[] = {
"16 16 78 1","  c None",".  c #888A85","+   c #FFFFFF","@   c #E3E3E3","#   c #A7A7A7","$   c #828282","%   c #2F2F2F","&   c #E6E6E6","*   c #FDFDFD","=   c #E2E2E2","-   c #DBDBDB",";   c #CECECE",">   c #E8E8E8",",   c #E9E9E9","'   c #B1B1B1",")   c #747474","!   c #E6E7E6","~   c #E5E6E5","{   c #E4E4E5","]   c #E4E3E4","^   c #D3D3D3","/   c #BFBFBF","(   c #EAE9E9","_   c #E8E9E9",":   c #E8E7E7","<   c #E4E5E4","[   c #FBFBFB","}   c #E4E4E4","|   c #B8B9B8","1   c #4B4B4B","2   c #ECEDEC","3   c #ECEBEC","4   c #EAEBEB","5   c #E7E7E6","6   c #ECECEC","7   c #EDEDED","8   c #EEEEEE","9   c #EFEFEF","0   c #474747","a   c #2C2C2C","b   c #F0F0F0","c   c #ECECEB","d   c #E9E9EA","e   c #F8F8F8","f   c #F1F1F1","g   c #484848","h   c #202020","i   c #343434","j   c #000000","k   c #010101","l   c #626262","m   c #F2F2F2","n   c #F6F6F6","o   c #F3F3F3","p   c #767676","q   c #666666","r   c #EAEBEA","s   c #F5F5F5","t   c #494949","u   c #050505","v   c #F9F9F9","w   c #7C7C7C","x   c #EBEBEB","y   c #F4F4F4","z   c #060606","A   c #F7F7F7","B   c #4A4A4A","C   c #797979","D   c #5F5F5F","E   c #ADADAD","F   c #EBEAEA","G   c #565656","H   c #2E2E2E","I   c #222222","J   c #040404","K   c #4D4D4D","L   c #FCFCFC","M   c #FAFAFA"," .............. ",".++++++++++++++.",".+@#$%%@&&&&@@*.",".+@=-;%@>,>>@@*.",".+@'%)%&!&~{]@*.",".+@%^/%,,(_:&<[.",".+}%%%|1%234,5[.",".+&67890ab98cde.",".+>79bfghijklmn.",".+(9bmogjpmqj'9.",".+rbmostuov-jw9.",".+xfoyntzf[^jp9.",".+4mynABjCADjE9.",".+FmyneGHIJjKA9.",".+LLLLLLMMMnnn9."," .............. "};
""",'edit-select-all':
"""/* XPM */
static char * edit_select_all_xpm[] = {
"16 16 37 1","  c None",".  c #8B8D89","+   c #888A85","@   c #8C8E89","#   c #FDFDFD","$   c #FEFEFE","%   c #FCFCFC","&   c #FBFBFB","*   c #FAFAFA","=   c #F9F9F9","-   c #8B8D88",";   c #A8BED6",">   c #A9BFD7",",   c #AAC0D8","'   c #ABC1D9",")   c #F8F8F8","!   c #8197AF","~   c #ACC2DA","{   c #ADC3DB","]   c #AEC4DC","^   c #EBEBEB","/   c #AFC5DD","(   c #ECECEC","_   c #B0C6DE",":   c #EEEEEE","<   c #B1C7DF","[   c #F0F0F0","}   c #B2C8E0","|   c #F2F2F2","1   c #F7F7F7","2   c #000000","3   c #B3C9E1","4   c #F4F4F4","5   c #F5F5F5","6   c #F6F6F6","7   c #8298B0","8   c #8D8F8A"," .++++++++++++@ "," +#$$##%%&&**=- "," +#;>>,,''''')- "," +$>!!!!~!!!~)- "," +#,!!!!{{{{{)- "," +#,!!!!{]]]^)- "," +%'!!!!]!!/()- "," +%~~{]//___:)- "," +%~{]//__<<[)- "," +&~!!!!!!!}|1- "," +&{]/__2}2341- "," +*{]/_<}25661- "," +={7777}21)11- "," +={]/_<}21=)1- "," +))))))2)2)))- "," @++++++++++++8 "};
""",'edit-find':
"""/* XPM */
static char * edit_find_xpm[] = {
"16 16 77 1","  c None",".  c #9A9B97","+   c #888A85","@   c #8D8F8A","#   c #8A8C87","$   c #FFFFFF","%   c #898B86","&   c #F0F0EF","*   c #C7C7C6","=   c #D6D6D5","-   c #818380",";   c #828480",">   c #A8A9A6",",   c #AEBAC8","'   c #A6BCD2",")   c #A2BAD4","!   c #A8B9CD","~   c #D6D7D5","{   c #A8B7C8","]   c #8AACD2","^   c #BFD3E7","/   c #C5D7EA","(   c #9CBAD9","_   c #90ADCB",":   c #A3AEBB","<   c #85A9CF","[   c #DCE6F2","}   c #E8EEF7","|   c #E4ECF5","1   c #CADAEC","2   c #8EB2D8","3   c #97AFCB","4   c #A2B8D0","5   c #A5C0DF","6   c #D9E4F1","7   c #E0EAF3","8   c #DDE7F2","9   c #C1D4E9","0   c #A0BEDF","a   c #81A6D0","b   c #FEFEFD","c   c #A9BFD6","d   c #A5C1E0","e   c #D0DEEE","f   c #DAE5F2","g   c #CDDCED","h   c #C8D9EC","i   c #BCD0E8","j   c #80A7D1","k   c #FAFAF9","l   c #A7B5C3","m   c #89ABD0","n   c #B3CAE5","o   c #C3D7EB","p   c #C1D4EA","q   c #CFDDEE","r   c #A3BDDA","s   c #93AFCE","t   c #CFCFCD","u   c #9FB8D1","v   c #91B3D6","w   c #AFC5DF","x   c #B2CAE3","y   c #A0BAD6","z   c #97B4D3","A   c #757673","B   c #8C8E89","C   c #7E807B","D   c #B3C8DC","E   c #8BACCF","F   c #80A8D1","G   c #99B3D0","H   c #A3A4A3","I   c #6C6E6A","J   c #8D8E8C","K   c #B8B8B7","L   c #848482",".++++++++++@    ","#$$$$$$$$$$+    ","%$&&&&&&&&$+    ","#$&******&$+    ","%$&&&&=----;    ","#$&**>-,')!-    ","%$&&~-{]^/(_-   ","#$&*-:<[}|123-  ","#$&&-4567890a-  ","%b&&-cdefghij-  ","%k&&-lmnopqrs-  ","%$$$t-uvwxyz-A  ","B%+++C-DEFG-HHI ","      I----JKHHL","            JKHL","             JJL"};
""",'edit-paste':
"""/* XPM */
static char * edit_paste_xpm[] = {
"16 16 77 1","  c None",".  c #5F5F5E","+   c #5C5C5C","@   c #6D4401","#   c #6C4401","$   c #6B4403","%   c #5C5C5B","&   c #959589","*   c #97978A","=   c #C08424","-   c #A47E3E",";   c #706D64",">   c #5E5E5E",",   c #7F7F7C","'   c #80807D",")   c #7E7E7B","!   c #6E6C64","~   c #A17C40","{   c #B97F23","]   c #6C4301","^   c #6F4602","/   c #C68827","(   c #716F64","_   c #F1F1F1",":   c #E0E0E0","<   c #BBBBBB","[   c #F2F2F2","}   c #6E6D64","|   c #C58727","1   c #6A4200","2   c #666864","3   c #FFFFFF","4   c #F0F0EF","5   c #676964","6   c #C28628","7   c #C58726","8   c #B3B5B5","9   c #EFEFEE","0   c #EFEFED","a   c #EDEDEB","b   c #6E4602","c   c #B2B4B4","d   c #B1B2B2","e   c #EAEAE8","f   c #EDEDEC","g   c #EBEBEA","h   c #DBDBD9","i   c #EEEEED","j   c #ECECEB","k   c #EBEBE9","l   c #E9E9E7","m   c #DADAD8","n   c #CCCDCA","o   c #ECECEA","p   c #E8E8E6","q   c #CDCECB","r   c #B9BAB6","s   c #B8B9B5","t   c #6E4502","u   c #E7E7E5","v   c #D9D9D6","w   c #B9B9B6","x   c #E7E7E4","y   c #D8D8D5","z   c #C1C2BE","A   c #B7B7B4","B   c #706D63","C   c #EDEEED","D   c #FEFEFE","E   c #FEFEFD","F   c #BA7F23","G   c #A77D3B","H   c #736F64","I   c #6A6C68","J   c #A37C3D","K   c #B37B22","L   c #6B4301","     .++++.     ","  @#$%&**&%$##  "," @=-;>,'')>!~{] "," ^/(_:<<<<:[}|1 "," ^/234444443561 "," ^7234888893561 "," ^72344440a3561 "," b723488cde3561 "," b72349fgeh3561 "," b723ijklmn3561 "," b723oepqrs3561 "," t723luvw333561 "," t723xyzA335|61 "," t7BCDDD9E5|||1 "," ]FGHIIIIIJJJKL ","  ]##########L  "};
""",'edit-cut':
"""/* XPM */
static char * edit_cut_xpm[] = {
"16 16 88 1","  c None",".  c #8B8D88","+   c #939590","@   c #8F918C","#   c #8E908B","$   c #F7F7F7","%   c #90918D","&   c #D2D3D0","*   c #D2D4D0","=   c #EFF0EF","-   c #92948F",";   c #AAACA7",">   c #C6C8C3",",   c #8D8F8A","'   c #B3B5B0",")   c #F7F7F6","!   c #CCCEC9","~   c #AEAFAB","{   c #DBDCD9","]   c #91938E","^   c #8C8E89","/   c #B6B8B3","(   c #CDCECB","_   c #B5B6B2",":   c #9FA09C","<   c #B5B6B3","[   c #B8BAB5","}   c #E1E1DF","|   c #F5F6F5","1   c #9A9C97","2   c #A8A9A5","3   c #BABBB7","4   c #E7E8E6","5   c #8A8C87","6   c #898984","7   c #C5C6C3","8   c #B3B2AF","9   c #9C2F2C","0   c #AE1818","a   c #AB1616","b   c #A60606","c   c #A34A45","d   c #A60202","e   c #C71A19","f   c #AD1717","g   c #A90707","h   c #D22020","i   c #CE1E1E","j   c #B70F0E","k   c #A40502","l   c #A80403","m   c #C91A1A","n   c #D12020","o   c #CB1F1F","p   c #A90A0A","q   c #A80606","r   c #D01F1F","s   c #A80303","t   c #C01514","u   c #A60101","v   c #CD1D1C","w   c #C01513","x   c #CD1D1D","y   c #A70606","z   c #AB1414","A   c #D52323","B   c #CE1D1D","C   c #CA1B1A","D   c #AB0D0D","E   c #CF1D1D","F   c #B50B0B","G   c #D32121","H   c #AA0C0C","I   c #AA0909","J   c #D62323","K   c #B80D0D","L   c #D11F1F","M   c #AB1111","N   c #AB1313","O   c #DB2727","P   c #A80707","Q   c #AA0808","R   c #D42222","S   c #AA0E0E","T   c #AB1010","U   c #AA0D0D","V   c #AA0B0B","W   c #A90B0B","    .+    .@    ","   #$.    %&@   ","   .*=-   ;>,   ","   ,').  #!~.   ","    .{=]^/(.    ","    ,_$.:<[.    ","     .}|12.     ","     ,34;#5     ","      6789      ","    0abcdef0    ","   ghijklmnop   ","  qrstu  vwsxy  "," zA  Bp  sC  nz "," DE FGH  IJK LM "," NOrBP    QREBN ","  STa      UVW  "};
""",'edit-copy':
"""/* XPM */
static char * edit_copy_xpm[] = {
"16 16 41 1","  c None",".  c #888A85","+   c #FFFFFF","@   c #F0F0EF","#   c #EFEFEE","$   c #C8C8C7","%   c #9A9B97","&   c #8D8F8A","*   c #8A8C87","=   c #898B86","-   c #C7C7C6",";   c #C6C6C5",">   c #EEEEED",",   c #EDEDEC","'   c #FEFEFE",")   c #ECECEC","!   c #C4C4C3","~   c #FAFAFA","{   c #F3F3F3","]   c #F9F9F9","^   c #EBEBEB","/   c #EAEAEA","(   c #EEEEEE","_   c #F7F7F6",":   c #C3C4C3","<   c #F3F3F2","[   c #F4F4F3","}   c #F2F2F2","|   c #8C8E89","1   c #FEFEFD","2   c #989A95","3   c #F8F8F7","4   c #E3E4E2","5   c #FAFAF9","6   c #E3E3E2","7   c #F4F4F4","8   c #F6F6F5","9   c #FCFCFB","0   c #FBFBFB","a   c #D4D4D4","b   c #989A96"," ..........     "," ++++++++++.    "," +@#####@@+.    "," +@$%..........&"," +@@*++++++++++."," +@$=+@@@@@@@@+."," +@#*+@------@+."," +#;=+@@@@@@@@+."," +>,*+@-----@@+."," ')!=+@@@@@@@~{."," ]^/*+@-----(_:."," <[}*+@@@@@||||."," ====1@@@@~2~34.","    =5@@@~~2~6..","    =7_890ab4.. ","    |=........  "};
""",'edit-redo':
"""/* XPM */
static char * edit_redo_xpm[] = {
"16 16 47 1","  c None",".  c #4E9A06","+   c #AEF36C","@   c #8F9B0C","#   c #A9DE49","$   c #AEF16A","%   c #AEF26B","&   c #B3F573","*   c #A6EF61","=   c #73D216","-   c #ACD945",";   c #AFEF67",">   c #A1E950",",   c #A0DB24","'   c #A9D846",")   c #B1EF65","!   c #A4DE24","~   c #97DD2A","{   c #AFD71A","]   c #75D318","^   c #9DC230","/   c #B1ED60","(   c #A5DF26","_   c #C8D009",":   c #77D014","<   c #8AE234","[   c #559F0C","}   c #B1E963","|   c #BAE031","1   c #CBD417","2   c #9BD622","3   c #A1DA23","4   c #D9DE23","5   c #529D0A","6   c #B2EC64","7   c #CDD624","8   c #93A10B","9   c #CCD41E","0   c #BEE246","a   c #99A605","b   c #B3D937","c   c #B8DD3A","d   c #AFC723","e   c #919D05","f   c #5AA80F","g   c #C0D62C","h   c #9A9902","         .      ","         ..     ","         .+.    ","      ....++.   ","    .@#$%&*=+.  ","   .-;>,,,,==+. ","  .')!~,,{===]+."," .^/({{_:====<. "," [}|1233334=<.  "," 5678.....9<.   "," .0a.    .<.    "," .b.     ..     "," .c.     .      "," .de            ","  fgh           ","                "};
""",'edit-undo':
"""/* XPM */
static char * edit_undo_xpm[] = {
"16 16 61 1","  c None",".  c #C4A000","+   c #FBF3AD","@   c #FBE425","#   c #BEA113","$   c #BB9F15","%   c #BBA11B","&   c #F6E131","*   c #FAE320","=   c #FAEC73","-   c #FAEB6F",";   c #F7E86E",">   c #F7E86C",",   c #BCA114","'   c #C1A314",")   c #F6E02F","!   c #F7E232","~   c #F1DB29","{   c #F5E02F","]   c #E3CD16","^   c #ECD936","/   c #F6E769","(   c #E3CE41","_   c #C1A313",":   c #F8E232","<   c #E8D21D","[   c #E1CD40","}   c #BDA116","|   c #FBED79","1   c #F4DF2C","2   c #D6C004","3   c #DFC80B","4   c #F3E56A","5   c #C5AB1B","6   c #BCA015","7   c #FBED76","8   c #DAC304","9   c #F9EA69","0   c #F7DD05","a   c #DFC80A","b   c #D8C207","c   c #EBDC6F","d   c #BFA31B","e   c #C4A901","f   c #EEE16E","g   c #DFC90F","h   c #F2E469","i   c #C0A41A","j   c #F5E66D","k   c #EFE276","l   c #C1A319","m   c #C8AC02","n   c #F2E788","o   c #C2A211","p   c #CBAA0E","q   c #E9DA5D","r   c #C0A623","s   c #DBC443","t   c #D8C543","u   c #EADB66","v   c #C2A611","      .         ","     ..         ","    .+.         ","   .+@..#$%     ","  .+&*=-;>,'    "," .+)!~{~]^/(_   ",".+):!!{~<<<^[}  "," .|:1222<<<3456 ","  .78799990abcd ","   .77....efghi ","    .7.    .jkl ","     ..     mno ","      .     pqr ","            str ","            uv  ","                "};
""",'document-print':
"""/* XPM */
static char * document_print_xpm[] = {
"16 16 67 1","  c None",".  c #AAABA9","+   c #F9F9F9","@   c #888A85","#   c #F8F8F8","$   c #C4C4C4","%   c #F1F1F1","&   c #F3F3F3","*   c #F7F7F7","=   c #C6C6C6","-   c #C7C7C7",";   c #E0E0E0",">   c #E2E2E2",",   c #E3E3E3","'   c #E5E5E5",")   c #E6E6E6","!   c #E7E7E7","~   c #F6F6F6","{   c #F5F5F5","]   c #F5F5F6","^   c #7D7E7C","/   c #858684","(   c #ABABAB","_   c #A9A9A9",":   c #AAAAAA","<   c #FCFCFC","[   c #F4F4F4","}   c #E8E8E8","|   c #FDFDFD","1   c #D4D4D4","2   c #EDEDED","3   c #AEAEAE","4   c #DFDFDF","5   c #E1E1E1","6   c #DCDCDC","7   c #9F9F9F","8   c #CDCCCB","9   c #F0F0F0","0   c #CCCBCB","a   c #DDDDDD","b   c #DEDEDE","c   c #D9D9D9","d   c #8C8B8A","e   c #C5C5C5","f   c #F2F2F2","g   c #BEBEBE","h   c #868584","i   c #7A7978","j   c #767574","k   c #787675","l   c #767472","m   c #72716F","n   c #747372","o   c #B2B2B2","p   c #BBBBBB","q   c #B9B9B9","r   c #B8B8B8","s   c #B8B8B7","t   c #B6B6B6","u   c #B3B3B3","v   c #B5B5B5","w   c #B7B7B7","x   c #ECECEC","y   c #D7D7D7","z   c #D8D8D8","A   c #D5D5D5","B   c #D6D6D6","                ","   ...........  ","   .++++@+++#.  ","   .+$$@@@$$#.  ","   .+%@@@@@&*.  ","   .*$$=@=--#.  ","   .*;>,@')!*.  ","   .~{{{{]]~*.  "," ^^/(_(((((_:/^^"," ^<+[[[[[[[[[)}^"," ^|123&4,5>;678^"," ^90aabbb6aacde^"," ^fghiijklmnkoe^"," ^fpqqrrstuvwr-^"," ^xyzzyyyyyAyB1^"," ^^^^^^^^^^^^^^^"};
""",'document-print-preview':
"""/* XPM */
static char * document_print_preview_xpm[] = {
"16 16 130 2","     c None",".  c #AAABA9","+   c #F9F9F9","@   c #A2A3A1","#   c #6E6F6B","$   c #ADAEAC","%   c #F8F8F8","&   c #9D9E9C","*   c #70726F","=   c #CACBC9","-   c #DADBDC",";   c #C9C9C8",">   c #6E706D",",   c #B3B3B2","'   c #C4C4C4",")   c #6F716C","!   c #DADBDB","~   c #98AAC2","{   c #6C96C4","]   c #9DAEC3","^   c #DEDEDE","/   c #DDDDDD","(   c #F3F3F3","_   c #F7F7F7",":   c #6C6E6A","<   c #DADADA","[   c #8CA7C5","}   c #729FCE","|   c #C4D5E9","1   c #729FCD","2   c #8FA8C5","3   c #DBDBDB","4   c #6F716D","5   c #C7C7C7","6   c #A7A8A6","7   c #9EAEC3","8   c #D6E1EF","9   c #E4ECF5","0   c #A9C2DC","a   c #719ECE","b   c #AEBBCA","c   c #A5A6A3","d   c #B9BAB8","e   c #696B66","f   c #DADAD9","g   c #6690BF","h   c #ADC7E2","i   c #D8E2EF","j   c #DFE8F3","k   c #85A6CC","l   c #779ECA","m   c #81A3CA","n   c #D9D9D8","o   c #82847F","p   c #C2C2C2","q   c #85A5C9","r   c #7899BF","s   c #8BA2BD","t   c #86A2C1","u   c #95A6B9","v   c #7392B5","w   c #89A9CA","x   c #C8C8C7","y   c #8D8E8B","z   c #AAAAAA","A   c #858684","B   c #7D7E7C","C   c #80827F","D   c #8F918E","E   c #D1D9E1","F   c #A4BFDC","G   c #9FBCDC","H   c #B2C7DE","I   c #D2D9E0","J   c #727470","K   c #B4B5B3","L   c #F4F4F4","M   c #E6E6E6","N   c #E8E8E8","O   c #777976","P   c #ABACAB","Q   c #B9CADC","R   c #6087B4","S   c #739FCE","T   c #C5CCD2","U   c #939592","V   c #898A88","W   c #6E6F6C","X   c #CECECE","Y   c #9F9F9F","Z   c #CDCCCB","`   c #DDDDDC"," .  c #6F706C","..  c #999A99","+.  c #DBE2E9","@.  c #96B3D2","#.  c #D5DCE4","$.  c #6A6B68","%.  c #B8B8B7","&.  c #858784","*.  c #747672","=.  c #6F716E","-.  c #858583",";.  c #C5C5C5",">.  c #F2F2F2",",.  c #B4B4B3","'.  c #7E7F7C",").  c #8D8E8D","!.  c #666764","~.  c #6D6C6B","{.  c #6D6E6B","].  c #B7B7B5","^.  c #898B88","/.  c #C6C6C6","(.  c #6C6D6A","_.  c #BBBBBB",":.  c #B9B9B9","<.  c #A6A7A5","[.  c #8B8D89","}.  c #A5A6A4","|.  c #8E8E8E","1.  c #CBCBCA","2.  c #D6D6D6","3.  c #ECECEC","4.  c #D7D7D7","5.  c #D8D8D8","6.  c #D1D1D1","7.  c #A9A9A9","8.  c #B2B2B1","9.  c #D4D4D4","                                ","      . . . . . . . . . . .     ","      . + @ # $ + + + + % .     ","      & * = - ; > , ' ' % .     ","      ) ! ~ { ] ^ ) / ( _ .     ","    : < [ } | 1 2 3 4 5 % .     ","    6 7 } 8 9 0 a b c d _ .     ","  e f g h i j k l m n e _ .     ","  o p q r s t u v w x y z A B B ","  C D E } F G H } I J K L M N B ","  B O P Q } R S T U V W X Y Z B ","  B `  ...+.@.#.$.%.&.*.=.-.;.B ","  B >.,.: '.).!.~.{.].^./.(.;.B ","  B >._.:.<.[.}.%.|.(.1.2.(.5 B ","  B 3.4.5.2.X 6.6.6.7.(.(.8.9.B ","  B B B B B B B B B B B B B B B "};
""",'document-save-as':
"""/* XPM */
static char * document_save_as_xpm[] = {
"16 16 95 2","      c None",".  c #38678B","+   c #3D698A","@   c #4A7180","#   c #58787A","$   c #B1CEE6","%   c #D0DFEF","&   c #C5DBEC","*   c #9BC2DF","=   c #688BA0","-   c #436E88",";   c #6B7F88",">   c #667173",",   c #627075","'   c #4A6D85",")   c #41749A","!   c #44789F","~   c #9EBFD9","{   c #C1D9EB","]   c #5186AF","^   c #4E6A7D","/   c #6E706B","(   c #6B716E","_   c #E2E6DD",":   c #FFFFFF","<   c #DDE1D6","[   c #C9D6DD","}   c #6E99B6","|   c #ABCBE2","1   c #92B7D3","2   c #547D9B","3   c #D5DFE5","4   c #F4F4F4","5   c #72756B","6   c #FDFDFD","7   c #EEEEEE","8   c #EDEDED","9   c #DFE2DE","0   c #7798B0","a   c #79A7CA","b   c #8FB3CE","c   c #3D6B8E","d   c #ACBCC3","e   c #EDEDEE","f   c #EDEEEE","g   c #EDEEED","h   c #F3F4F3","i   c #FCFBFC","j   c #EBECEC","k   c #5892BD","l   c #ECECEC","m   c #F3F3F3","n   c #FAFAFA","o   c #E9E9EA","p   c #CACFC4","q   c #98BFDC","r   c #719FBF","s   c #739FC0","t   c #96BBD8","u   c #95A9AF","v   c #EAE9EA","w   c #F2F2F2","x   c #F9F9F9","y   c #E4E4E4","z   c #C5CBBF","A   c #ABC8DF","B   c #92A6AC","C   c #F1F1F1","D   c #ACCBE3","E   c #3B6B8F","F   c #F7F7F7","G   c #E3E3E3","H   c #CED4C8","I   c #3F6C8E","J   c #9AAEB4","K   c #FCFCFC","L   c #F0F0F0","M   c #A3A4A1","N   c #A2A4A1","O   c #DCDCDC","P   c #DCDBDB","Q   c #DCDCDB","R   c #DCDBDC","S   c #DBDCDB","T   c #DBDCDC","U   c #000000","V   c #EFEFEF","W   c #AFB0AD","X   c #AEB0AE","Y   c #AFB0AE","Z   c #AEB0AD","`   c #EFEEEF"," .  c #EEEFEE","..  c #EEEEEF","+.  c #B7B8B6","      . . . + @ #               ","      $ % & * = -               ","; > , ' ) ! ~ { ] ^ / / / / / / ","( _ : < [ } . | 1 2 3 : : : 4 / ","5 6 7 8 9 0 . a b c d e f g h / ","/ i j . . . . a k . . . . l m / ","/ n o p . q r r r s t . u v w / ","/ x n y z . q s s A . B y 4 C / ","/ x 7 n y z . D q E B y n 7 C / ","/ F G 7 n n H I . J n K 7 G L / ","/ M N M M M M M M M M M M M M / ","/ O P Q O R Q R O S T U Q T O / ","/ V W X Y Z W W W W ` U  ...` / ","/ : +.+.+.+.+.+.+.+.: U : : : / ","/ : : : : : : : : : : U : : : / ","/ / / / / / / / / / / / / / / / "};
""",'document-save':
"""/* XPM */
static char * document_save_xpm[] = {
"16 16 107 2","     c None",".  c #38678B","+   c #3D698A","@   c #4A7180","#   c #58787A","$   c #B1CEE6","%   c #D0DFEF","&   c #C5DBEC","*   c #9BC2DF","=   c #688BA0","-   c #436E88",";   c #6B7F88",">   c #667173",",   c #627075","'   c #4A6D85",")   c #41749A","!   c #44789F","~   c #9EBFD9","{   c #C1D9EB","]   c #5186AF","^   c #4E6A7D","/   c #6E706B","(   c #6B716E","_   c #E2E6DD",":   c #FFFFFF","<   c #DDE1D6","[   c #C9D6DD","}   c #6E99B6","|   c #ABCBE2","1   c #92B7D3","2   c #547D9B","3   c #D5DFE5","4   c #F4F4F4","5   c #72756B","6   c #FDFDFD","7   c #EEEEEE","8   c #EDEDED","9   c #DFE2DE","0   c #7798B0","a   c #79A7CA","b   c #8FB3CE","c   c #3D6B8E","d   c #ACBCC3","e   c #EDEDEE","f   c #EDEEEE","g   c #EDEEED","h   c #F3F4F3","i   c #FCFBFC","j   c #EBECEC","k   c #5892BD","l   c #ECECEC","m   c #F3F3F3","n   c #FAFAFA","o   c #E9E9EA","p   c #CACFC4","q   c #98BFDC","r   c #719FBF","s   c #739FC0","t   c #96BBD8","u   c #95A9AF","v   c #EAE9EA","w   c #F2F2F2","x   c #F9F9F9","y   c #E4E4E4","z   c #C5CBBF","A   c #ABC8DF","B   c #92A6AC","C   c #F1F1F1","D   c #ACCBE3","E   c #3B6B8F","F   c #F7F7F7","G   c #E3E3E3","H   c #CED4C8","I   c #3F6C8E","J   c #9AAEB4","K   c #FCFCFC","L   c #F0F0F0","M   c #FEFEFE","N   c #EBEBEB","O   c #CECECE","P   c #C9C9C9","Q   c #C5C5C5","R   c #D6D6D6","S   c #9F9F9F","T   c #AFAFAF","U   c #BCBCBC","V   c #C4C4C4","W   c #C8C8C8","X   c #D0D0D0","Y   c #A9A9A9","Z   c #D2D2D2","`   c #B9B9B9"," .  c #CACACA","..  c #CDCDCD","+.  c #C3C3C3","@.  c #AAAAA9","#.  c #B4B4B4","$.  c #C2C2C2","%.  c #CBCBCB","&.  c #A8A7A8","*.  c #D1D1D1","=.  c #A8A7A7","-.  c #B7B6B6",";.  c #DDDDDD",">.  c #DCDCDC",",.  c #D5D5D5","'.  c #CFCFCF","      . . . + @ #               ","      $ % & * = -               ","; > , ' ) ! ~ { ] ^ / / / / / / ","( _ : < [ } . | 1 2 3 : : : 4 / ","5 6 7 8 9 0 . a b c d e f g h / ","/ i j . . . . a k . . . . l m / ","/ n o p . q r r r s t . u v w / ","/ x n y z . q s s A . B y 4 C / ","/ x 7 n y z . D q E B y n 7 C / ","/ F G 7 n n H I . J n K 7 G L / ","/ M : : : : : : : 4 4 N N G L / ","/ O P P P P Q P P Q Q Q Q Q R / ","/ O Q S T U V W X Y Z Y Z `  ./ ","/ ..+.@.#.$.V W %.&.*.=.*.-. ./ ","/ ;.>.>.>.,.,.'.'.'.'.'.'.'. ./ ","/ / / / / / / / / / / / / / / / "};
""",'document-open':
"""/* XPM */
static char * document_open_xpm[] = {
"16 16 137 2","     c None",".  c #565854","+   c #575955","@   c #595B57","#   c #5A5C58","$   c #5F615D","%   c #7A7A7A","&   c #797979","*   c #F7F7F7","=   c #F9F9F9","-   c #FAFAFA",";   c #FBFBFB",">   c #FCFCFC",",   c #A2A3A2","'   c #5B5C58",")   c #787878","!   c #C9C9C9","~   c #C7C7C7","{   c #C4C4C4","]   c #555753","^   c #DADADA","/   c #D3D3D3","(   c #D2D2D2","_   c #CFCFCF",":   c #CDCDCD","<   c #FEFEFE","[   c #939392","}   c #5B5E5A","|   c #737373","1   c #C5C5C5","2   c #B0B0B0","3   c #ACACAC","4   c #DCDCDC","5   c #9C9D9C","6   c #D5D5D4","7   c #FDFDFD","8   c #969796","9   c #5B5D59","0   c #6E6E6E","a   c #C1C1C0","b   c #AAAAAA","c   c #E2E2E2","d   c #DFDFDF","e   c #DEDEDE","f   c #DDDDDD","g   c #E0E0E0","h   c #E9E9E9","i   c #E5E5E5","j   c #D0D0D0","k   c #5D5F5B","l   c #6A6A6A","m   c #BDBDBD","n   c #A9A9A9","o   c #A5A5A5","p   c #E6E6E6","q   c #9FA09E","r   c #9C9D9B","s   c #E3E3E3","t   c #D0D1D0","u   c #656565","v   c #B7B7B7","w   c #A6A6A6","x   c #A1A1A1","y   c #EBEBEB","z   c #EAEAEA","A   c #E8E8E8","B   c #E7E7E7","C   c #D9D9D9","D   c #5B5C59","E   c #5F5F5F","F   c #B3B3B3","G   c #406CA5","H   c #3868A5","I   c #3768A5","J   c #3666A5","K   c #3566A5","L   c #3566A4","M   c #3465A4","N   c #3767A6","O   c #5B5B5B","P   c #AEAEAE","Q   c #C0D5EA","R   c #C1D5EA","S   c #C1D6EA","T   c #BBD2E8","U   c #3465A5","V   c #565656","W   c #C3D6EA","X   c #92B5DB","Y   c #95B8DC","Z   c #B9D0E7","`   c #3466A4"," .  c #515151","..  c #A5A5A4","+.  c #3666A4","@.  c #C5D7EB","#.  c #98B9DD","$.  c #95B7DC","%.  c #B8CEE7","&.  c #4C4C4C","*.  c #3767A5","=.  c #BFD2E9","-.  c #9BBADD",";.  c #9ABADD",">.  c #96B7DC",",.  c #8FB2DA","'.  c #8BB0D8",").  c #B1C9E4","!.  c #484848","~.  c #9B9B9B","{.  c #A5C1E1","].  c #8EB2D9","^.  c #8AAFD8","/.  c #85ACD7","(.  c #83AAD6","_.  c #81A9D5",":.  c #7EA7D4","<.  c #79A3D3","[.  c #77A2D2","}.  c #7BA5D3","|.  c #95B6DB","1.  c #3567A6","2.  c #494949","3.  c #999999","4.  c #3968A5","5.  c #94B5DB","6.  c #82AAD5","7.  c #7DA6D4","8.  c #7FA8D4","9.  c #85ABD5","0.  c #7E8896","a.  c #5588BF","b.  c #5689C0","c.  c #4B7EB7","d.  c #3667A6","e.  c #454A51","f.  c #3565A4","        . + . + + @ # $         ","% & & & . * = - ; ; > , '       ",") ! ~ { ] ^ / / ( _ : < [ }     ","| 1 2 3 ] 4 5 5 5 5 6 < 7 8 9   ","0 a 3 b . c d e e f g h i j k   ","l m n o . p q r r r f s s t 9   ","u v w x + y z z h h A A B C D   ","E F G H H I J J K L L L M M M N ","O P K Q Q Q Q Q Q R S S S S T U ","V n L W X X X X X X X X X Y Z ` "," ...+.@.#.#.#.#.#.#.#.#.#.$.%.K ","&.x *.=.-.;.;.;.;.;.;.>.,.'.).K ","!.~.H {.].^./.(._.:.<.[.[.}.|.1.","2.3.4.5.6.7.7.7.7.7.7.7.7.8.9.J ","!.0.4.a.b.b.b.b.b.b.b.b.b.b.c.d.","e.M M M M M M M M M M M M M f.  "};
""",'tab-new':
"""/* XPM */
static char * tab_new_xpm[] = {
"16 16 49 1","  c None",".  c #FFF416","+   c #FFF526","@   c #FFF52C","#   c #FFF418","$   c #FFF522","%   c #FFFA90","&   c #FFFA9B","*   c #FFF533","=   c #888A85","-   c #8B8D88",";   c #898B86",">   c #BBB751",",   c #F2EA36","'   c #F9F6A8",")   c #FAF7B8","!   c #F5EC46","~   c #A8AAA5","{   c #FDFDFD","]   c #FDFAB4","^   c #FEF653","/   c #FEF75C","(   c #FEF761","_   c #E7DF31",":   c #DFDFDB","<   c #D5D5D1","[   c #D3D3CF","}   c #E5E4C6","|   c #E6E4B7","1   c #FDF66A","2   c #A9A765","3   c #FCFBF6","4   c #F2F2F0","5   c #D6D6D2","6   c #F7F7F7","7   c #F0F0EF","8   c #D8D8D4","9   c #8A8C87","0   c #EDEDEB","a   c #D9D9D5","b   c #91938E","c   c #EBEBE9","d   c #DEDEDA","e   c #EDEDEC","f   c #949691","g   c #CACBC9","h   c #D2D3D1","i   c #DDDDD9","j   c #EAEAE9","                ","                ","           .+@# ","           $%&* ","  =--;;;==>,')! "," =~{{{{{{{]^/(_ "," ={:<[[[[[[}|12 "," ={<[[[[[[[[[3; "," =4<55555<<<<6; "," =7888888888879 "," =0aaaaaaaaaa79 ","=bcd:::::::::ef=","=ge::::::::::eh=","=eidddddd:::::7=","=7jeeeeejjjjjjj=","-;;;;;;;;;;;;;;-"};
""", 'media_playback_start':
"""/* XPM */
static char * media_playback_start_xpm[] = {
"16 16 58 1","  c None",".  c #464745","+   c #4C4D4A","@   c #4D4E4B","#   c #4A4B47","$   c #4B4C49","%   c #FBFBFB","&   c #B0B2AF","*   c #474745","=   c #4E4F4C","-   c #F2F3F0",";   c #E8E8E6",">   c #A3A4A2",",   c #50514E","'   c #464845",")   c #545551","!   c #F6F6F5","~   c #FAFBFA","{   c #F9F9F9","]   c #DEDEDD","^   c #9D9D9A","/   c #555754","(   c #595B57","_   c #ECEEEA",":   c #EEEFEC","<   c #EDEEEB","[   c #EBECE9","}   c #E6E7E5","|   c #959694","1   c #6C6E69","2   c #5E5F5C","3   c #E1E4DF","4   c #E1E3DE","5   c #E0E3DE","6   c #E5E7E3","7   c #F5F5F4","8   c #EBEBEA","9   c #949591","0   c #7F807C","a   c #646561","b   c #D7DAD3","c   c #DCDFDA","d   c #F6F7F6","e   c #F3F3F2","f   c #959592","g   c #6F716C","h   c #696B67","i   c #FBFBFA","j   c #FAFAF9","k   c #A6A7A4","l   c #797B77","m   c #F9FAF9","n   c #B3B5B1","o   c #858781","p   c #92958F","q   c #787A73","r   c #898A85","s   c #7E807A","                ","                ","   .            ","   +@#          ","   $%&$*        ","   =%-;>,'      ","   )%!~{]^/     ","   (%_::<[}|1   ","   2%34567890   ","   a%bcdefg     ","   hi!jkl       ","   gmnop        ","   qrs          ","   g            ","                ","                "};
""",'format_text_bold':
"""/* XPM */
static char * format_text_bold_xpm[] = {
"16 16 99 2","      c None",".  c #3566A4","+   c #3364A3","@   c #82A2C9","#   c #E7EEF6","$   c #E8EFF7","%   c #7D9EC6","&   c #3666A4","*   c #D0DDED","=   c #A8C3E1","-   c #6790C0",";   c #A1BEDC",">   c #B3C6DD",",   c #6287B8","'   c #DAE5F1",")   c #8CB0D6","!   c #3464A1","~   c #88ADD5","{   c #ACC1DB","]   c #4B75AC","^   c #35639F","/   c #AAC0D9","(   c #ACC5DF","_   c #6E95C3",":   c #34629F","<   c #648DC0","[   c #89ABD3","}   c #6F93C0","|   c #33619F","1   c #3A66A0","2   c #BFCFE0","3   c #8DB1D8","4   c #3F6BA6","5   c #3C69A5","6   c #719CCF","7   c #759BCB","8   c #2F5D9B","9   c #2F5C99","0   c #7796BE","a   c #9DB8D7","b   c #729ACB","c   c #2D5B99","d   c #2D5B98","e   c #5C8BC5","f   c #6090CB","g   c #406FAD","h   c #2C5A99","i   c #2C5896","j   c #94AFCF","k   c #7EA4D1","l   c #5E89BF","m   c #295694","n   c #4C7CBA","o   c #5688C9","p   c #4A7DC0","q   c #2A5795","r   c #4A71A6","s   c #85A7D0","t   c #6E9AD0","u   c #759FD2","v   c #89ADD9","w   c #9BB9DE","x   c #B0C7E5","y   c #C5D6EC","z   c #C6D6EC","A   c #4B80C6","B   c #497FC6","C   c #2F5E9E","D   c #295592","E   c #658BBC","F   c #6C97CD","G   c #6392CD","H   c #5E8ECB","I   c #598BCA","J   c #5487C9","K   c #4F83C7","L   c #4A80C6","M   c #3E71B5","N   c #275392","O   c #2B5691","P   c #6692CA","Q   c #5D8ECB","R   c #32609D","S   c #234F8C","T   c #2D5C9C","U   c #487EC5","V   c #265391","W   c #244F8C","X   c #416EAC","Y   c #588ACA","Z   c #4B7DBE","`   c #224D8B"," .  c #4377BD","..  c #3667A9","+.  c #234E8C","@.  c #224D8A","#.  c #204A87","$.  c #214C89","%.  c #224C8A","                                ","          . + + + + .           ","          @ # $ $ # %           ","        & * = - - ; > &         ","        , ' ) ! ! ~ { ]         ","      ^ / ( _ : : < [ } |       ","      1 2 3 4     5 6 7 8       ","    9 0 a b c     d e f g h     ","    i j k l m m m m n o p q     ","    r s t u v w x y z A B C     ","  D E F G H I J K L B B B M N   ","  O P Q R S S S S S S T B U V   ","W X Y Z `             `  .B ..+.","@.#.#.#.$.            %.#.#.#.%.","                                ","                                "};
"""}


class SelectX(QtGui.QMainWindow):

    def __init__(self, ForseEmbededIcons = None, ok = 0):
        super(SelectX, self).__init__()
        #pixmap = QtGui.QPixmap()
        #pixmap.loadFromData(TANGO_ICONS["edit-select-all"])
        #splashScreen = QtGui.QSplashScreen(pixmap)
        #init class constants
        self.ok = ok
        self.nonPrintFlag = True
        self.newDocNumber = 0
        self.path = os.getenv('HOME')
        self.selectForCopyByWords = False
        self.startPath = os.getenv('HOME')
        if ForseEmbededIcons:
            self.useThemeIcons = False
        else:
            self.useThemeIcons = True
            
        self.okRun = False
        self.text_url = False
        self.wordsForSelect = 2

        self.initUI()
        try:
            if len(sys.argv)<3:
                if not sys.argv[1]=='--ok':
                    print _(u'Try Open This File -> %s') % sys.argv[1]
                    self.openExistFile(sys.argv[1])
            else:
                print _(u'Too many args')
                print CONSOLE_USAGE
        except IndexError:
            #print 'not open File'
            pass

        #splashScreen.close()
        #self.installEventFilter(self)
        global TANGO_ICONS
        TANGO_ICONS = None

    def initUI(self):
        self.MenuBar = self.makeMenu()

        self.statusBar()
        self.setGeometry(100, 100, 400, 400)
        self.setWindowIcon(self.getNewIcon("edit-select-all"))
        self.setMinimumSize(200,150)
        self.setWindowTitle(_(u'SelectX'))
        self.mainTab = QtGui.QTabWidget(self)
        self.mainTab.setTabsClosable(True)
        self.mainTab.setMovable(True)
        self.setCentralWidget(self.mainTab)
        self.cWidget=TextEditX(parent=self)
        tabId = self.mainTab.addTab(self.cWidget, _(u"New Text"))
        self.mainTab.tabCloseRequested.connect(self.closeTab)
        self.mainTab.currentChanged.connect(self.changeTab)

        self.setHighlighter()
        self.changeTab(tabId)
        self.show()
        

    def removeTab(self, index):
        widget = self.mainTab.widget(index)
        if widget is not None:
            widget.deleteLater()
        self.mainTab.removeTab(index)

    def wheelEvent(self, event):
        if  event.modifiers()==0x04000000 or event.modifiers()==QtCore.Qt.CTRL or event.modifiers()==QtCore.Qt.ControlModifier:
            if event.delta()>0:
                self.viewZoomIn()
                return True
                #event.ignore()
            else:
                self.viewZoomOut()
                return True
                #event.ignore()

    def checkPluginsDir(self, plugDir):
        #if not  os.path.isfile(plugDir+'SelectX_simpley_find.py'):
        FIND_PY = r"""from selectx import localGettextX as localGettextX
from selectx import QtGui as QtGui

_ = localGettextX()

__plugin_name__ = _(u'SelectX_Find_Dialog')
__plugin_menu_caption__ = _(u'SelectX Find Dialog')
__plugin_menu_key__ = 'F7'
__plugin_menu_help__ = _(u'SelectX Find Dialog')
__plugin_menu_icon__ = 'edit-find'
__plugin_version__ = '0.0.4'
__plugin_about__ = _(u'Enter text to find:')

def __plugin_init__(self, params_list=[]):
    nnn = __plugin_name__+' '+__plugin_version__
    #print nnn
    self.statusBar().showMessage(nnn)

def __plugin_run_function__(self):
    findText(self)

def findText(self):
    #print 'findText(self-'+str(self)
    cursor = self.cWidget.edit.textCursor()
    textSelected = cursor.selectedText()
    text_find, find_ok = QtGui.QInputDialog.getText(self, \
    _(u'SelectX Find Dialog'), _(u'Enter text to find:'), QtGui.QLineEdit.Normal,  textSelected)
    if find_ok:
        if self.cWidget.edit.find(str(text_find)):
            self.statusBar().showMessage(_(u'Found: %s') % text_find)
            return
        else:
            self.statusBar().showMessage(_(u'Not found: %s') % text_find)
            return
        return
    self.statusBar().showMessage(_(u'Find Canceled'))

"""
        if writeIfNotSame (plugDir+'SelectX_simpley_find.py', FIND_PY):
            import py_compile
            py_compile.compile(plugDir+'SelectX_simpley_find.py')
        RUN_PY = r"""#!/usr/bin/env python
# -*- coding: utf-8 -*-

from selectx import localGettextX as localGettextX

_ = localGettextX()

__plugin_name__ = _(u'SelectX_Run_Python')
__plugin_menu_caption__ = _(u'Run Python Script')
__plugin_menu_key__ = 'F5'
__plugin_menu_help__ = _(u'SelectX Run Python Script from current tab')
__plugin_menu_icon__ = '''applications_system'''
__plugin_version__ = '0.1.2'
__plugin_about__ = _(u'Run Python Script from current tab')

def __plugin_init__(self, params_list=[]):
    nnn = __plugin_name__+' '+__plugin_version__
    #print nnn
    self.statusBar().showMessage(nnn)

def __plugin_run_function__(self):
    py_run(self)

def py_run(self, py_name=r'./hi.py', run_params=' '):
    import os
    if self:
        #print 'py_run(self-'+str(self)
        if self.cWidget.edit.filePath:
            py_name = self.cWidget.edit.filePath
        else:
            print _(u'You try to run not saved code. Saved code 1st.')
            return False
    if os.name in ['nt',]:
        status = os.system(r'start cmd /C "python ' + py_name + run_params+r''' &&  pause"''')
    else:
        status = os.system(r'xterm  -e "python ' + py_name + run_params+r''' && echo 'Waiting for press Enter key.' && read"''')
    #print 'status - %s'%status
    return status

if __name__ == "__main__":
    py_run(0)
"""
        if writeIfNotSame (plugDir+'SelectX_run_py.py', RUN_PY):
            import py_compile
            py_compile.compile(plugDir+'SelectX_run_py.py')

    def makeMenu(self):
        menubar = self.menuBar()

        self.toolbar = self.addToolBar(_(u"File"))
        self.toolbar.setMovable(True)

        fileMenu = menubar.addMenu(_(u'&File'))
        #self.addActionParamX(_(u'New'), 'Ctrl+N', _(u'Create new file'), self.newFile, \
        #fileMenu, 'document-new', self.toolbar)
        self.addActionParamX(_(u'New Tab'), 'Ctrl+T', _(u'Create new tab'), self.newTab, \
        fileMenu, 'tab-new', self.toolbar)
        #self.addActionParamX(_(u'Open in new tab'), 'Ctrl+Shift+O', _(u'Set open a file in new tab'), self.setOpenInNewTab, \
        #fileMenu, 'document-open', checkAble=True)
        self.addActionParamX(_(u'Open'), 'Ctrl+O', _(u'Open a file'), self.openFile, \
        fileMenu, 'document-open', self.toolbar)
        self.addActionParamX(_(u'Save'), 'Ctrl+S', _(u'Save current file'), \
        self.saveFile, fileMenu, 'document-save', self.toolbar)
        self.addActionParamX(_(u'Save As...'), 'Ctrl+Shift+S', _(u'Save as new file'), \
        self.saveFileAs, fileMenu, 'document-save-as', self.toolbar)
        fileMenu.addSeparator()
        self.addActionParamX(_(u'Preview'), 'Ctrl+L', _(u'File Preview'), \
        self.filePreview, fileMenu, 'document-print-preview', self.toolbar)
        self.addActionParamX(_(u'Print'), 'Ctrl+P', _(u'File Print'), \
        self.filePrint, fileMenu, 'document-print', self.toolbar)
        fileMenu.addSeparator()
        self.addActionParamX(_(u'Close Tab'), 'Ctrl+Shift+Q', _(u'Close current tab'), \
        self.closeTab, fileMenu, 'window-close')
        self.addActionParamX(_(u'Exit'), 'Ctrl+Q', _(u'Exit SelectX'), \
        self.checkExitProgram, fileMenu, 'application-exit')

        self.toolbar = self.addToolBar(_(u"Edit"))
        self.toolbar.setMovable(True)
        editMenu = menubar.addMenu(_(u'&Edit'))
        self.addActionParamX(_(u'Undo'), 'Ctrl+Z', _(u'Undo last text edit'), \
        self.undoText, editMenu, 'edit-undo', self.toolbar)
        self.addActionParamX(_(u'Redo'), 'Ctrl+Y', _(u'Redo last text edit'), \
        self.redoText, editMenu, 'edit-redo', self.toolbar)
        editMenu.addSeparator()
        self.addActionParamX(_(u'Copy'), 'Ctrl+C', _(u'Copy selected text'), \
        self.copyText, editMenu, 'edit-copy', self.toolbar)
        self.addActionParamX(_(u'Cut'), 'Ctrl+X', _(u'Cut selected text'), \
        self.cutText, editMenu, 'edit-cut', self.toolbar)
        self.addActionParamX(_(u'Paste'), 'Ctrl+V', _(u'Paste text'), self.pasteText, \
        editMenu, 'edit-paste', self.toolbar)
        editMenu.addSeparator()
        self.addActionParamX(_(u'Find and replace'), 'Ctrl+F', _(u'Find and replace words in your document'), FindDialog(self).show, \
        editMenu, 'edit-find-replace', self.toolbar)

        self.toolbar = self.addToolBar(_(u"Select"))
        self.toolbar.setMovable(True)
        selectMenu = menubar.addMenu(_(u'&Select'))
        self.addActionParamX(_(u'Select All'), 'Ctrl+A', _(u'Select all text in editor'), \
        self.selectAll, selectMenu, 'edit-select-all', self.toolbar)
        self.addActionParamX(_(u'Select For Copy By Words'), 'Ctrl+Shift+A', _(u'Set Select For Copy By Words'), \
        self.setSelectByWords, selectMenu, 'edit-select', None, checkAble=True)

        self.toolbar = self.addToolBar(_(u"View"))
        self.toolbar.setMovable(True)
        viewMenu = menubar.addMenu(_(u'&View'))
        
        highlighterSubmenu = QtGui.QMenu(viewMenu)
        highlighterSubmenu.setTitle(_(u"&Highlighter"))
        viewMenu.addMenu(highlighterSubmenu)
        self.highlighterGroup = QtGui.QActionGroup(self, exclusive=True)
        self.nonHi = self.addActionParamX(_(u'None'), False, _(u'None Highlighter'), \
        self.putHighlighter, highlighterSubmenu,  False, None, 
        True, True, True, self.highlighterGroup)
        self.cppHi = self.addActionParamX(_(u'Cpp'), False, _(u'Cpp Highlighter'), \
        lambda: self.putHighlighter('cpp'), highlighterSubmenu, False, None, 
        True, False, True, self.highlighterGroup)
        self.pyHi = self.addActionParamX(_(u'Python'), False, _(u'Python Highlighter'), \
        lambda: self.putHighlighter('py'), highlighterSubmenu, False, None, 
        True, False, True, self.highlighterGroup)
        
        zoomSubmenu = QtGui.QMenu(viewMenu)
        zoomSubmenu.setTitle(_(u"&Zoom"))
        viewMenu.addMenu(zoomSubmenu)
        self.addActionParamX(_(u'Zoom In'), 'Ctrl++', _(u'Zoom In text in editor'), \
        self.viewZoomIn, zoomSubmenu, 'zoom-in', self.toolbar)
        self.addActionParamX(_(u'Zoom Out'), 'Ctrl+-', _(u'Zoom Out text in editor'), \
        self.viewZoomOut, zoomSubmenu, 'zoom-out', self.toolbar)
        self.addActionParamX(_(u'Zoom Original'), 'Ctrl+0', _(u'Zoom original text in editor'), \
        self.viewZoomOriginal, zoomSubmenu, 'zoom-original', self.toolbar)
        viewMenu.addSeparator()
        self.addActionParamX(_(u'Font'), 'F8', _(u'Font select dialog'), \
        self.viewFont, viewMenu, 'preferences-desktop-font', self.toolbar)
        viewMenu.addSeparator()
        self.nonPrintOn = self.addActionParamX(_(u'Show/Hide non-printabale'), 'Ctrl+H', _(u'Show/Hide non-printabale symbols'), self.inverseNonPrintabale, \
        viewMenu, 'media_record', self.toolbar, checkAble=True, returnName=True)
        self.nonPyEnter = self.addActionParamX(_(u'Pythonic Enter'), 'Ctrl+Shift+P', _(u'On/Off Pythonic Enter Style'), self.inversePyEnter, \
        viewMenu, 'media_skip_backward', self.toolbar, checkAble=True, returnName=True)
        self.nonLineNumbers = self.addActionParamX(_(u'Line Numbers'), 'Ctrl+Shift+L', _(u'On/Off PLine Numbers'), self.inverseLineNumbering, \
        viewMenu, 'office_calendar', self.toolbar, checkAble=True, returnName=True)
        
        self.addPlugins(menubar)

        self.toolbar = self.addToolBar(_(u"Help"))
        self.toolbar.setMovable(True)
        helpMenu = menubar.addMenu(_(u'&Help'))
        self.addActionParamX(_(u'Help'), 'F1', _(u'Keys Help'), self.keyHelp, helpMenu, \
        'help-contents', self.toolbar)
        self.addActionParamX(_(u'About'), 'F9', _(u'About editor'), self.aboutHelp, \
        helpMenu, 'help-about')
        self.addActionParamX(_(u"About &Qt"), 'Shift+F9', _(u'About current QT'), QtGui.qApp.aboutQt, \
        helpMenu, 'help-about')
        self.okPlay = self.addActionParamX(_(u'Ok Player'), 'Ctrl+Shift+F12', _(u'On/Off Ok Player'), self._okPlayer, \
        helpMenu, 'media_playback_start', self.toolbar, checkAble=True, returnName=True)
        self.okPlay.setEnabled(self.ok>9)
        self.okPlay.setVisible(self.ok>9)
        self.okVolume = self.addActionParamX(_(u'Ok Volume'), 'Ctrl+Shift+F11', _(u'Volume Ok Player'), self._setOkVolume, \
        helpMenu, 'media_playback_start', self.toolbar, checkAble=False, returnName=True)
        self.okVolume.setEnabled(False)
        self.okVolume.setVisible(False)
        


        return menubar

    def _setOkVolume(self):
        if self.ok>9:
            VolumeDialog(self, self.aOutput)
            #if LIB_USE == "PySide":
                #from PySide.phonon import Phonon
            #else:
                #from PyQt4.phonon import Phonon
            #newOkVolume = Phonon.VolumeSlider(self.aOutput, self)
            #print str(newOkVolume)
            
        #self.aOutput = Phonon.AudioOutput()
        #self.aOutput.setMuted(False)
        #self.aOutput.setVolume(10)
                

    def addPlugins(self, menuLink):
        pluginsDir = gluePath([__baseDir__, '.config', 'SelectX', 'Plugins', ''])
        self.checkPluginsDir(pluginsDir)
        dictPlugs = {}
        for fff in os.listdir(pluginsDir):
            plugExt = fff.split('.')[-1]
            plugName= fff[:-len(plugExt)-1]
            #print plugName, plugExt
            if plugExt == 'py':
                dictPlugs[plugName] = plugExt
            elif plugExt == 'pyc':
                if not plugName in dictPlugs.keys():
                    dictPlugs[plugName] = plugExt
            elif plugExt == 'dll' or plugExt == 'so':
                dictPlugs[plugName] = plugExt
                    
        if dictPlugs:
            PluginsMenu = menuLink.addMenu(_(u'&Plugins'))
            self.plugins=[]
            
        for ppp in dictPlugs.keys():
            if dictPlugs[ppp] in ['py', 'pyc']:
                self.importPlugin(ppp, PluginsMenu, pluginsDir, dictPlugs[ppp])
            elif dictPlugs[ppp] in ['so', 'dll']:
                self.importBinPlugin(ppp, PluginsMenu, pluginsDir, dictPlugs[ppp])

    def importPlugin(self, pluginname, plugMenu, pluginpath='', pluginType='.py'):
        import imp
        plug = imp.load_source(pluginname, pluginpath+pluginname+'.'+pluginType)
        #print plug
        plug.__plugin_init__(self)
        
        
        self.plugins.append(plug)

        if plug.__plugin_menu_caption__ and \
        plug.__plugin_menu_key__ and \
        plug.__plugin_menu_help__ and \
        plug.__plugin_run_function__:
            self.addActionParamX(plug.__plugin_menu_caption__, \
            plug.__plugin_menu_key__, \
            plug.__plugin_menu_help__, \
            lambda: plug.__plugin_run_function__(self), \
            plugMenu, \
            plug.__plugin_menu_icon__)
            
        else:
            print "import pass %s, %s, %s, %s"% plug.__plugin_menu_caption__, \
            plug.__plugin_menu_key__, \
            plug.__plugin_menu_help__, \
            plug.__plugin_run_function

    def importBinPlugin(self, pluginname, plugMenu, pluginpath='', pluginType='.so'):
        from ctypes import CDLL, c_char_p
        get_lib = CDLL(pluginpath+pluginname+'.'+pluginType)
        
        sss=c_char_p('hi from python\n')
        kk10=get_lib.plugin_init(sss)
        #print 'python plugin_init='+str(kk10)
        sss=c_char_p('run from python\n')
        init_function=get_lib.plugin_run_function(sss)
        self.plugins.append(init_function)
        
        run_function = get_lib.plugin_run_function
        run_function.restype = c_char_p
        #print 'python plugin_init='+str(run_function)
    
        self.addActionParamX("Bin plugin#"+str(len(self.plugins))+'-'+pluginname, \
            "", \
            "SelectX bin plugin#"+str(len(self.plugins)), \
            lambda: self.statusBar().showMessage(str(run_function(c_char_p(str(self))))), \
            plugMenu, \
            'applications_system')
            

    def addActionParamX(self, ActText, ActSortcut, ActTip, ActConnect, \
    TopActLevel, IconName=None, toolBar=None, checkAble=False, \
    checkState=False, returnName=False, ActionGroupName=False):
        if IconName:
            newIcon =  self.getNewIcon(IconName)
            MakeAct = QtGui.QAction(newIcon, ActText, self)
        else:
            MakeAct = QtGui.QAction(ActText, self)
        if checkAble:
            MakeAct.setCheckable (True)
            MakeAct.setChecked (checkState)
        MakeAct.setIconVisibleInMenu (True)
        if ActSortcut:
            MakeAct.setShortcut(ActSortcut)
        MakeAct.setStatusTip(ActTip)
        MakeAct.triggered.connect(ActConnect)
        
        if ActionGroupName:
            MakeAction = ActionGroupName.addAction(MakeAct)
        else:
            MakeAction = MakeAct
        
        TopActLevel.addAction(MakeAction)

        if toolBar:
            toolBar.addAction(MakeAction)

        if returnName:
            return MakeAction

    def inversePyEnter(self):
        currentWidget = self.cWidget.edit
        if currentWidget.pythonicEnterOn:
            currentWidget.pythonicEnterOn = False
            self.statusBar().showMessage(_(u'Hide Py Enter'))
        else:
            currentWidget.pythonicEnterOn = True
            self.statusBar().showMessage(_(u'Add Py Enter'))

    def getNewIcon(self, IconName):
        newIcon = QtGui.QIcon.fromTheme(IconName)
        if self.useThemeIcons and newIcon.hasThemeIcon(IconName):
        #if False:
            #print 'has in theme '+IconName #debug prints to find missing icons
            pass
        else:
            if IconName in TANGO_ICONS:
                newPixmap = QtGui.QPixmap()
                #print TANGO_ICONS[IconName]
                newPixmap.loadFromData(TANGO_ICONS[IconName])
                newIcon = QtGui.QIcon(newPixmap)
                #print 'has in file '+IconName
            else:
                #print 'has not '+IconName
                pass
        #print 'newIcon - '+str(newIcon)
        return newIcon


    def setHighlighter(self):
        if self.path:
            extention = getFileName(self.path, '.').lower()
            self.putHighlighter(extention)
        
    def putHighlighter(self, extention = None):
        if extention in ['c', 'cc','cpp', 'c++', 'cxx', 'h', 'hh', 'hpp', 'hxx']:
            if self.cWidget.edit.highlighterType:
                self.cWidget.edit.highlighter.setDocument(None)
            self.cWidget.edit.highlighter = Highlighter(self.cWidget.edit.document(), extention)
            self.cWidget.edit.highlighterType = 'cpp'
            self.cppHi.setChecked(True)
        elif extention in ['py', 'py3']:
            if self.cWidget.edit.highlighterType:
                self.cWidget.edit.highlighter.setDocument(None)
            self.cWidget.edit.highlighter = PythonHighlighter(self.cWidget.edit.document())
            self.cWidget.edit.highlighterType = 'python'
            self.pyHi.setChecked(True)
        elif self.cWidget.edit.highlighterType:
            self.cWidget.edit.highlighter.setDocument(None)
            self.cWidget.edit.highlighter = None
            self.cWidget.edit.highlighterType = None
            self.nonHi.setChecked(True)
            #print "set-"+self.cWidget.edit.highlighterType
        else:
            pass
            

    def newFile(self):
        self.cWidget.edit.clear()
        self.path=None
        self.statusBar().showMessage(_(u'New Text'))
        self.setWindowTitle(_(u'SelectX'))

    def newTab(self):
        self.newDocNumber += 1
        self.cWidget = TextEditX(parent=self)
        
        tabId = self.mainTab.addTab(self.cWidget, _(u"New text - %s")%self.newDocNumber)
        self.mainTab.setCurrentWidget(self.cWidget)
        self.setHighlighter()
        self.changeTab(tabId)

    def changeTab(self, tabIndex):
        self.cWidget=self.mainTab.currentWidget()
        bar = self.cWidget.number_bar
        
        edit = self.cWidget.edit
        doc = edit.document()
        if doc.defaultTextOption().flags():
            self.nonPrintOn.setChecked(True)
        else:
            self.nonPrintOn.setChecked(False)
        if edit.pythonicEnterOn:
            self.nonPyEnter.setChecked(True)
        else:
            self.nonPyEnter.setChecked(False)
        if bar.paintLineNumber:
            self.nonLineNumbers.setChecked(True)
        else:
            self.nonLineNumbers.setChecked(False)
        if self.cWidget.edit.highlighterType == 'python':
            self.pyHi.setChecked(True)
            self.cppHi.setChecked(False)
            self.nonHi.setChecked(False)
        elif self.cWidget.edit.highlighterType == 'cpp':
            self.cppHi.setChecked(True)
            self.pyHi.setChecked(False)
            self.nonHi.setChecked(False)
        else:
            self.nonHi.setChecked(True)
            self.cppHi.setChecked(False)
            self.pyHi.setChecked(False)
        self.statusBar().showMessage(_(u'Selected Tab #%s') % (tabIndex+1))

    def closeTab(self, tabIndex):
        if self.mainTab.count()==1:
            return -1
        if self.mainTab.widget(tabIndex).edit.document().isModified():
            if self.checkCloseTab(tabIndex):
                self.removeTab(tabIndex)
                return tabIndex
        else:
            self.removeTab(tabIndex)
            return tabIndex

    def saveFile(self):
        if self.path:
            #f = open(self.path, 'w')
            try:
                with codecs.open(self.path, 'w', self.cWidget.edit.encodingSet) as f:
                    filedata = self.cWidget.edit.document().toPlainText()
                    #filedata = codecs.encode(filedata, 'utf8')
                    f.write(filedata)
                    f.close()
                    self.statusBar().showMessage(_(u'Save Text: %s') % self.path)
                    pass
                #f = open(self.path, 'w')
            except IOError:
                self.saveFileAs()
        else:
            self.saveFileAs()

    def saveFileAs(self):
        if not self.startPath:
            self.startPath = './'
        filename = QtGui.QFileDialog.getSaveFileName(self, _(u'Save File'), \
        self.startPath)
            
        #print str(filename)
        if filename:
            if type(filename) is tuple:
                if filename[0] <> u'':
                    #print 'type(filename)-'+str(filename)
                    filename = filename[0]
                else:
                    self.statusBar().showMessage(_(u'Stop Save Text'))
                    return
            self.path = filename
            try:
                with codecs.open(self.path, 'w', self.cWidget.edit.encodingSet) as f:
                    filedata = self.cWidget.edit.document().toPlainText()
                    #filedata = codecs.encode(filedata, 'utf8')
                    f.write(filedata)
                    f.close()
                    self.statusBar().showMessage(_(u'Save Text: %s') % self.path)
                    pass
                #f = open(self.path, 'w')
                #f = open(self.path, 'w')
            except IOError:
                return self.path
            #filedata = self.cWidget.edit.toPlainText()
            #f.write(filedata)
            #f.close()
            #self.path = filename
            self.startPath = self.path[:-len(getFileName(self.path))]
            self.statusBar().showMessage(_(u'Save Text: %s') % filename)
            self.setWindowTitle(_(u'SelectX - %s') % filename)
            curtabind = self.mainTab.currentIndex()

            self.mainTab.setTabToolTip (curtabind, '%s' % self.path)
            newFileName =  getFileName(self.path)
            self.mainTab.setTabText(curtabind, '%s' % newFileName)
            self.setHighlighter()
            self.cWidget.edit.filePath = newFileName
        else:
            self.statusBar().showMessage(_(u'Stop Save Text'))

    def setOpenInNewTab(self):
        self.openInNewTab = not(self.openInNewTab)
        print self.openInNewTab

    def openFile(self):
        ###to see http://www.rkblog.rk.edu.pl/w/p/simple-text-editor-pyqt4/
        if not self.startPath:
            #for windows
            self.startPath = './'
        self.path = QtGui.QFileDialog.getOpenFileName(self, _(u'Open File'), \
        self.startPath, \
         _(u"All Files (*);;Text Files (*.txt *.log *.TXT *.LOG);;Python Files (*.py *.PY *.py3 *.PY3);;C/C++ Files (*.c *.cc *.cpp *.c++ *.cxx *.h *.hh *.hpp *.hxx *.CPP *.H *.c *.C)") \
        )

        if self.path:
            if type(self.path) is tuple: #for PySide
                self.path = self.path[0]
                #print self.path

            self.startPath = self.path[:-len(getFileName(self.path))]
            if self.checkNotEmptyText() and self.path:
                self.newTab()
                self.statusBar().showMessage(_(u'Start reading: %s') % self.path)
                
            if self.path<>u'':
                self.openExistFile(self.path)
        else:
            self.statusBar().showMessage(_(u'Stop Open Text'))
        #if self.path:
            #print
            #if type(self.path) is tuple: #for PySide
                #if self.checkNotEmptyText():
                    #self.path = self.path[0]
                ##print self.path

            #self.startPath = self.path[:-len(getFileName(self.path))]
            #if self.checkNotEmptyText():
                #self.newTab()
            #self.openExistFile(self.path)
        #else:
            #self.statusBar().showMessage(_(u'Stop Open Text'))

    def checkNotEmptyText(self):
        if len(self.cWidget.edit.toPlainText()) > 0:
            return True
        return False

    def openExistFile(self, filePath):
        self.statusBar().showMessage(_(u'Start reading: %s') % self.path)
        self.path = filePath
        inFile = QtCore.QFile(self.path)
        
        with codecs.open(self.path, 'r', self.cWidget.edit.encodingSet) as inFile:
        #with codecs.open(self.path, 'r', 'koi8-r') as inFile:
        #with codecs.open(self.path, 'r', 'windows_1251') as inFile:
            text = inFile.read()
            #content = inFile.readlines()
            #text = ''
            #for lll in content:
                #text += lll
        #if inFile.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
            #text = inFile.readAll()
            #text = inFile.readAll()
            #inFile.close()
            inFile.close()
            #try:
                #print 1
                ## Python v3.
                ##text = str(text, encoding='windows_1251')
                ##text = str(text, encoding='ascii')
                
                #text = str(text, encoding='utf-8')
            #except TypeError:
                #print 2
                ## Python v2.
                #text = str(text)
                
            #text = str(text)
                
            #self.cWidget.edit.clear()
            self.setHighlighter()
            self.cWidget.edit.setPlainText(text)
            
            self.statusBar().showMessage(_(u'Open Text: %s') % self.path)
            curtabind = self.mainTab.currentIndex()

            self.mainTab.setTabToolTip (curtabind, '%s' % self.path)
            self.mainTab.setTabText(curtabind, '%s' % getFileName(self.path))
            self.setWindowTitle(_(u'SelectX - %s') % self.path)
            self.cWidget.edit.filePath = self.path
        #else:
            #print 'Can Not Open This File -> %s' % self.path
            #self.path = None

    def filePreview(self):
        '''Open preview dialog'''
        preview = QtGui.QPrintPreviewDialog()
        preview.paintRequested.connect(lambda p: self.cWidget.edit.print_(p))
        preview.exec_()

    def filePrint(self):
        '''Open printing dialog'''
        dialog = QtGui.QPrintDialog()
        if dialog.exec_() == QtGui.QDialog.Accepted:
            self.cWidget.edit.document().print_(dialog.printer())

    def checkExitProgram(self):
        reply_exit = QtGui.QMessageBox.question(self, _(u'Confirm Exit SelectX'), \
        _(u"Are you sure to Exit?"), QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, \
        QtGui.QMessageBox.No)
        if reply_exit==QtGui.QMessageBox.Yes:
            self.close()
        self.statusBar().showMessage(_(u'Close Stoped'))

    def checkCloseTab(self, idTab=None):
        reply_exit = QtGui.QMessageBox.question(self, _(u'Confirm Close Tab'), \
        _(u"Are you sure to Close Tab?"), QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, \
        QtGui.QMessageBox.No)
        if reply_exit==QtGui.QMessageBox.Yes:
            return True
        return False

    def undoText(self):
        self.cWidget.edit.undo()
        self.statusBar().showMessage(_(u'Undo Text'))

    def redoText(self):
        self.cWidget.edit.redo()
        self.statusBar().showMessage(_(u'Redo Text'))

    def wordsCountDialog(self):
        
        wordsCount, wordsCount_ok = QtGui.QInputDialog.getText(self, \
        _(u'Enter words number'), _(u'Enter words number for copy:'), QtGui.QLineEdit.Normal,  str(self.wordsForSelect))
        #_(u'Enter words number'), _(u'Enter words number for copy:'),spinnerQ)
        if wordsCount_ok:
            self.wordsForSelect = int(wordsCount)
        wordsCount = self.wordsForSelect
                
    def copyText(self):
        cursor = self.cWidget.edit.textCursor()
        if cursor.hasSelection():
            if self.selectForCopyByWords:
                wordsCount = self.wordsForSelect
                wordsSpliter = ' '
                if u'\u2029' in cursor.selectedText():
                    selectedRows=cursor.selectedText().split(u'\u2029')
                else:
                    selectedRows=cursor.selectedText().split('\n')
                resultString = ''
                for rrr in selectedRows:
                    wordsInRow = rrr.split(wordsSpliter)
                    if len(wordsInRow)>wordsCount:
                        nnn = 0
                        while nnn < wordsCount:
                            resultString += wordsInRow[nnn]+wordsSpliter
                            nnn += 1
                        resultString += '\n'
                    else:
                        resultString += rrr+'\n'
                    
                clipQ = QtGui.QClipboard()
                clipQ.setText(resultString)
    
            else:
                self.cWidget.edit.copy()
            self.statusBar().showMessage(_(u'Copy Text'))

    def cutText(self):
        self.cWidget.edit.cut()
        self.statusBar().showMessage(_(u'Cut Text'))

    def pasteText(self):
        self.cWidget.edit.paste()
        self.statusBar().showMessage(_(u'Paste Text'))

    def inverseNonPrintabale(self):
        edit = self.cWidget.edit
        doc = edit.document()
        option = QtGui.QTextOption()
        if doc.defaultTextOption().flags():
            option.setFlags(QtGui.QTextOption.Flag())
            self.statusBar().showMessage(_(u'Hide Non Printabale'))
        else:
            option.setFlags(QtGui.QTextOption.ShowTabsAndSpaces)
            self.statusBar().showMessage(_(u'Show Non Printabale'))
        doc.setDefaultTextOption(option)

    def inverseLineNumbering(self):
        bar = self.cWidget.number_bar
        bar.paintLineNumber = not bar.paintLineNumber
        if bar.paintLineNumber:
           self.statusBar().showMessage(_(u'Show Line Numbers'))
        else:
            self.statusBar().showMessage(_(u'Hide Line Numbers'))
        bar.update()

    def selectAll(self):
        self.cWidget.edit.selectAll()
        #self.statusBar().showMessage(_(u''Select All Text'))
        self.cursorPosition()

    def setSelectByWords(self):
        self.selectForCopyByWords = not(self.selectForCopyByWords)
        if self.selectForCopyByWords:
            self.wordsCountDialog()

    def viewZoomIn(self):
        currentw = self.cWidget.edit
        currentw.zoomIn(1)
        currentw.zoomRate += 1
        self.statusBar().showMessage(_(u'Zoom Rate: %s') % currentw.zoomRate)

    def viewZoomOut(self):
        currentw = self.cWidget.edit
        currentw.zoomOut(1)
        currentw.zoomRate -= 1
        self.statusBar().showMessage(_(u'Zoom Rate: %s') % currentw.zoomRate)

    def viewZoomOriginal(self):
        currentw = self.cWidget.edit
        currentw.zoomIn(-currentw.zoomRate)
        currentw.zoomRate = 0
        self.statusBar().showMessage(_(u'Zoom Rate: %s') % currentw.zoomRate)

    def viewFont(self):
        font, ok = QtGui.QFontDialog.getFont(self.cWidget.edit.qFont, self)
        if ok:
            self.cWidget.edit.qFont = font
            self.viewZoomOriginal()
            self.cWidget.edit.setFont(font)
            self.statusBar().showMessage('Font set: %s' % font.toString())

    def _okPlayer(self):
        self.okRun = not self.okRun
        if not self.text_url: # my favorit on-line radio ;)
            #self.text_url = """http://online-radiomelodia.tavrmedia.ua/RadioMelodia"""
            self.text_url = """http://cast2.retro.ua/retro_romantic"""
                
        if self.okRun:
            self.text_url, play_ok = QtGui.QInputDialog.getText(self, \
            _(u'Enter media URL'), \
            _(u'Enter you favorit on-line radio URL:'), \
            QtGui.QLineEdit.Normal, \
            self.text_url)
            if play_ok:
                #from PySide.phonon import Phonon
                global Phonon
                if LIB_USE == "PySide":
                    from PySide.phonon import Phonon as Phonon
                else:
                    from PyQt4.phonon import Phonon as Phonon
                    #pass
                self.okVolume.setEnabled(True)
                self.okVolume.setVisible(True)
        
                self.aOutput = Phonon.AudioOutput(Phonon.MusicCategory)
                self.playSource = Phonon.MediaSource(QtCore.QUrl(self.text_url))
                self.playSource.setAutoDelete(False)
                self.playSource.Type = Phonon.MediaSource.Url
                self.okMediaPlayer = Phonon.createPlayer(Phonon.MusicCategory, self.playSource)#Phonon.MediaObject()
                #self.aOutput.setMuted(False)
                #self.aOutput.setVolume(10)
                Phonon.createPath(self.okMediaPlayer, self.aOutput)
                self.okMediaPlayer.play()
                self.statusBar().showMessage(_(u'okPlayer play: %s')%self.text_url)
                
        else:
            self.okMediaPlayer.stop()
            self.statusBar().showMessage(_(u'okPlayer stop'))

    def aboutHelp(self):
        QtGui.QMessageBox.about(self, _(u'About SelectX'), \
        _(u"SelectX. Text editor licensed by GPL3. Ver. %s") % __version__)
        self.statusBar().showMessage(VERSION_INFO % \
        __version__)
        if self.ok<10:
            self.ok += 1
        if self.ok>9:
            self.okPlay.setEnabled(True)
            self.okPlay.setVisible(True)
            self.statusBar().showMessage(_(u'Ok'))

    def keyHelp(self):
        ok = QtGui.QMessageBox.information(self, _(u'Keys SelectX'), KEYS_HELP, \
        QtGui.QMessageBox.Ok)

class TextEditBaseX(QtGui.QTextEdit):
    def __init__(self, parent = None):
        super(TextEditBaseX, self).__init__()

        self.filePath = None
        self.setStyleSheet("QTextEdit {background-color: #EEFFEE;}")
        self.parentControl = parent
        self.qFont = QtGui.QFont()
        self.qFont.setFamily('Courier New')
        self.qFont.setFixedPitch(True)
        self.qFont.setPointSize(14)

        doc = QtGui.QTextDocument()
        self.highlighter = None
        self.highlighterType = None
        option = QtGui.QTextOption()
        option.setFlags(QtGui.QTextOption.ShowTabsAndSpaces)
        #option.setFlags(QtGui.QTextOption.ShowLineAndParagraphSeparators)
        doc.setDefaultTextOption(option)

        #self.setStyleSheet("QTextEdit {font-family: Courier New;}")
        doc.setDefaultStyleSheet ("QTextDocument {font-family: Courier New;}")
        self.setFont(self.qFont)
        #self.setCurrentFont('Courier New')
        
        doc.setDefaultFont(self.qFont)
        self.setDocument(doc)
        self.setAcceptRichText (False)

        self.cursorPositionChanged.connect(self.cursorPosition)
        self.installEventFilter(self)

        self.setWordWrapMode (QtGui.QTextOption.WrapMode(0))
        self.setTextBackgroundColor(QtGui.QColor(245, 250, 250))
        self.pythonicEnterOn = True
        self.enterPressed = False
        self.insertSpace = ''
        #self.textEdit.setWordWrapMode (QtGui.QTextOption.WrapMode(QtGui.QTextOption.WrapMode.NoWrap))
        #return self.textEdit
        self.zoomRate = 0
        self.encodingSet = 'utf8'

    def pythonEnter(self):
        if self.pythonicEnterOn:
            currentDoc = self.document()
            cursor = self.textCursor()
            line = cursor.blockNumber()
            lineblock = currentDoc.findBlockByLineNumber(line)
            linetext = str(lineblock.text())
            if len(linetext)>0:
                if len(linetext.rstrip()) > 0:
                    if linetext[0]=='\t':
                        if linetext.rstrip()[-1] == ':':
                            self.insertSpace = (len(linetext)-len(linetext.lstrip())+1)*'\t'
                        else:
                            self.insertSpace = (len(linetext)-len(linetext.lstrip()))*'\t'
                        self.enterPressed=True
                    elif linetext[0]==' ':
                        if linetext.rstrip()[-1] == ':':
                            self.insertSpace = (len(linetext)-len(linetext.lstrip())+4)*' '
                        else:
                            self.insertSpace = (len(linetext)-len(linetext.lstrip()))*' '
                        self.enterPressed=True
                else:
                    self.insertSpace = linetext
                    self.enterPressed=True

    def cursorPosition(self):
        currentDoc = self.document()
        cursor = self.textCursor()
        line = cursor.blockNumber() + 1
        col = cursor.columnNumber()
        #currentText = currentWidget.toPlainText()
        #symb = len(currentText)
        symb = currentDoc.characterCount()-1
        rows = currentDoc.lineCount()
        if  cursor.hasSelection():
            block = cursor.selectionEnd() - cursor.selectionStart()
            self.parentControl.parent.statusBar().showMessage(_(u"Symbols: {} | Rows: {} | Line: {} | Column: {} | Selected: {}").format(symb, rows, line, col, block))
        else:
            self.parentControl.parent.statusBar().showMessage(_(u"Symbols: {} | Rows: {} | Line: {} | Column: {}").format(symb, rows, line, col))
            pass
        if self.enterPressed:
            self.enterPressed=False
            self.insertPlainText (self.insertSpace)

    def eventFilter(self, receiver, event):
        if event.type() == QtCore.QEvent.KeyPress:
            #print 'receiver, event, event.key()'+str(QtCore.Qt.Key_Enter)+str(receiver)+str(event)+str(event.key())
            if event.key()==QtCore.Qt.Key_Enter or event.key()==16777220:
                self.pythonEnter()
            #else:
                #print str(event.key())
            #print receiver
            #return False # means stop event propagation
        #if event.type() == QtCore.QEvent.Wheel and event.modifiers()==QtCore.Qt.ControlModifier:
            #if event.delta()>0:
                #self.viewZoomIn()
                #event.ignore()
                return False
            #else:
                #self.viewZoomOut()
                #event.ignore()
                #return True
        else:
            return False
            #return QtGui.QTextEdit.eventFilter(self, receiver, event)
        return QtGui.QFrame.eventFilter(self, receiver, event)


HILIGHTER_SETUP = {'cpp c h' : {'keywordPatternsRules' : ["\\bchar\\b", "\\bclass\\b", "\\bconst\\b",
                "\\bdouble\\b", "\\benum\\b", "\\bexplicit\\b", "\\bfriend\\b",
                "\\binline\\b", "\\bint\\b", "\\blong\\b", "\\bnamespace\\b",
                "\\boperator\\b", "\\bprivate\\b", "\\bprotected\\b",
                "\\bpublic\\b", "\\bshort\\b", "\\bsignals\\b", "\\bsigned\\b",
                "\\bslots\\b", "\\bstatic\\b", "\\bstruct\\b",
                "\\btemplate\\b", "\\btypedef\\b", "\\btypename\\b",
                "\\bunion\\b", "\\bunsigned\\b", "\\bvirtual\\b", "\\bvoid\\b",
                "\\bvolatile\\b"],
                'classFormatRules' : "\\bQ[A-Za-z]+\\b",
                'quotationFormatRules':"\".*\"",
                'functionFormatRules':"\\b[A-Za-z0-9_]+(?=\\()",
                'multiLineCommentFormat' : ["/\\*", "\\*/"]},
                'py py3':{'keywordPatternsRules' : ["\\bchar\\b", "\\bclass\\b", "\\bconst\\b",
                "\\bdouble\\b", "\\benum\\b", "\\bexplicit\\b", "\\bfriend\\b",
                "\\binline\\b", "\\bint\\b", "\\blong\\b", "\\bnamespace\\b",
                "\\boperator\\b", "\\bprivate\\b", "\\bprotected\\b",
                "\\bpublic\\b", "\\bshort\\b", "\\bsignals\\b", "\\bsigned\\b",
                "\\bslots\\b", "\\bstatic\\b", "\\bstruct\\b",
                "\\btemplate\\b", "\\btypedef\\b", "\\btypename\\b",
                "\\bunion\\b", "\\bunsigned\\b", "\\bvirtual\\b", "\\bvoid\\b",
                "\\bvolatile\\b"],
                'classFormatRules' : "\\bQ[A-Za-z]+\\b",
                'quotationFormatRules':"\".*\"",
                'functionFormatRules':"\\b[A-Za-z0-9_]+(?=\\()",
                'multiLineCommentFormat' : ["/\\*", "\\*/"]}
                }

class Highlighter(QtGui.QSyntaxHighlighter):
    def __init__(self, parent=None, fileExt=''):
        if fileExt:
            super(Highlighter, self).__init__(parent)

            keywordFormat = QtGui.QTextCharFormat()
            keywordFormat.setForeground(QtCore.Qt.darkBlue)
            keywordFormat.setFontWeight(QtGui.QFont.Bold)

            keywordPatterns = ["\\bchar\\b", "\\bclass\\b", "\\bconst\\b",
                    "\\bdouble\\b", "\\benum\\b", "\\bexplicit\\b", "\\bfriend\\b",
                    "\\binline\\b", "\\bint\\b", "\\blong\\b", "\\bnamespace\\b",
                    "\\boperator\\b", "\\bprivate\\b", "\\bprotected\\b",
                    "\\bpublic\\b", "\\bshort\\b", "\\bsignals\\b", "\\bsigned\\b",
                    "\\bslots\\b", "\\bstatic\\b", "\\bstruct\\b",
                    "\\btemplate\\b", "\\btypedef\\b", "\\btypename\\b",
                    "\\bunion\\b", "\\bunsigned\\b", "\\bvirtual\\b", "\\bvoid\\b",
                    "\\bvolatile\\b"]

            self.highlightingRules = [(QtCore.QRegExp(pattern), keywordFormat)
                    for pattern in keywordPatterns]

            classFormat = QtGui.QTextCharFormat()
            classFormat.setFontWeight(QtGui.QFont.Bold)
            classFormat.setForeground(QtCore.Qt.darkMagenta)
            self.highlightingRules.append((QtCore.QRegExp("\\bQ[A-Za-z]+\\b"),
                    classFormat))

            singleLineCommentFormat = QtGui.QTextCharFormat()
            singleLineCommentFormat.setForeground(QtCore.Qt.red)
            self.highlightingRules.append((QtCore.QRegExp("//[^\n]*"),
                    singleLineCommentFormat))

            self.multiLineCommentFormat = QtGui.QTextCharFormat()
            self.multiLineCommentFormat.setForeground(QtCore.Qt.red)

            quotationFormat = QtGui.QTextCharFormat()
            quotationFormat.setForeground(QtCore.Qt.darkGreen)
            self.highlightingRules.append((QtCore.QRegExp("\".*\""),
                    quotationFormat))

            functionFormat = QtGui.QTextCharFormat()
            functionFormat.setFontItalic(True)
            functionFormat.setForeground(QtCore.Qt.blue)
            self.highlightingRules.append((QtCore.QRegExp("\\b[A-Za-z0-9_]+(?=\\()"),
                    functionFormat))

            self.commentStartExpression = QtCore.QRegExp("/\\*")
            self.commentEndExpression = QtCore.QRegExp("\\*/")

    def highlightBlock(self, text):
        for pattern, format in self.highlightingRules:
            expression = QtCore.QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)

        startIndex = 0
        if self.previousBlockState() != 1:
            startIndex = self.commentStartExpression.indexIn(text)

        while startIndex >= 0:
            endIndex = self.commentEndExpression.indexIn(text, startIndex)

            if endIndex == -1:
                self.setCurrentBlockState(1)
                commentLength = len(text) - startIndex
            else:
                commentLength = endIndex - startIndex + self.commentEndExpression.matchedLength()

            self.setFormat(startIndex, commentLength,
                    self.multiLineCommentFormat)
            startIndex = self.commentStartExpression.indexIn(text,
                    startIndex + commentLength);



class TextEditX(QtGui.QFrame):
#based on https://john.nachtimwald.com/2009/08/15/qtextedit-with-line-numbers/
    class NumberBar(QtGui.QWidget):
        def __init__(self, *args):
            QtGui.QWidget.__init__(self, *args)
            self.edit = None
            self.highest_line = 0

        def setTextEdit(self, edit):
            self.edit = edit

        def update(self, *args):
            '''
            Updates the number bar to display the current set of numbers.
            Also, adjusts the width of the number bar if necessary.
            '''
            width = self.fontMetrics().width(str(self.highest_line)) + 4
            if self.width() != width:
                self.setFixedWidth(width)
            QtGui.QWidget.update(self, *args)

        def paintEvent(self, event):
            if self.paintLineNumber:
                contents_y = self.edit.verticalScrollBar().value()
                page_bottom = contents_y + self.edit.viewport().height()
                font_metrics = self.fontMetrics()
                current_block = self.edit.document().findBlock(self.edit.textCursor().position())
    
                painter = QtGui.QPainter(self)
    
                line_count = 0
                block = self.edit.document().begin()
                while block.isValid():
                    line_count += 1
    
                    position = self.edit.document().documentLayout().blockBoundingRect(block).topLeft()
                    
                    if position.y() > page_bottom:
                        break
    
                    bold = False
                    if block == current_block:
                        bold = True
                        font = painter.font()
                        font.setBold(True)
                        painter.setFont(font)
    
                    painter.drawText(self.width() - font_metrics.width(str(line_count)) - 3, round(position.y()) - contents_y + font_metrics.ascent(), str(line_count))
    
                    if bold:
                        font = painter.font()
                        font.setBold(False)
                        painter.setFont(font)
    
                    block = block.next()
    
                self.highest_line = line_count
                painter.end()
    
                QtGui.QWidget.paintEvent(self, event)


    def __init__(self, parent, *args):
        QtGui.QFrame.__init__(self, *args)
        self.parent = parent

        self.setFrameStyle(QtGui.QFrame.StyledPanel | QtGui.QFrame.Sunken)

        self.edit = TextEditBaseX(parent=self)
        self.edit.setFrameStyle(QtGui.QFrame.NoFrame)
        self.edit.setAcceptRichText(False)

        self.number_bar = self.NumberBar()
        self.number_bar.setTextEdit(self.edit)
        self.number_bar.paintLineNumber = True

        hbox = QtGui.QHBoxLayout(self)
        hbox.setSpacing(0)
        hbox.addWidget(self.number_bar)
        hbox.addWidget(self.edit)

        self.edit.installEventFilter(self)
        self.edit.viewport().installEventFilter(self)

    def eventFilter(self, receiver, event):
        # Update the line numbers for all events on the text edit and the viewport.
        # This is easier than connecting all necessary singals.
        if (receiver in (self.edit, self.edit.viewport())) and \
        (event.type() in (QtCore.QEvent.Paint,)):
        #(event.type() in (QtCore.QEvent.Wheel, QtCore.QEvent.KeyPress, \
        #QtCore.QEvent.MouseButtonPress, QtCore.QEvent.Paint)):
            self.number_bar.update()
            return False
        return QtGui.QFrame.eventFilter(self, receiver, event)

    def getTextEdit(self):
        return self.edit


def format(color, style=''):
    """Return a QtGui.QTextCharFormat with the given attributes.
    """
    _color = QtGui.QColor()
    _color.setNamedColor(color)

    _format = QtGui.QTextCharFormat()
    _format.setForeground(_color)
    if 'bold' in style:
        _format.setFontWeight(QtGui.QFont.Bold)
    if 'italic' in style:
        _format.setFontItalic(True)

    return _format


# Syntax styles that can be shared by all languages
STYLES = {
    'keyword': format('blue'),
    'operator': format('red'),
    'brace': format('darkGray'),
    'defclass': format('black', 'bold'),
    'string': format('magenta'),
    'string2': format('darkMagenta'),
    'comment': format('darkGreen', 'italic'),
    'self': format('black', 'italic'),
    'numbers': format('brown'),
}


class PythonHighlighter (QtGui.QSyntaxHighlighter):
    """Syntax highlighter for the Python language.
    """
    # Python keywords
    keywords = [
        'and', 'assert', 'break', 'class', 'continue', 'def',
        'del', 'elif', 'else', 'except', 'exec', 'finally',
        'for', 'from', 'global', 'if', 'import', 'in',
        'is', 'lambda', 'not', 'or', 'pass', 'print',
        'raise', 'return', 'try', 'while', 'yield',
        'None', 'True', 'False',
    ]

    # Python operators
    operators = [
        '=',
        # Comparison
        '==', '!=', '<', '<=', '>', '>=',
        # Arithmetic
        '\+', '-', '\*', '/', '//', '\%', '\*\*',
        # In-place
        '\+=', '-=', '\*=', '/=', '\%=',
        # Bitwise
        '\^', '\|', '\&', '\~', '>>', '<<',
    ]

    # Python braces
    braces = [
        '\{', '\}', '\(', '\)', '\[', '\]',
    ]
    def __init__(self, document):
        QtGui.QSyntaxHighlighter.__init__(self, document)

        # Multi-line strings (expression, flag, style)
        # FIXME: The triple-quotes in these two lines will mess up the
        # syntax highlighting from this point onward
        #self.tri_single = (QtCore.QRegExp("'''[^'''\\]*(\\.[^'''\\]*)*'''"), 1, STYLES['string2'])
        #self.tri_double = (QtCore.QRegExp('"""[^"""\\]*(\\.[^"""\\]*)*"""'), 2, STYLES['string2'])
        self.tri_single = (QtCore.QRegExp("'''"), 1, STYLES['string2'])
        self.tri_double = (QtCore.QRegExp('"""'), 2, STYLES['string2'])

        rules = []


        # Keyword, operator, and brace rules
        rules += [(r'\b%s\b' % w, 0, STYLES['keyword'])
            for w in PythonHighlighter.keywords]
        rules += [(r'%s' % o, 0, STYLES['operator'])
            for o in PythonHighlighter.operators]
        rules += [(r'%s' % b, 0, STYLES['brace'])
            for b in PythonHighlighter.braces]

        # All other rules
        rules += [
            # 'self'
            (r'\bself\b', 0, STYLES['self']),

            # Double-quoted string, possibly containing escape sequences
            (r'"[^"\\]*(\\.[^"\\]*)*"', 0, STYLES['string']),
            # Single-quoted string, possibly containing escape sequences
            (r"'[^'\\]*(\\.[^'\\]*)*'", 0, STYLES['string']),

            # 'def' followed by an identifier
            (r'\bdef\b\s*(\w+)', 1, STYLES['defclass']),
            # 'class' followed by an identifier
            (r'\bclass\b\s*(\w+)', 1, STYLES['defclass']),

            # From '#' until a newline
            (r'#[^\n]*', 0, STYLES['comment']),

            # Numeric literals
            (r'\b[+-]?[0-9]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b', 0, STYLES['numbers']),
        ]

        # Build a QtCore.QRegExp for each pattern
        self.rules = [(QtCore.QRegExp(pat), index, fmt)
            for (pat, index, fmt) in rules]


    def highlightBlock(self, text):
        """Apply syntax highlighting to the given block of text.
        """
        # Do other syntax formatting
        for expression, nth, format in self.rules:
            index = expression.indexIn(text, 0)

            while index >= 0:
                # We actually want the index of the nth match
                index = expression.pos(nth)
                #length = expression.cap(nth).length() # pyside fix
                length = len(expression.cap(nth))
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)

        # Do multi-line strings
        #in_multiline1 = self.match_multiline(text, *self.tri_single)
        #if not in_multiline1:
            #in_multiline1 = self.match_multiline(text, *self.tri_double)
        #in_multiline2 = self.match_multiline(text, *self.tri_double)
        #if not in_multiline2:
            #in_multiline2 = self.match_multiline(text, *self.tri_single)


    def match_multiline(self, text, delimiter, in_state, style):
        """Do highlighting of multi-line strings. ``delimiter`` should be a
        ``QtCore.QRegExp`` for triple-single-quotes or triple-double-quotes, and
        ``in_state`` should be a unique integer to represent the corresponding
        state changes when inside those strings. Returns True if we're still
        inside a multi-line string when this function is finished.
        """
        # If inside triple-single quotes, start at 0
        if self.previousBlockState() == in_state:
            start = 0
            add = 0
        # Otherwise, look for the delimiter on this line
        else:
            start = delimiter.indexIn(text)
            # Move past this match
            add = delimiter.matchedLength()

        # As long as there's a delimiter match on this line...
        while start >= 0:
            # Look for the ending delimiter
            end = delimiter.indexIn(text, start + add)
            # Ending delimiter on this line?
            if end >= add:
                length = end - start + add + delimiter.matchedLength()
                self.setCurrentBlockState(0)
            # No; multi-line string
            else:
                self.setCurrentBlockState(in_state)
                length = len(text) - start + add
                #length = text.length() - start + add
            # Apply formatting
            self.setFormat(start, length, style)
            # Look for the next match
            start = delimiter.indexIn(text, start + length)

        # Return True if still inside a multi-line string, False otherwise
        if self.currentBlockState() == in_state:
            return True
        else:
            return False


class VolumeDialog(QtGui.QDialog):
    '''Extended find/replase dialouge based on http://www.binpress.com/tutorial/building-a-text-editor-with-pyqt-part-3/147'''
    def __init__(self, parent, aOutput):

        QtGui.QDialog.__init__(self, parent, 0x00000000- 0x08000000)
        self.setModal(False)
        self.parent = parent
        self.aOutput = aOutput
        self.initUI()
        self.show()

    def initUI(self):
        #from PySide.phonon import Phonon
        #if LIB_USE == "PySide":
            #from PySide.phonon import Phonon
        #else:
            #from PyQt4.phonon import Phonon
            ##pass
        #print str(self.aOutput.outputDevice())
        self.newOkVolume = Phonon.VolumeSlider()
        self.newOkVolume.setAudioOutput(self.aOutput)
        self.newOkVolume.setTracking (True)
        #self.newOkVolume.valueChanged.connect(self.changeVolume)
        #self.newOkVolume.setMaximumVolume(2.0)
        #print str(self.newOkVolume)

        self.OkButton = QtGui.QPushButton(_(u"Ok"),self)
        self.OkButton.clicked.connect(self.Ok)

        layout = QtGui.QGridLayout()

        layout.addWidget(self.newOkVolume)
        layout.addWidget(self.OkButton)
        self.setWindowTitle(_(u"Set Ok"))
        self.setLayout(layout)

    def changeVolume(self, value):
        self.aOutput.setVolume(value)

        
    def Ok(self):
        #self.aOutput.setVolumeDecibel(1000)
        self.close()
        
        
class FindDialog(QtGui.QDialog):
    '''Extended find/replase dialouge based on http://www.binpress.com/tutorial/building-a-text-editor-with-pyqt-part-3/147'''
    def __init__(self, parent = None):

        QtGui.QDialog.__init__(self, parent)
        self.setModal(True)
        self.parent = parent
        self.lastMatch = None
        self.initUI()

    def initUI(self):
        findButton = QtGui.QPushButton(_(u"Find"),self)
        findButton.clicked.connect(self.find)
        replaceButton = QtGui.QPushButton(_(u"Replace"),self)
        replaceButton.clicked.connect(self.replace)
        allButton = QtGui.QPushButton(_(u"Replace all"),self)
        allButton.clicked.connect(self.replaceAll)
        self.normalRadio = QtGui.QRadioButton(_(u"Normal"),self)
        self.normalRadio.toggled.connect(self.normalMode)
        self.regexRadio = QtGui.QRadioButton(_(u"RegEx"),self)
        self.regexRadio.toggled.connect(self.regexMode)
        self.findField = QtGui.QTextEdit(self)
        self.findField.setAcceptRichText(False)

        self.replaceField = QtGui.QTextEdit(self)
        self.replaceField.setAcceptRichText(False)

        optionsLabel = QtGui.QLabel(_(u"Options: "),self)
        self.caseSens = QtGui.QCheckBox(_(u"Case sensitive"),self)
        self.wholeWords = QtGui.QCheckBox(_(u"Whole words"),self)
        layout = QtGui.QGridLayout()

        layout.addWidget(self.findField,1,0,1,4)
        layout.addWidget(self.normalRadio,2,2)
        layout.addWidget(self.regexRadio,2,3)
        layout.addWidget(findButton,2,0,1,2)

        layout.addWidget(self.replaceField,3,0,1,4)
        layout.addWidget(replaceButton,4,0,1,2)
        layout.addWidget(allButton,4,2,1,2)
        spacer = QtGui.QWidget(self)

        spacer.setFixedSize(0,1)

        layout.addWidget(spacer,5,0)

        layout.addWidget(optionsLabel,6,0)
        layout.addWidget(self.caseSens,6,1)
        layout.addWidget(self.wholeWords,6,2)
        self.setWindowTitle(_(u"Find and Replace"))
        self.setLayout(layout)
        self.normalRadio.setChecked(True)

    def find(self):
        text = self.parent.mainTab.currentWidget().edit.toPlainText()
        query = self.findField.toPlainText()
        if self.wholeWords.isChecked():
            query = r'\W' + query + r'\W'
        flags = 0 if self.caseSens.isChecked() else re.I
        pattern = re.compile(query,flags)
        start = self.lastMatch.start() + 1 if self.lastMatch else 0
        self.lastMatch = pattern.search(text,start)
        if self.lastMatch:
            start = self.lastMatch.start()
            end = self.lastMatch.end()
            if self.wholeWords.isChecked():
                start += 1
                end -= 1

            self.moveCursor(start,end)

        else:
            self.parent.mainTab.currentWidget().edit.moveCursor(QtGui.QTextCursor.End)

    def replace(self):
        cursor = self.parent.mainTab.currentWidget().edit.textCursor()
        if self.lastMatch and cursor.hasSelection():
            cursor.insertText(self.replaceField.toPlainText())
            self.parent.mainTab.currentWidget().edit.setTextCursor(cursor)

    def replaceAll(self):
        self.lastMatch = None
        self.find()
        while self.lastMatch:
            self.replace()
            self.find()

    def regexMode(self):
        self.caseSens.setChecked(False)
        self.wholeWords.setChecked(False)
        self.caseSens.setEnabled(False)
        self.wholeWords.setEnabled(False)

    def normalMode(self):
        self.caseSens.setEnabled(True)
        self.wholeWords.setEnabled(True)

    def moveCursor(self,start,end):
        cursor = self.parent.mainTab.currentWidget().edit.textCursor()
        cursor.setPosition(start)
        cursor.movePosition(QtGui.QTextCursor.Right,QtGui.QTextCursor.KeepAnchor,end - start)
        self.parent.mainTab.currentWidget().edit.setTextCursor(cursor)


def main():
    if len(sys.argv) < 2:
        runWindow()
    elif sys.argv[1]=='-h' or sys.argv[1]=='--help':
        usage()
        sys.exit()
    elif sys.argv[1]=='--ForceEmbededIcons':
        runWindow(True)
    elif sys.argv[1]=='--ok':
        runWindow(True, 10)
    elif sys.argv[1]=='--version':
        print VERSION_INFO % __version__
        sys.exit()
    runWindow()

def getFileName(pathName, separatorSymbol=None):
    if separatorSymbol:
        try:
            return pathName.split(separatorSymbol)[-1]
        except AttributeError:
            return None
    #elif ( '\\' in pathName ) :
        #return pathName.split('\\')[-1]
    else:
        return pathName.split(os.path.sep)[-1]

def getQtCodecsList():
    newlist=[]
    for kkk in QtCore.QTextCodec.availableCodecs():
        ccc = QtCore.QTextCodec.codecForName(kkk)
        nnn=ccc.name()
        if not nnn in newlist and not nnn[0] in ('0','1','2','3','4','5','6','7','8','9'):
            newlist.append(nnn)
    return newlist

def getCodecsList(newlist = []):
    encodings_aliases=encodings._aliases
    for kkk in encodings_aliases.keys():
        if not kkk in newlist and not kkk[0] in ('0','1','2','3','4','5','6','7','8','9'):
            newlist.append(kkk)
    #for kkk in encodings_aliases.keys():
        #if not encodings_aliases[kkk] in newlist:
            #newlist.append(encodings_aliases[kkk])
    return sorted(newlist)

def getCodecsAliasesList(newlist = []):
    encodings_aliases=encodings._aliases
    #for kkk in encodings_aliases.keys():
        ##print encodings_aliases[kkk]
        #if not kkk in newlist and not kkk[0] in ('0','1','2','3','4','5','6','7','8','9'):
            #newlist.append(kkk)
    for kkk in encodings_aliases.keys():
        if not encodings_aliases[kkk] in newlist:
            newlist.append(encodings_aliases[kkk])
    return sorted(newlist)

def usage():
    print sys.argv[0] + '\n' + VERSION_INFO % __version__ + CONSOLE_USAGE


def runWindow(ForceIcons = None, ok=0):
    app = QtGui.QApplication(sys.argv)
    if ForceIcons:
        selxnotepad = SelectX(ForceIcons, ok)
    else:
        selxnotepad = SelectX(ok = ok)
    sys.exit(app.exec_())


if __name__ == "__main__":
    _ = localGettextX()
    VERSION_INFO = _(u"SelectX. Text editor licensed by GPL3. Ver. %s")
    main()

