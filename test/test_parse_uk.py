import unittest
from datetime import datetime, timedelta

from lingua_franca import set_default_lang, \
    load_language, unload_language
from lingua_franca.parse import extract_datetime
from lingua_franca.parse import extract_duration
from lingua_franca.parse import extract_number, extract_numbers
from lingua_franca.parse import fuzzy_match
from lingua_franca.parse import match_one
from lingua_franca.parse import normalize
from lingua_franca.time import default_timezone


def setUpModule():
    load_language("uk-ua")
    set_default_lang("uk")


def tearDownModule():
    unload_language("uk")


class TestFuzzyMatch(unittest.TestCase):
    def test_matches(self):
        self.assertTrue(fuzzy_match("ти і ми", "ти і ми") >= 1.0)
        self.assertTrue(fuzzy_match("ти і ми", "ти") < 0.5)
        self.assertTrue(fuzzy_match("Ти", "ти") >= 0.5)
        self.assertTrue(fuzzy_match("ти і ми", "ти") ==
                        fuzzy_match("ти", "ти і ми"))
        self.assertTrue(fuzzy_match("ти і ми", "він або вони") < 0.36)

    def test_match_one(self):
        # test list of choices
        choices = ['френк', 'кейт', 'гаррі', 'генрі']
        self.assertEqual(match_one('френк', choices)[0], 'френк')
        self.assertEqual(match_one('френ', choices)[0], 'френк')
        self.assertEqual(match_one('енрі', choices)[0], 'генрі')
        self.assertEqual(match_one('кетт', choices)[0], 'кейт')
        # test dictionary of choices
        choices = {'френк': 1, 'кейт': 2, 'гаррі': 3, 'генрі': 4}
        self.assertEqual(match_one('френк', choices)[0], 1)
        self.assertEqual(match_one('енрі', choices)[0], 4)


class TestNormalize(unittest.TestCase):

    def test_extract_number(self):
        self.assertEqual(extract_number("це перший тест",
                                        ordinals=True), 1)
        self.assertEqual(extract_number("це 2 тест"), 2)
        self.assertEqual(extract_number("це другий тест",
                                        ordinals=True), 2)
        self.assertEqual(extract_number("цей один третій тест",
                                        ordinals=True), 3.0)
        self.assertEqual(extract_number("це четвертий", ordinals=True), 4.0)
        self.assertEqual(extract_number(
            "це тридцять шостий", ordinals=True), 36.0)
        self.assertEqual(extract_number("це тест на число 4"), 4)
        self.assertEqual(extract_number("одна третя чашки"), 1.0 / 3.0)
        self.assertEqual(extract_number("три чашки"), 3)
        self.assertEqual(extract_number("1/3 чашки"), 1.0 / 3.0)
        self.assertEqual(extract_number("четвертина чашки"), 0.25)
        self.assertEqual(extract_number("чверть чашки"), 0.25)
        self.assertEqual(extract_number("одна четверта чашки"), 0.25)
        self.assertEqual(extract_number("1/4 чашки"), 0.25)
        self.assertEqual(extract_number("2/3 чашки"), 2.0 / 3.0)
        self.assertEqual(extract_number("3/4 чашки"), 3.0 / 4.0)
        self.assertEqual(extract_number("1 і 3/4 чашки"), 1.75)
        self.assertEqual(extract_number("1 чашка з половиною"), 1.5)
        self.assertEqual(extract_number("один чашка з половиною"), 1.5)
        self.assertEqual(extract_number("одна і половина чашки"), 1.5)
        self.assertEqual(extract_number("одна з половиною чашка"), 1.5)
        self.assertEqual(extract_number("одна і одна половина чашки"), 1.5)
        self.assertEqual(extract_number("три четвертих чашки"), 3.0 / 4.0)
        self.assertEqual(extract_number("три четверті чашки"), 3.0 / 4.0)
        self.assertEqual(extract_number("двадцять два"), 22)
        self.assertEqual(extract_number(
            "Двадцять два з великою буквой на початку"), 22)
        self.assertEqual(extract_number(
            "Двадцять Два з двома великими буквами"), 22)
        self.assertEqual(extract_number(
            "двадцять Два з другою великою буквою"), 22)
        # self.assertEqual(extract_number("Двадцять два і Три п'ятих"), 22.6)
        self.assertEqual(extract_number("двісті"), 200)
        self.assertEqual(extract_number("дев'ять тисяч"), 9000)
        self.assertEqual(extract_number("шістсот шістдесят шість"), 666)
        self.assertEqual(extract_number("два мільйони"), 2000000)
        self.assertEqual(extract_number("два мільйони п'ятсот тисяч "
                                        "тонн чавуну"), 2500000)
        self.assertEqual(extract_number("шість трильйонів"), 6000000000000.0)
        self.assertEqual(extract_number("шість трильйонів", short_scale=False),
                         6e+18)
        self.assertEqual(extract_number("один крапка п'ять"), 1.5)
        self.assertEqual(extract_number("три крапка чотирнадцять"), 3.14)
        self.assertEqual(extract_number("нуль крапка два"), 0.2)
        self.assertEqual(extract_number("мільярд років"),
                         1000000000.0)
        self.assertEqual(extract_number("більйон років",
                                        short_scale=False),
                         1000000000000.0)
        self.assertEqual(extract_number("сто тисяч"), 100000)
        self.assertEqual(extract_number("мінус 2"), -2)
        self.assertEqual(extract_number("мінус сімдесят"), -70)
        self.assertEqual(extract_number("тисяча мільйонів"), 1000000000)
        self.assertEqual(extract_number("мільярд", short_scale=False),
                         1000000000)
        # self.assertEqual(extract_number("шестая треть"),
        #                  1 / 6 / 3)
        # self.assertEqual(extract_number("шестая треть", ordinals=True),
        #                  6)
        self.assertEqual(extract_number("тридцять секунд"), 30)
        self.assertEqual(extract_number("тридцять два", ordinals=True), 32)
        self.assertEqual(extract_number("ось це мільярдний тест",
                                        ordinals=True), 1e09)
        self.assertEqual(extract_number("ось це одна мільярдна теста"), 1e-9)
        self.assertEqual(extract_number("ось це більйонний тест",
                                        ordinals=True,
                                        short_scale=False), 1e12)
        # self.assertEqual(extract_number("ось це одна більйонна теста",
        #                                 short_scale=False), 1e-12)

        # Verify non-power multiples of ten no longer discard
        # adjacent multipliers
        self.assertEqual(extract_number("двадцять тисяч"), 20000)
        self.assertEqual(extract_number("п'ятдесят мільйонів"), 50000000)

        # Verify smaller powers of ten no longer cause miscalculation of larger
        # powers of ten (see MycroftAI#86)
        self.assertEqual(extract_number("двадцять мільярдів триста мільйонів "
                                        "дев'ятсот п'ятдесят тисяч "
                                        "шістсот сімдесят п'ять крапка вісім"),
                         20300950675.8)
        self.assertEqual(extract_number("дев'ятсот дев'яносто дев'ять мільйонів "
                                        "дев'ятсот дев'яносто дев'ять тисяч "
                                        "дев'ятсот дев'яносто дев'ять крапка дев'ять"),
                         999999999.9)

        # TODO why does "trillion" result in xxxx.0?
        self.assertEqual(extract_number("вісімсот трильйонів двісті \
                                        п'ятдесят сім"), 800000000000257.0)

        # TODO handle this case
        # self.assertEqual(
        #    extract_number("6 dot six six six"),
        #    6.666)
        self.assertTrue(extract_number("Тенісист швидкий") is False)
        self.assertTrue(extract_number("крихкий") is False)

        self.assertTrue(extract_number("крихкий нуль") is not False)
        self.assertEqual(extract_number("крихкий нуль"), 0)

        self.assertTrue(extract_number("грубий 0") is not False)
        self.assertEqual(extract_number("грубий 0"), 0)

        self.assertEqual(extract_number("пара пива"), 2)
        # self.assertEqual(extract_number("пара сотен пив"), 200)
        self.assertEqual(extract_number("пара тисяч пив"), 2000)

        self.assertEqual(extract_number(
            "ось це 7 тест", ordinals=True), 7)
        self.assertEqual(extract_number(
            "ось це 7 тест", ordinals=False), 7)
        self.assertTrue(extract_number("ось це n. тест") is False)
        self.assertEqual(extract_number("ось це 1. тест"), 1)
        self.assertEqual(extract_number("ось це 2. тест"), 2)
        self.assertEqual(extract_number("ось це 3. тест"), 3)
        self.assertEqual(extract_number("ось це 31. тест"), 31)
        self.assertEqual(extract_number("ось це 32. тест"), 32)
        self.assertEqual(extract_number("ось це 33. тест"), 33)
        self.assertEqual(extract_number("ось це 34. тест"), 34)
        self.assertEqual(extract_number("загалом 100%"), 100)

    def test_extract_duration_uk(self):
        self.assertEqual(extract_duration("10 секунд"),
                         (timedelta(seconds=10.0), ""))
        self.assertEqual(extract_duration("5 хвилин"),
                         (timedelta(minutes=5), ""))
        self.assertEqual(extract_duration("2 години"),
                         (timedelta(hours=2), ""))
        self.assertEqual(extract_duration("3 дні"),
                         (timedelta(days=3), ""))
        self.assertEqual(extract_duration("25 тижнів"),
                         (timedelta(weeks=25), ""))
        self.assertEqual(extract_duration("сім годин"),
                         (timedelta(hours=7), ""))
        self.assertEqual(extract_duration("7.5 секунд"),
                         (timedelta(seconds=7.5), ""))
        self.assertEqual(extract_duration("вісім з половиною днів "
                                          "тридцять дев'ять секунд"),
                         (timedelta(days=8.5, seconds=39), ""))
        self.assertEqual(extract_duration("Встанови таймер на 30 хвилин"),
                         (timedelta(minutes=30), "встанови таймер на"))
        self.assertEqual(extract_duration("Чотири з половиною хвилини до заходу"),
                         (timedelta(minutes=4.5), "до заходу"))
        self.assertEqual(extract_duration("дев'ятнадцять хвилин через годину"),
                         (timedelta(minutes=19), "через годину"))
        # self.assertEqual(extract_duration("розбуди мене через три тижні, "
        #                                   "чотириста дев'яносто сім днів "
        #                                   "і триста 91.6 секунд"),
        #                  (timedelta(weeks=3, days=497, seconds=391.6),
        #                   "розбуди мене через , a"))
        self.assertEqual(extract_duration("фільм одна година п'ятдесят сім і пів хвилини довжиною"),
                         (timedelta(hours=1, minutes=57.5), "фільм   довжиною"))
        self.assertEqual(extract_duration("10-секунд"),
                         (timedelta(seconds=10.0), ""))
        self.assertEqual(extract_duration("5-хвилин"),
                         (timedelta(minutes=5), ""))

    def test_extract_datetime_uk(self):
        def extractWithFormat(text):
            # Tue June 27, 2017 @ 1:04pm
            date = datetime(2017, 6, 27, 13, 4, tzinfo=default_timezone())
            [extractedDate, leftover] = extract_datetime(text, date)
            extractedDate = extractedDate.strftime("%Y-%m-%d %H:%M:%S")
            return [extractedDate, leftover]

        def testExtract(text, expected_date, expected_leftover):
            res = extractWithFormat(normalize(text))
            self.assertEqual(res[0], expected_date, "for=" + text)
            self.assertEqual(res[1], expected_leftover, "for=" + text)

        testExtract("тепер пора", "2017-06-27 13:04:00", "пора")
        self.u = "секунду"
        testExtract("через %s" % self.u, "2017-06-27 13:04:01", "")
        testExtract("через хвилину", "2017-06-27 13:05:00", "")
        testExtract("через дві хвилини", "2017-06-27 13:06:00", "")
        # testExtract("через пару хвилин", "2017-06-27 13:06:00", "")
        testExtract("через дві години", "2017-06-27 15:04:00", "")
        # testExtract("через пару годин", "2017-06-27 15:04:00", "")
        testExtract("через два тижні", "2017-07-11 00:00:00", "")
        # testExtract("через пару тижнів", "2017-07-11 00:00:00", "")
        testExtract("через два місяці", "2017-08-27 00:00:00", "")
        testExtract("через два роки", "2019-06-27 00:00:00", "")
        # testExtract("через пару місяців", "2017-08-27 00:00:00", "")
        # testExtract("через пару років", "2019-06-27 00:00:00", "")
        testExtract("через десятиліття", "2027-06-27 00:00:00", "")
        # testExtract("через пару десятиліть", "2037-06-27 00:00:00", "")
        testExtract("наступне десятиліття", "2027-06-27 00:00:00", "")
        testExtract("через століття", "2117-06-27 00:00:00", "")
        # testExtract("через тисячоліття", "2017-06-27 00:00:00", "")
        # testExtract("через два десятиліття", "2037-06-27 00:00:00", "")
        # testExtract("через 5 десятиліть", "2067-06-27 00:00:00", "")
        # testExtract("через два віки", "2217-06-27 00:00:00", "")
        # testExtract("через пару віків", "2217-06-27 00:00:00", "")
        # testExtract("через два тисячоліття", "4017-06-27 00:00:00", "")
        # testExtract("через дві тисячі років", "4017-06-27 00:00:00", "")
        # testExtract("через пару тисячоліть", "4017-06-27 00:00:00", "")
        # testExtract("через пару тисяч років", "4017-06-27 00:00:00", "")
        testExtract("через рік", "2018-06-27 00:00:00", "")
        testExtract("хочу морозиво через годину", "2017-06-27 14:04:00", "хочу морозиво")
        testExtract("через 1 секунду", "2017-06-27 13:04:01", "")
        testExtract("через 2 секунди", "2017-06-27 13:04:02", "")
        testExtract("Встанови таймер на 1 хвилину", "2017-06-27 13:05:00", "встанови таймер")
        testExtract("Встанови таймер на пів години", "2017-06-27 13:34:00", "встанови таймер")
        # testExtract("Встанови таймер на 5 днів з сьогодні", "2017-07-02 00:00:00", "Встанови таймер")
        testExtract("післязавтра", "2017-06-29 00:00:00", "")
        testExtract("після завтра", "2017-06-29 00:00:00", "")
        testExtract("Яка погода післязавтра?", "2017-06-29 00:00:00", "яка погода")
        testExtract("Нагадай мені о 10:45 pm", "2017-06-27 22:45:00", "нагадай мені")
        testExtract("Нагадай мені о 10:45 вечора", "2017-06-27 22:45:00", "нагадай мені")
        testExtract("Яка погода в п'ятницю зранку", "2017-06-30 08:00:00", "яка погода")
        testExtract("Яка завтра погода", "2017-06-28 00:00:00", "яка погода")
        testExtract("Яка погода сьогодні вдень", "2017-06-27 15:00:00", "яка погода")
        testExtract("Яка погода сьогодні ввечері", "2017-06-27 19:00:00", "яка погода")
        testExtract("Яка була погода сьогодні зранку", "2017-06-27 08:00:00", "яка була погода")
        testExtract("Нагадай мені подзвонити мамі через 8 тижнів і 2 дні", "2017-08-24 00:00:00",
                    "нагадай мені подзвонити мамі")
        testExtract("Нагадай мені подзвонити мамі в серпні 3", "2017-08-03 00:00:00", "нагадай мені подзвонити мамі")
        testExtract("Нагадай мені завтра подзвонити мамі о 7am", "2017-06-28 07:00:00", "нагадай мені подзвонити мамі")
        testExtract("Нагадай мені завтра подзвонити мамі о 7ранку", "2017-06-28 07:00:00",
                    "нагадай мені подзвонити мамі")
        testExtract("Нагадай мені завтра подзвонити мамі в 10pm", "2017-06-28 22:00:00", "нагадай мені подзвонити мамі")
        testExtract("Нагадай мені завтра подзвонити мамі о 7 вечора", "2017-06-28 19:00:00",
                    "нагадай мені подзвонити мамі")
        testExtract("Нагадай мені завтра подзвонити мамі в 10 вечора", "2017-06-28 22:00:00",
                    "нагадай мені подзвонити мамі")
        testExtract("Нагадай мені завтра подзвонити мамі о 7 годині вечора", "2017-06-28 19:00:00",
                    "нагадай мені подзвонити мамі")
        testExtract("Нагадай мені завтра подзвонити мамі о 10 годині вечора", "2017-06-28 22:00:00",
                    "нагадай мені подзвонити мамі")
        testExtract("Нагадай мені подзвонити мамі о 7am", "2017-06-28 07:00:00", "нагадай мені подзвонити мамі")
        testExtract("Нагадай мені подзвонити мамі о 7ранку", "2017-06-28 07:00:00", "нагадай мені подзвонити мамі")
        testExtract("Нагадай мені подзвонити мамі через годину", "2017-06-27 14:04:00", "нагадай мені подзвонити мамі")
        testExtract("Нагадай мені подзвонити мамі о 1730", "2017-06-27 17:30:00", "нагадай мені подзвонити мамі")
        testExtract("Нагадай мені подзвонити мамі о 0630", "2017-06-28 06:30:00", "нагадай мені подзвонити мамі")
        testExtract("Нагадай мені подзвонити мамі о 06 30 годині", "2017-06-28 06:30:00",
                    "нагадай мені подзвонити мамі")
        testExtract("Нагадай мені подзвонити мамі о 06 30", "2017-06-28 06:30:00", "нагадай мені подзвонити мамі")
        testExtract("Нагадай мені подзвонити мамі о 06 30 годин", "2017-06-28 06:30:00", "нагадай мені подзвонити мамі")
        testExtract("Нагадай мені подзвонити мамі о 7 годин", "2017-06-27 19:00:00", "нагадай мені подзвонити мамі")
        testExtract("Нагадай мені подзвонити мамі ввечері о 7 годині", "2017-06-27 19:00:00",
                    "нагадай мені подзвонити мамі")
        testExtract("Нагадай мені подзвонити мамі  о 7 годині ввечері", "2017-06-27 19:00:00",
                    "нагадай мені подзвонити мамі")
        testExtract("Нагадай мені подзвонити мамі о 7 годин ранку", "2017-06-28 07:00:00",
                    "нагадай мені подзвонити мамі")
        testExtract("Нагадай мені подзвонити мамі в четвер ввечері о 7 годині", "2017-06-29 19:00:00",
                    "нагадай мені подзвонити мамі")
        testExtract("Нагадай мені подзвонити мамі в четвер зранку о 7 годині", "2017-06-29 07:00:00",
                    "нагадай мені подзвонити мамі")
        testExtract("Нагадай мені подзвонити мамі о 7 годині в четвер зранку", "2017-06-29 07:00:00",
                    "нагадай мені подзвонити мамі")
        testExtract("Нагадай мені подзвонити мамі о 7:00 в четвер зранку", "2017-06-29 07:00:00",
                    "нагадай мені подзвонити мамі")
        testExtract("Нагадай мені подзвонити мамі о 7:00 в четвер ввечері", "2017-06-29 19:00:00",
                    "нагадай мені подзвонити мамі")
        testExtract("Нагадай мені подзвонити мамі в 8 вечора середи", "2017-06-28 20:00:00",
                    "нагадай мені подзвонити мамі")
        testExtract("Нагадай мені подзвонити мамі в 8 в середу ввечері", "2017-06-28 20:00:00",
                    "нагадай мені подзвонити мамі")
        testExtract("Нагадай мені подзвонити мамі ввечері середи о 8", "2017-06-28 20:00:00",
                    "нагадай мені подзвонити мамі")
        testExtract("Нагадай мені подзвонити мамі через дві години", "2017-06-27 15:04:00",
                    "нагадай мені подзвонити мамі")
        testExtract("Нагадай мені подзвонити мамі через 2 години", "2017-06-27 15:04:00",
                    "нагадай мені подзвонити мамі")
        testExtract("Нагадай мені подзвонити мамі через 15 хвилин", "2017-06-27 13:19:00",
                    "нагадай мені подзвонити мамі")
        testExtract("Нагадай мені подзвонити мамі через п'ятнадцять хвилин", "2017-06-27 13:19:00",
                    "нагадай мені подзвонити мамі")
        testExtract("Нагадай мені подзвонити мамі через пів години", "2017-06-27 13:34:00",
                    "нагадай мені подзвонити мамі")
        testExtract("Нагадай мені подзвонити мамі через чверть години", "2017-06-27 13:19:00",
                    "нагадай мені подзвонити мамі")
        # testExtract("Нагадай мені подзвонити мамі о 10am на 2 день після цієї суботи",
        #             "2017-07-03 10:00:00", "нагадай мені подзвонити мамі")
        testExtract("Слухайте музику Ріка Естлі через 2 дні з п'ятниці", "2017-07-02 00:00:00",
                    "слухайте музику ріка естлі")
        testExtract("Почати вторгнення о 3:45 pm в четвер", "2017-06-29 15:45:00", "почати вторгнення")
        testExtract("Почати вторгнення о 3:45 вечора в четвер", "2017-06-29 15:45:00", "почати вторгнення")
        testExtract("Почати вторгнення о 3:45 дня в четвер", "2017-06-29 15:45:00", "почати вторгнення")
        testExtract("В понеділок замов торт з пекарні", "2017-07-03 00:00:00", "замов торт з пекарні")
        testExtract("Увімкни музику з днем народження через 5 років", "2022-06-27 00:00:00",
                    "увімкни музику з днем народження")
        testExtract("Скайп Мамі о 12:45 pm в наступний четвер", "2017-07-06 12:45:00", "скайп мамі")
        testExtract("Скайп Мамі о 12:45 дня в наступний четвер", "2017-07-06 12:45:00", "скайп мамі")
        testExtract("Яка погода в наступну п'ятницю?", "2017-06-30 00:00:00", "яка погода")
        testExtract("Яка погода в наступну середу?", "2017-07-05 00:00:00", "яка погода")
        testExtract("Яка погода в наступний четвер?", "2017-07-06 00:00:00", "яка погода")
        testExtract("Яка погода в наступну п'ятницю зранку", "2017-06-30 08:00:00", "яка погода")
        testExtract("Яка погода в наступну п'ятницю ввечері", "2017-06-30 19:00:00", "яка погода")
        testExtract("Яка погода в наступну п'ятницю вдень", "2017-06-30 15:00:00", "яка погода")
        testExtract("Яка погода в наступну п'ятницю опівдні", "2017-06-30 12:00:00", "яка погода")
        testExtract("Нагадай мені подзвонити мамі третього серпня", "2017-08-03 00:00:00",
                    "нагадай мені подзвонити мамі")
        # testExtract("купити фейерверк о 4 в четвер", "2017-07-04 00:00:00", "купити фейерверк")
        testExtract("Яка погода через 2 тижні з наступної п'ятниці", "2017-07-14 00:00:00", "яка погода")
        testExtract("Яка погода в середу о 0700 годині", "2017-06-28 07:00:00", "яка погода")
        testExtract("Постав будильник в середу о 7 годині", "2017-06-28 07:00:00", "постав будильник")
        testExtract("Признач зустріч о 12:45 pm в наступний четвер", "2017-07-06 12:45:00", "признач зустріч")
        testExtract("Признач зустріч о 12:45 дня в наступний четвер", "2017-07-06 12:45:00", "признач зустріч")
        testExtract("Яка погода в цей четвер?", "2017-06-29 00:00:00", "яка погода")
        testExtract("признач зустріч через 2 тижні і 6 днів з суботи", "2017-07-21 00:00:00", "признач зустріч")
        testExtract("Почати вторгнення о 03 45 в четвер", "2017-06-29 03:45:00", "почати вторгнення")
        testExtract("Почати вторгнення в 800 годин в четвер", "2017-06-29 08:00:00", "почати вторгнення")
        testExtract("Почати вечірку о 8 годині вечора в четвер", "2017-06-29 20:00:00", "почати вечірку")
        testExtract("Почати вторгнення о 8 вечора в четвер", "2017-06-29 20:00:00", "почати вторгнення")
        testExtract("Почати вторгнення в четвер в полудень", "2017-06-29 12:00:00", "почати вторгнення")
        testExtract("Почати вторгнення в четвер в північ", "2017-06-29 00:00:00", "почати вторгнення")
        testExtract("Почати вторгнення в четвер о 0500", "2017-06-29 05:00:00", "почати вторгнення")
        testExtract("Нагадай мені встати через 4 роки", "2021-06-27 00:00:00", "нагадай мені встати")
        testExtract("Нагадай мені встати через 4 роки і 4 дні", "2021-07-01 00:00:00", "нагадай мені встати")
        # testExtract("Яка погода 3 дні після завтра?", "2017-07-01 00:00:00", "яка погода")
        testExtract("3 грудня", "2017-12-03 00:00:00", "")
        testExtract("ми зустрінемось о 8:00 сьогодні ввечері", "2017-06-27 20:00:00", "ми зустрінемось")
        testExtract("ми зустрінемось о 5pm", "2017-06-27 17:00:00", "ми зустрінемось")
        testExtract("ми зустрінемось в 5дня", "2017-06-27 17:00:00", "ми зустрінемось")
        testExtract("ми зустрінемось в 8 am", "2017-06-28 08:00:00", "ми зустрінемось")
        testExtract("ми зустрінемось о 8 ранку", "2017-06-28 08:00:00", "ми зустрінемось")
        testExtract("ми зустрінемось о 8 вечора", "2017-06-27 20:00:00", "ми зустрінемось")
        testExtract("Нагадати мені встати о 8 am", "2017-06-28 08:00:00", "нагадати мені встати")
        testExtract("Нагадати мені встати о 8 ранку", "2017-06-28 08:00:00", "нагадати мені встати")
        testExtract("Яка погода у вівторок", "2017-06-27 00:00:00", "яка погода")
        testExtract("Яка погода в понеділок", "2017-07-03 00:00:00", "яка погода")
        testExtract("Яка погода в цю середу", "2017-06-28 00:00:00", "яка погода")
        testExtract("В четвер яка погода", "2017-06-29 00:00:00", "яка погода")
        testExtract("В цей четвер яка погода", "2017-06-29 00:00:00", "яка погода")
        testExtract("в минулий понеділок яка була погода", "2017-06-26 00:00:00", "яка була погода")
        testExtract("постав будильник на середу ввечері о 8", "2017-06-28 20:00:00", "постав будильник")
        testExtract("постав будильник на середу о 3 години дня", "2017-06-28 15:00:00", "постав будильник")
        testExtract("постав будильник на середу о 3 годині ранку", "2017-06-28 03:00:00", "постав будильник")
        testExtract("постав будильник на середу зранку о 7 годині", "2017-06-28 07:00:00", "постав будильник")
        testExtract("постав будильник на сьогодні о 7 годині", "2017-06-27 19:00:00", "постав будильник")
        testExtract("постав будильник на цей вечір о 7 годині", "2017-06-27 19:00:00", "постав будильник")
        testExtract("постав будильник на цей вечір о 7:00", "2017-06-27 19:00:00", "постав будильник")
        testExtract("ввечері 5 червня 2017 нагадай мені подзвонити мамі", "2017-06-05 19:00:00",
                    "нагадай мені подзвонити мамі")
        testExtract("онови мій календар зранку побачення з юлею 4 березня", "2018-03-04 08:00:00",
                    "онови мій календар побачення з юлею")
        testExtract("Нагадай мені подзвонити мамі в наступний вівторок", "2017-07-04 00:00:00",
                    "нагадай мені подзвонити мамі")
        # testExtract("Нагадай мені подзвонити мамі за 3 тижні",
        #             "2017-07-18 00:00:00", "нагадай мені подзвонити мамі")
        testExtract("Нагадай мені подзвонити мамі через 8 тижнів", "2017-08-22 00:00:00",
                    "нагадай мені подзвонити мамі")
        testExtract("Нагадай мені подзвонити мамі через 8 тижнів і 2 дні", "2017-08-24 00:00:00",
                    "нагадай мені подзвонити мамі")
        testExtract("Нагадай мені подзвонити мамі через 4 дні", "2017-07-01 00:00:00", "нагадай мені подзвонити мамі")
        testExtract("Нагадай мені подзвонити мамі через 3 місяці",
                    "2017-09-27 00:00:00", "нагадай мені подзвонити мамі")
        testExtract("Нагадай мені подзвонити мамі через 2 роки і 2 дні",
                    "2019-06-29 00:00:00", "нагадай мені подзвонити мамі")
        testExtract("Нагадай мені подзвонити мамі на наступному тижні",
                    "2017-07-04 00:00:00", "нагадай мені подзвонити мамі")
        testExtract("Нагадай мені подзвонити мамі в 10am в суботу",
                    "2017-07-01 10:00:00", "нагадай мені подзвонити мамі")
        testExtract("Нагадай мені подзвонити мамі в 10 ранку в суботу",
                    "2017-07-01 10:00:00", "нагадай мені подзвонити мамі")
        # testExtract("Нагадай мені подзвонити мамі в 10am в цю суботу",
        #             "2017-07-01 10:00:00", "нагадай мені подзвонити мамі")
        testExtract("Нагадай мені подзвонити мамі о 10 в наступну суботу",
                    "2017-07-01 10:00:00", "нагадай мені подзвонити мамі")
        testExtract("Нагадай мені подзвонити мамі о 10am в наступну суботу",
                    "2017-07-01 10:00:00", "нагадай мені подзвонити мамі")
        testExtract("Нагадай мені подзвонити мамі о 10 ранку в наступну суботу",
                    "2017-07-01 10:00:00", "нагадай мені подзвонити мамі")
        # test yesterday
        testExtract("який був день вчора", "2017-06-26 00:00:00", "який був день")
        testExtract("який був день позавчора", "2017-06-25 00:00:00", "який був день")
        testExtract("я поснідав вчора о 6", "2017-06-26 06:00:00", "я поснідав")
        testExtract("я поснідав вчора о 6 am", "2017-06-26 06:00:00", "я поснідав")
        testExtract("я поснідав вчора о 6 ранку", "2017-06-26 06:00:00", "я поснідав")

        # Below two tests, ensure that time is picked
        # even if no am/pm is specified
        # in case of weekdays/tonight

        testExtract("постав будильник на 9 у вихідні", "2017-06-27 21:00:00", "постав будильник вихідні")
        testExtract("на 8 сьогодні ввечері", "2017-06-27 20:00:00", "")
        testExtract("на 8:30pm сьогодні ввечері", "2017-06-27 20:30:00", "")
        testExtract("на 8:30вечора сьогодні", "2017-06-27 20:30:00", "")
        testExtract("на 8:30 вечора сьогодні", "2017-06-27 20:30:00", "")
        # Tests a time with ':' & without am/pm
        testExtract("постав будильник сьогодні ввечері на 9:30", "2017-06-27 21:30:00", "постав будильник")
        testExtract("постав будильник на 9:00 сьогодні ввечері", "2017-06-27 21:00:00", "постав будильник")
        # Check if it picks intent irrespective of correctness
        testExtract("постав будильник о 9 годині сьогодні ввечері", "2017-06-27 21:00:00", "постав будильник")
        # todo
        # testExtract("Нагадай мені про гру сьогодні ввечері об 11:30", "2017-06-27 23:30:00", "нагадай мені про гру")
        testExtract("постав будильник о 7:30 на вихідних", "2017-06-27 19:30:00", "постав будильник на вихідних")

        #  "# days <from X/after X>"
        testExtract("мій день народження через 2 дні від сьогодні", "2017-06-29 00:00:00", "мій день народження")
        testExtract("мій день народження через 2 дні з сьогодні", "2017-06-29 00:00:00", "мій день народження")
        testExtract("мій день народження через 2 дні з завтра", "2017-06-30 00:00:00", "мій день народження")
        testExtract("мій день народження через 2 дня від завтра", "2017-06-30 00:00:00", "мій день народження")
        # testExtract("Нагадай мені подзвонити мамі в 10am через 2 дні після наступної суботи",
        #             "2017-07-10 10:00:00", "нагадай мені подзвонити мамі")
        testExtract("мій день народження через 2 дні зі вчора", "2017-06-28 00:00:00", "мій день народження")
        testExtract("мій день народження через 2 дні від вчора", "2017-06-28 00:00:00", "мій день народження")

        #  "# days ago>"
        testExtract("мій день народження був 1 день тому", "2017-06-26 00:00:00", "мій день народження був")
        testExtract("мій день народження був 2 дні тому", "2017-06-25 00:00:00", "мій день народження був")
        testExtract("мій день народження був 3 дні тому", "2017-06-24 00:00:00", "мій день народження був")
        testExtract("мій день народження був 4 дні тому", "2017-06-23 00:00:00", "мій день народження був")
        testExtract("мій день народження був 5 днів тому", "2017-06-22 00:00:00", "мій день народження був")
        testExtract("зустрінемось сьогодні вночі", "2017-06-27 22:00:00", "зустрінемось вночі")
        testExtract("зустрінемось пізніше вночі", "2017-06-27 22:00:00", "зустрінемось пізніше вночі")
        testExtract("Яка буде погода завтра вночі", "2017-06-28 22:00:00", "яка буде погода вночі")
        testExtract("Яка буде погода у наступний вівторок вночі", "2017-07-04 22:00:00", "яка буде погода вночі")

    def test_extract_ambiguous_time_uk(self):
        morning = datetime(2017, 6, 27, 8, 1, 2, tzinfo=default_timezone())
        evening = datetime(2017, 6, 27, 20, 1, 2, tzinfo=default_timezone())
        noonish = datetime(2017, 6, 27, 12, 1, 2, tzinfo=default_timezone())
        self.assertEqual(extract_datetime('годування риб'), None)
        self.assertEqual(extract_datetime('день'), None)
        # self.assertEqual(extract_datetime('сьогодні'), None)
        self.assertEqual(extract_datetime('місяць'), None)
        self.assertEqual(extract_datetime('рік'), None)
        self.assertEqual(extract_datetime(' '), None)
        self.assertEqual(
            extract_datetime('погодувати риб о 10 годині', morning)[0],
            datetime(2017, 6, 27, 10, 0, 0, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('погодувати риб о 10 годині', noonish)[0],
            datetime(2017, 6, 27, 22, 0, 0, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('погодувати риб о 10 годині', evening)[0],
            datetime(2017, 6, 27, 22, 0, 0, tzinfo=default_timezone()))

    def test_extract_relative_datetime_uk(self):
        def extractWithFormat(text):
            date = datetime(2017, 6, 27, 10, 1, 2, tzinfo=default_timezone())
            [extractedDate, leftover] = extract_datetime(text, date)
            extractedDate = extractedDate.strftime("%Y-%m-%d %H:%M:%S")
            return [extractedDate, leftover]

        def testExtract(text, expected_date, expected_leftover):
            res = extractWithFormat(normalize(text))
            self.assertEqual(res[0], expected_date, "for=" + text)
            self.assertEqual(res[1], expected_leftover, "for=" + text)

        testExtract("ми зустрінемось через 5 хвилин", "2017-06-27 10:06:02", "ми зустрінемось")
        # testExtract("ми зустрінемось через 5хвилин", "2017-06-27 10:06:02", "ми зустрінемось")
        testExtract("ми зустрінемось через 5 секунд", "2017-06-27 10:01:07", "ми зустрінемось")
        testExtract("ми зустрінемось через 1 годину", "2017-06-27 11:01:02", "ми зустрінемось")
        testExtract("ми зустрінемось через 2 години", "2017-06-27 12:01:02", "ми зустрінемось")
        testExtract("ми зустрінемось через 1 хвилину", "2017-06-27 10:02:02", "ми зустрінемось")
        testExtract("ми зустрінемось через 1 секунду", "2017-06-27 10:01:03", "ми зустрінемось")
        # testExtract("ми зустрінемось через 5секунд", "2017-06-27 10:01:07", "ми зустрінемось")

    def test_spaces(self):
        self.assertEqual(normalize("  ось   це   тест"), "ось це тест")
        self.assertEqual(normalize("  ось   це     тест  "), "ось це тест")
        self.assertEqual(normalize("  ось   це  один    тест"), "ось це 1 тест")

    def test_numbers(self):
        self.assertEqual(normalize("ось це один два три  тест"), "ось це 1 2 3 тест")
        self.assertEqual(normalize("  ось це чотири п'ять шість  тест"), "ось це 4 5 6 тест")
        self.assertEqual(normalize("ось це сім вісім дев'ять тест"), "ось це 7 8 9 тест")
        self.assertEqual(normalize("ось це сім вісім дев'ять  тест"), "ось це 7 8 9 тест")
        self.assertEqual(normalize("ось це десять одинадцять дванадцять тест"), "ось це 10 11 12 тест")
        self.assertEqual(normalize("ось це тринадцять чотирнадцять тест"), "ось це 13 14 тест")
        self.assertEqual(normalize("ось це п'ятнадцять шістнадцять сімнадцять"), "ось це 15 16 17")
        self.assertEqual(normalize("ось це вісімнадцять дев'ятнадцять двадцять"), "ось це 18 19 20")
        self.assertEqual(normalize("ось це один дев'ятнадцять двадцять два"), "ось це 1 19 20 2")
        self.assertEqual(normalize("ось це один сто"), "ось це 1 сто")
        self.assertEqual(normalize("ось це один два двадцять два"), "ось це 1 2 20 2")
        self.assertEqual(normalize("ось це один і половина"), "ось це 1 і половина")
        self.assertEqual(normalize("ось це один і половина і п'ять шість"), "ось це 1 і половина і 5 6")

    def test_multiple_numbers(self):
        self.assertEqual(extract_numbers("ось це один два три тест"), [1.0, 2.0, 3.0])
        self.assertEqual(extract_numbers("ось це чотири п'ять шість тест"), [4.0, 5.0, 6.0])
        self.assertEqual(extract_numbers("ось це десять одинадцять дванадцять тест"), [10.0, 11.0, 12.0])
        self.assertEqual(extract_numbers("ось це один двадцять один тест"), [1.0, 21.0])
        self.assertEqual(extract_numbers("1 собака, сім свиней, у макдонадьда "
                                         "була ферма ферма, 3 рази по 5 бургерів"), [1, 7, 3, 5])
        # self.assertEqual(extract_numbers("два пива для двох ведмедів"), [2.0, 2.0])
        self.assertEqual(extract_numbers("двадцять 20 двадцять"), [20, 20, 20])
        self.assertEqual(extract_numbers("двадцять 20 22"), [20.0, 20.0, 22.0])
        self.assertEqual(extract_numbers("двадцять двадцять два двадцять"), [20, 22, 20])
        self.assertEqual(extract_numbers("двадцять 2"), [22.0])
        self.assertEqual(extract_numbers("двадцять 20 двадцять 2"), [20, 20, 22])
        self.assertEqual(extract_numbers("третина один"), [1 / 3, 1])
        self.assertEqual(extract_numbers("третій", ordinals=True), [3])
        self.assertEqual(extract_numbers("шість трильйонів", short_scale=True), [6e12])
        self.assertEqual(extract_numbers("шість трильйонів", short_scale=False), [6e18])
        self.assertEqual(extract_numbers("двоє поросят і шість трильйонів бактерій", short_scale=True), [2, 6e12])
        self.assertEqual(extract_numbers("двоє поросят і шість трильйонів бактерsй", short_scale=False), [2, 6e18])
        self.assertEqual(extract_numbers("тридцять другий або перший", ordinals=True), [32, 1])
        self.assertEqual(extract_numbers("ось це сім вісім дев'ять і половина тест"), [7.0, 8.0, 9.5])


if __name__ == "__main__":
    unittest.main()
