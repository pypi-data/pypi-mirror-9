# -*- coding: utf-8 -*-
from datetime import date, timedelta

from django.test import TestCase
import simplejson as json
from vkontakte_wall.factories import PostFactory, GroupFactory

from .models import PostStatistic

GROUP_ID = 16297716
POST_ID = '-16297716_262399'


class VkontakteWallStatisticTest(TestCase):

    def test_parse_post(self):
        response = '''{"age": [{"reach": 2153, "value": "12-18"},
                  {"reach": 1113, "value": "18-21"},
                  {"reach": 984, "value": "21-24"},
                  {"reach": 948, "value": "24-27"},
                  {"reach": 642, "value": "27-30"},
                  {"reach": 555, "value": "30-35"},
                  {"reach": 363, "value": "35-45"},
                  {"reach": 357, "value": "45-100"}],
                 "cities": [{"name": "Донецк", "reach": 38, "value": 223},
                  {"name": "Воронеж", "reach": 25, "value": 1057},
                  {"name": "Рио", "reach": 18, "value": 136},
                  {"name": "Тируванамалай", "reach": 14, "value": 427}],
                 "countries": [{"code": "RU",
                   "name": "Россия",
                   "reach": 6548,
                   "value": 1},
                  {"code": "US", "name": "США", "reach": 15, "value": 9}],
                 "day": "2014-02-27",
                 "link_clicks": 10,
                 "reach": 8243,
                 "reach_subscribers": 357,
                 "sex": [{"reach": 4420, "value": "f"}, {"reach": 3823, "value": "m"}],
                 "sex_age": [{"reach": 1141, "value": "f;12-18"},
                  {"reach": 464, "value": "f;18-21"},
                  {"reach": 513, "value": "f;21-24"},
                  {"reach": 487, "value": "f;24-27"},
                  {"reach": 355, "value": "f;27-30"},
                  {"reach": 337, "value": "f;30-35"},
                  {"reach": 243, "value": "f;35-45"},
                  {"reach": 186, "value": "f;45-100"},
                  {"reach": 1012, "value": "m;12-18"},
                  {"reach": 649, "value": "m;18-21"},
                  {"reach": 471, "value": "m;21-24"},
                  {"reach": 461, "value": "m;24-27"},
                  {"reach": 287, "value": "m;27-30"},
                  {"reach": 218, "value": "m;30-35"},
                  {"reach": 120, "value": "m;35-45"},
                  {"reach": 171, "value": "m;45-100"}]}'''

        instance = PostStatistic(post=PostFactory())
        instance.parse(json.loads(response))
        instance.save()

        self.assertEqual(instance.date, date(2014, 2, 27))
        self.assertEqual(instance.reach, 8243)
        self.assertEqual(instance.reach_subscribers, 357)
        self.assertEqual(instance.link_clicks, 10)

        self.assertEqual(instance.reach_males, 3823)
        self.assertEqual(instance.reach_females, 4420)

        self.assertEqual(instance.reach_age_18, 2153)
        self.assertEqual(instance.reach_age_18_21, 1113)
        self.assertEqual(instance.reach_age_21_24, 984)
        self.assertEqual(instance.reach_age_24_27, 948)
        self.assertEqual(instance.reach_age_27_30, 642)
        self.assertEqual(instance.reach_age_30_35, 555)
        self.assertEqual(instance.reach_age_35_45, 363)
        self.assertEqual(instance.reach_age_45, 357)

        self.assertEqual(instance.reach_males_age_18, 1012)
        self.assertEqual(instance.reach_males_age_18_21, 649)
        self.assertEqual(instance.reach_males_age_21_24, 471)
        self.assertEqual(instance.reach_males_age_24_27, 461)
        self.assertEqual(instance.reach_males_age_27_30, 287)
        self.assertEqual(instance.reach_males_age_30_35, 218)
        self.assertEqual(instance.reach_males_age_35_45, 120)
        self.assertEqual(instance.reach_males_age_45, 171)

        self.assertEqual(instance.reach_females_age_18, 1141)
        self.assertEqual(instance.reach_females_age_18_21, 464)
        self.assertEqual(instance.reach_females_age_21_24, 513)
        self.assertEqual(instance.reach_females_age_24_27, 487)
        self.assertEqual(instance.reach_females_age_27_30, 355)
        self.assertEqual(instance.reach_females_age_30_35, 337)
        self.assertEqual(instance.reach_females_age_35_45, 243)
        self.assertEqual(instance.reach_females_age_45, 186)

    def test_fetch_statistic(self):

        group = GroupFactory(remote_id=GROUP_ID)
        post = PostFactory(remote_id=POST_ID, owner=group)
        self.assertEqual(PostStatistic.objects.count(), 0)

        post.fetch_statistic(date_from=date.today() - timedelta(2), date_to=date.today())
        self.assertEqual(PostStatistic.objects.count(), 3)

        stat = PostStatistic.objects.all()[0]
        self.assertEqual(stat.date, date.today())
        self.assertTrue(stat.reach > 0)
        self.assertTrue(stat.reach_subscribers > 0)
        self.assertTrue(stat.reach_males > 0)
        self.assertTrue(stat.reach_females > 0)
