import unittest


from locations.models import Location


class TestLocations(unittest.TestCase):

    def test_geolocate(self):
        locate = Location(city='Loveland',
                          state='CO',
                          country='USA',
                          )

        locate.save()

        self.assertEqual(locate.latitude, 40.3977612)
        self.assertEqual(locate.longitude, -105.0749801)

    def test_state_unicode(self):
        locate = Location(city='Loveland',
                          state='CO',
                          country='USA',
                          )

        locate.save()

        self.assertEqual(locate.__str__(), 'Loveland, CO')

    def test_no_state_unicode(self):
        locate = Location(city='Rome',
                          country='Italy',
                          )

        locate.save()

        self.assertEqual(locate.__str__(), 'Rome, Italy')