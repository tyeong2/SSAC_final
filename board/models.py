from django.db import models

# Create your models here.

class Member(models.Model):
    user_email      = models.EmailField(max_length=100, verbose_name='유저 이메일')
    user_pw         = models.CharField(max_length=100, verbose_name='유저 비밀번호')
    user_created    = models.DateTimeField(auto_now_add=True, verbose_name='가입일')
    user_updated    = models.DateTimeField(auto_now=True, verbose_name='수정일')

    def __str__(self):
        return self.user_email

    class Meta:
        db_table            = 'members'
        verbose_name        = '사용자'
        verbose_name_plural = '사용자'


class Board(models.Model):
    title       = models.CharField(max_length=200, verbose_name='제목')
    contents    = models.TextField(verbose_name='내용')
    writer      = models.ForeignKey('board.Member', on_delete=models.CASCADE, verbose_name='작성자')
    created_at  = models.DateTimeField(auto_now_add=True, verbose_name='작성일')
    updated_at  = models.DateTimeField(auto_now=True, verbose_name='수정일')
    image       = models.ImageField(upload_to='images/', blank=True, null=True)
    # pip install django-imagekit
    # image       = ProcessedImageField(
    #     blank=True, processors=[Thumbnail(300, 300),], format='JPEG', options={'quality':90,}
    # )

    def __str__(self):
        return self.title

    class Meta:
        db_table            = 'boards'
        verbose_name        = '게시판'
        verbose_name_plural = '게시판'


class UserCars(models.Model):
    user_email = models.ForeignKey('board.Member', on_delete=models.CASCADE, verbose_name='유저 이메일')
    user_design = models.ImageField(width_field=512, height_field=512, verbose_name='저장 디자인')
    saved_at = models.DateTimeField(auto_now_add=True, verbose_name='저장 시각')

    class Meta:
        db_table = 'usercars'
        verbose_name = '유저 저장 이미지'
        verbose_name_plural = '유저 저장 이미지'


class Cars(models.Model):
    type = models.CharField(max_length=20, verbose_name='차종')
    brand = models.CharField(max_length=20, verbose_name='브랜드')
    design = models.ImageField(width_field=512, height_field=512, verbose_name='디자인')

    class Meta:
        db_table = 'cars'
        verbose_name = '디자인데이터'
        verbose_name_plural = '디자인데이터'
