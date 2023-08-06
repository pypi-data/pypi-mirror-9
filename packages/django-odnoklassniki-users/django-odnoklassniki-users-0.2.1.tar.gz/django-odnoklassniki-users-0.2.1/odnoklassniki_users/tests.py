# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from django.test import TestCase
from django.utils import timezone
import mock
import simplejson as json

from .factories import UserFactory
from .models import User, USER_INFO_TIMEOUT_DAYS

USER1_ID = 561348705024
USER1_NAME = u'Евгений Дуров'

USER2_ID = 578592731938
USER_SLUG_ID = 31073078859


def user_fetch_mock(**kwargs):
    ids = kwargs.get('uids').split(',')
    users = [User.objects.get(id=id) if User.objects.filter(id=id).count() == 1 else UserFactory(id=id) for id in ids]
    ids = [user.pk for user in users]
    return User.objects.filter(pk__in=ids)


class OdnoklassnikiUsersTest(TestCase):

    def test_get_by_url(self):

        user = UserFactory(id=USER_SLUG_ID)

        self.assertEqual(User.objects.count(), 1)

        urls = (
            'http://ok.ru/ivanov/',
            'http://ok.ru/ivanov',
            'http://odnoklassniki.ru/ivanov',
            'http://www.odnoklassniki.ru/ivanov',
            'http://www.odnoklassniki.ru/profile/31073078859',
        )

        for url in urls:
            instance = User.remote.get_by_url(url)
            self.assertEqual(instance.id, USER_SLUG_ID)

    def test_refresh_user(self):

        instance = User.remote.fetch(ids=[USER1_ID])[0]
        self.assertEqual(instance.name, USER1_NAME)

        instance.name = 'temp'
        instance.save()
        self.assertEqual(instance.name, 'temp')

        instance.refresh()
        self.assertEqual(instance.name, USER1_NAME)

    def test_fetch_user(self):

        self.assertEqual(User.objects.count(), 0)

        users = User.remote.fetch(ids=[USER1_ID, USER2_ID])

        self.assertEqual(len(users), 2)
        self.assertEqual(User.objects.count(), 2)

        instance = users.get(id=USER1_ID)

        self.assertEqual(instance.id, USER1_ID)
        self.assertEqual(instance.name, USER1_NAME)
        self.assertTrue(isinstance(instance.registered_date, datetime))

    @mock.patch('odnoklassniki_api.models.OdnoklassnikiManager.fetch', side_effect=user_fetch_mock)
    def test_fetch_users_more_than_100(self, fetch):

        users = User.remote.fetch(ids=range(0, 150))

        self.assertEqual(len(users), 150)
        self.assertEqual(User.objects.count(), 150)

        self.assertEqual(len(fetch.mock_calls[0].call_list()[0][2]['uids'].split(',')), 100)
        self.assertEqual(len(fetch.mock_calls[1].call_list()[0][2]['uids'].split(',')), 50)

    @mock.patch('odnoklassniki_api.models.OdnoklassnikiManager.fetch', side_effect=user_fetch_mock)
    def test_fetching_expired_users(self, fetch):

        users = User.remote.fetch(ids=range(0, 50))

        # make all users fresh
        User.objects.all().update(fetched=timezone.now())
        # make 10 of them expired
        User.objects.filter(pk__lt=10).update(fetched=timezone.now() - timedelta(USER_INFO_TIMEOUT_DAYS + 1))

        users_new = User.remote.fetch(ids=range(0, 50), only_expired=True)

        self.assertEqual(len(fetch.mock_calls[0].call_list()[0][2]['uids'].split(',')), 50)
        self.assertEqual(len(fetch.mock_calls[1].call_list()[0][2]['uids'].split(',')), 10)
        self.assertEqual(users.count(), 50)
        self.assertEqual(users.count(), users_new.count())

    def test_parse_user(self):

        response = u'''[{
              "allows_anonym_access": true,
              "birthday": "05-11",
              "current_status": "собщество генерал шермон",
              "current_status_date": "2013-11-12 03:45:01",
              "current_status_id": "62725470887936",
              "first_name": "Евгений",
              "gender": "male",
              "has_email": false,
              "has_service_invisible": false,
              "last_name": "Дуров",
              "last_online": "2014-04-09 02:35:10",
              "locale": "r",
              "location": {"city": "Кемерово",
               "country": "RUSSIAN_FEDERATION",
               "countryCode": "RU"},
              "name": "Евгений Дуров",
              "photo_id": "508669228288",
              "pic1024x768": "http://uld1.mycdn.me/getImage?photoId=508669228288&photoType=3&viewToken=1gbG-ihJLgI5L_XujVV_6A",
              "pic128max": "http://usd1.mycdn.me/getImage?photoId=508669228288&photoType=2&viewToken=1gbG-ihJLgI5L_XujVV_6A",
              "pic128x128": "http://umd1.mycdn.me/getImage?photoId=508669228288&photoType=6&viewToken=1gbG-ihJLgI5L_XujVV_6A",
              "pic180min": "http://itd0.mycdn.me/getImage?photoId=508669228288&photoType=13&viewToken=1gbG-ihJLgI5L_XujVV_6A",
              "pic190x190": "http://i500.mycdn.me/getImage?photoId=508669228288&photoType=5&viewToken=1gbG-ihJLgI5L_XujVV_6A",
              "pic240min": "http://itd0.mycdn.me/getImage?photoId=508669228288&photoType=14&viewToken=1gbG-ihJLgI5L_XujVV_6A",
              "pic320min": "http://itd0.mycdn.me/getImage?photoId=508669228288&photoType=15&viewToken=1gbG-ihJLgI5L_XujVV_6A",
              "pic50x50": "http://i500.mycdn.me/getImage?photoId=508669228288&photoType=4&viewToken=1gbG-ihJLgI5L_XujVV_6A",
              "pic640x480": "http://uld1.mycdn.me/getImage?photoId=508669228288&photoType=0&viewToken=1gbG-ihJLgI5L_XujVV_6A",
              "pic_1": "http://i500.mycdn.me/getImage?photoId=508669228288&photoType=4&viewToken=1gbG-ihJLgI5L_XujVV_6A",
              "pic_2": "http://usd1.mycdn.me/getImage?photoId=508669228288&photoType=2&viewToken=1gbG-ihJLgI5L_XujVV_6A",
              "pic_3": "http://i500.mycdn.me/getImage?photoId=508669228288&photoType=5&viewToken=1gbG-ihJLgI5L_XujVV_6A",
              "pic_4": "http://uld1.mycdn.me/getImage?photoId=508669228288&photoType=0&viewToken=1gbG-ihJLgI5L_XujVV_6A",
              "pic_5": "http://umd1.mycdn.me/getImage?photoId=508669228288&photoType=6&viewToken=1gbG-ihJLgI5L_XujVV_6A",
              "private": false,
              "registered_date": "2012-11-05 14:13:53",
              "uid": "561348705024",
              "url_profile": "http://www.odnoklassniki.ru/profile/561348705024",
              "url_profile_mobile": "http://www.odnoklassniki.ru/profile/?st.application_key=CBAEBGLBEBABABABA&st.signature=d9867421a0017d9a08c17a206edf2730&st.reference_id=561348705024"}]'''

        instance = User()
        instance.parse(json.loads(response)[0])
        instance.save()

        self.assertEqual(instance.id, 561348705024)
        self.assertEqual(instance.name, u'Евгений Дуров')

        self.assertEqual(instance.allows_anonym_access, True)
        self.assertEqual(instance.birthday, "05-11")
        self.assertEqual(instance.current_status, u"собщество генерал шермон")
        self.assertEqual(instance.current_status_id, 62725470887936)
        self.assertEqual(instance.first_name, u"Евгений")
        self.assertEqual(instance.gender, 2)
        self.assertEqual(instance.has_email, False)
        self.assertEqual(instance.has_service_invisible, False)
        self.assertEqual(instance.last_name, u"Дуров")
        self.assertIsInstance(instance.current_status_date, datetime)
        self.assertIsInstance(instance.last_online, datetime)
        self.assertEqual(instance.locale, "r")
        self.assertEqual(instance.city, u"Кемерово")
        self.assertEqual(instance.country, "RUSSIAN_FEDERATION")
        self.assertEqual(instance.country_code, "RU")
        self.assertEqual(instance.name, u"Евгений Дуров")
        self.assertEqual(instance.photo_id, 508669228288)

        self.assertEqual(
            instance.pic1024x768, "http://uld1.mycdn.me/getImage?photoId=508669228288&photoType=3&viewToken=1gbG-ihJLgI5L_XujVV_6A")
        self.assertEqual(
            instance.pic128max, "http://usd1.mycdn.me/getImage?photoId=508669228288&photoType=2&viewToken=1gbG-ihJLgI5L_XujVV_6A")
        self.assertEqual(
            instance.pic128x128, "http://umd1.mycdn.me/getImage?photoId=508669228288&photoType=6&viewToken=1gbG-ihJLgI5L_XujVV_6A")
        self.assertEqual(
            instance.pic180min, "http://itd0.mycdn.me/getImage?photoId=508669228288&photoType=13&viewToken=1gbG-ihJLgI5L_XujVV_6A")
        self.assertEqual(
            instance.pic190x190, "http://i500.mycdn.me/getImage?photoId=508669228288&photoType=5&viewToken=1gbG-ihJLgI5L_XujVV_6A")
        self.assertEqual(
            instance.pic240min, "http://itd0.mycdn.me/getImage?photoId=508669228288&photoType=14&viewToken=1gbG-ihJLgI5L_XujVV_6A")
        self.assertEqual(
            instance.pic320min, "http://itd0.mycdn.me/getImage?photoId=508669228288&photoType=15&viewToken=1gbG-ihJLgI5L_XujVV_6A")
        self.assertEqual(
            instance.pic50x50, "http://i500.mycdn.me/getImage?photoId=508669228288&photoType=4&viewToken=1gbG-ihJLgI5L_XujVV_6A")
        self.assertEqual(
            instance.pic640x480, "http://uld1.mycdn.me/getImage?photoId=508669228288&photoType=0&viewToken=1gbG-ihJLgI5L_XujVV_6A")
        self.assertEqual(instance.private, False)
        self.assertIsInstance(instance.registered_date, datetime)
        self.assertEqual(instance.url_profile, "http://www.odnoklassniki.ru/profile/561348705024")
        self.assertEqual(instance.url_profile_mobile,
                         "http://www.odnoklassniki.ru/profile/?st.application_key=CBAEBGLBEBABABABA&st.signature=d9867421a0017d9a08c17a206edf2730&st.reference_id=561348705024")


# TODO: write tests for this method
# Unhandled error: Expecting ',' delimiter or '}': line 1 column 10954
# (char 10953) registered while executing method users.getInfo with params
# {'fields':
# 'uid,locale,first_name,last_name,name,gender,age,birthday,has_email,location,current_location,current_status,current_status_id,current_status_date,online,last_online,photo_id,pic50x50,pic128x128,pic128max,pic180min,pic240min,pic320min,pic190x190,pic640x480,pic1024x768,url_profile,url_chat,url_profile_mobile,url_chat_mobile,can_vcall,can_vmail,allows_anonym_access,allows_messaging_only_for_friends,registered_date,has_service_invisible',
# 'emptyPictures': True, 'uids':
# '271999378203,272000388754,272001585140,272003778975,272005599594,272006929516,272009502311,272009872518,272010738176,272010956165,272017935578,272021890670,272022099425,272022625341,272027381039,272027615198,272029984122,272031187365,272031416790,272032095193,272032874313,272033463394,272035568025,272036240972,272036476825,272036664236,272039618491,272043569962,272044539617,272050104406,272050675543,272052100939,272053309942,272053443392,272055555210,272055927063,272057556601,272057898018,272059564903,272061108992,272062242224,272062695314,272065709648,272066424700,272066589093,272075033228,272075308452,272078831973,272081315803,272081797716,272083677943,272083821819,272084084258,272086643897,272087448180,272087672641,272088014038,272091356325,272091967062,272096450950,272098070888,272099027169,272099110332,272103632600,272106278417,272106323566,272107979580,272108237777,272110211014,272110772502,272111318133,272114514663,272115468945,272117206874,272118450042,272118825040,272119876553,272122325554,272122687324,272123064159,272127008791,272127206825,272128252192,272134300229,272135878074,272135985236,272136809872,272137028087,272137226430,272138418262,272140746305,272142014034,272142791007,272144575066,272144606196,272144708667,272144873675,272145506615,272145941795,272146101231'}
