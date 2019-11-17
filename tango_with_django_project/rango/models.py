from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=128, unique=True)
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Page(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=128)
    url = models.URLField()
    views = models.IntegerField(default=0)
    last_visit = models.DateTimeField(auto_now=True)
    first_visit = models.DateTimeField()

    def __str__(self):
        return self.title


class UserProfile(models.Model):
    # 这一行是必须的
    # 建立与 User 模型之间的关系
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # 想增加的属性
    website = models.URLField(blank=True)
    # 此外，注意 ImageField 字段的 upload_to 参数。这个参数的值与项目的 MEDIA_ROOT 设置
    # （第 4 章）结合在一起，确定上传的头像存储在哪里。假如 MEDIA_ROOT 的值为
    # <workspace>/tango_with_django_project/media/，upload_to 参数的值为 profile_images，那么头
    # 像将存储在<workspace>/tango_with_django_project/media/profile_images/ 目录中。
    picture = models.ImageField(upload_to='profile_images', blank=True)

    # 覆盖 __str__() 方法，返回有意义的字符串
    # 如果使用 python2.7.x，还要返回 __unicode__ 方法
    def __str__(self):
        return self.user.username




