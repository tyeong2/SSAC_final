from django.db import models

# Create your models here.

class Member(models.Model):
    user_email      = models.EmailField(max_length=100, blank=False, verbose_name='유저 이메일')
    user_nickname   = models.CharField(max_length=100, blank=False, default='NoNickname', verbose_name='유저 닉네임')
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
    writer      = models.ForeignKey('board.Member', on_delete=models.CASCADE, verbose_name='작성자', related_name='writer_board')
    created_at  = models.DateTimeField(auto_now_add=True, verbose_name='작성일')
    updated_at  = models.DateTimeField(auto_now=True, verbose_name='수정일')
    image_path  = models.CharField(max_length=100, verbose_name='게시글 사진 경로')
    image_type  = models.CharField(max_length=20, verbose_name='게시글 사진 차종')
    image_brand = models.CharField(max_length=20, verbose_name='게시글 사진 브랜드')
    hit         = models.PositiveIntegerField(default=0)
    voter = models.ManyToManyField('board.Member', related_name='voter_board')

    def __str__(self):
        return self.title
    
    @property
    def hit_up(self):
        self.hit = self.hit + 1
        self.save()

    class Meta:
        db_table            = 'boards'
        verbose_name        = '게시판'
        verbose_name_plural = '게시판'


class UserCar(models.Model):
    member      = models.ForeignKey(Member, on_delete=models.CASCADE, verbose_name='유저 이메일')
    img_type    = models.CharField(max_length=10, verbose_name='차종')
    img_brand   = models.CharField(max_length=10, verbose_name='브랜드')
    img_path    = models.CharField(max_length=100, default='/static/img/showcar.png', verbose_name='이미지 파일 경로')
    saved_at    = models.DateTimeField(auto_now_add=True, verbose_name='저장 시각')

    class Meta:
        db_table = 'usercars'
        verbose_name = '유저 저장 이미지'
        verbose_name_plural = '유저 저장 이미지'

        
class Comment(models.Model):
    author = models.ForeignKey('board.Member', on_delete=models.CASCADE)
    content = models.TextField()
    create_date = models.DateTimeField(auto_now_add=True, verbose_name='작성일')
    modify_date = models.DateTimeField(auto_now=True, null=True, blank=True)
    board = models.ForeignKey('board.Board', on_delete=models.CASCADE)
