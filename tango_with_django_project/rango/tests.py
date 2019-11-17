from django.test import TestCase
from rango.models import Category
from django.urls import reverse

# Create your tests here.


class CategoryMethodTests(TestCase):

    def test_index_view_with_no_categories(self):

        add_cat('test', 1, 1)
        add_cat('temp', 1, 1)
        add_cat('tmp', 1, 1)
        add_cat('tmp test tmp', 1, 1)

        response = self.client.get(reverse('rango:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "tmp test tmp")

        num_cats = len(response.context['categories'])
        self.assertEqual(num_cats, 4)


def add_cat(name, views, likes):
    c = Category.objects.get_or_create(name=name)[0]
    c.views = views
    c.likes = likes
    c.save()
    return c