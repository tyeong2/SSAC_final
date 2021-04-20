from django import forms
from django.contrib.auth.hashers import check_password
from .models import Member, Board

class LoginForm(forms.Form):
    user_email = forms.CharField(
        error_messages={'required' : '이메일을 입력하세요.'},
        max_length=100,
        label='사용자이름')
    user_pw = forms.CharField(
        error_messages={'required' : '비밀번호를 입력하세요.'},
        widget=forms.PasswordInput,
        max_length=100,
        label='비밀번호')

    def clean(self):
        cleaned_data = super().clean()
        user_email = cleaned_data.get('user_email')
        user_pw = cleaned_data.get('user_pw')

        if user_email and user_pw:
            # 입력한 이메일이 없을 경우 에외처리
            try:
                member = Member.objects.get(user_email=user_email)
            except Member.DoesNotExist:
                self.add_error('user_email', '아이디가 없습니다.')
                return
            
            if not check_password(user_pw, member.user_pw):
                self.add_error('user_pw', '비밀번호가 다릅니다.')
            else:
                self.user_id = member.id


class BoardForm(forms.Form):
    # 입력 받을 값
    title = forms.CharField(
        error_messages={'required': '제목을 입력하세요.'},
        max_length=100,
        label='게시글 제목')
    contents = forms.CharField(
        error_messages={'required': '내용을 입력하세요.'},
        widget=forms.Textarea,
        label='게시글 내용')
    image = forms.ImageField(
        label='첨부 이미지',
        widget=forms.ClearableFileInput,
        allow_empty_file=True
    )


class BoardUpdate(forms.ModelForm):
    class Meta:
        model = Board
        fields = ['title', 'contents', 'image']
