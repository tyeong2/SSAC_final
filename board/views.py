from django.shortcuts import render, redirect, get_object_or_404
from .models import Member, Board, Cars, Comment
from django.contrib.auth.hashers import make_password, check_password
from django.http import HttpResponse
from .forms import LoginForm, BoardForm, BoardUpdate, CommentForm
from django.http import Http404
from django.core.paginator import Paginator
from django.contrib import messages
from PIL import Image as pil
from io import BytesIO

# Create your views here.
def register(request):
    if request.method == 'GET':
        return render(request, 'register.html')
    elif request.method == 'POST':
        user_email = request.POST.get('email')
        user_pw = request.POST.get('password')
        user_pw_confirm = request.POST.get('password-check')

        res_data = {}
        #모든 값을 입력하지 않았을 때
        if (user_email is None) or (user_pw is None) or (user_pw_confirm is None):
            res_data['error'] = '모든 값을 입력해야 합니다.'
            return render(request, 'register.html', res_data)
        #입력받은 비밀번호가 다를때
        elif user_pw != user_pw_confirm:
            res_data['error'] = '비밀번호가 다릅니다.'
            return render(request, 'register.html', res_data)
        #이미 등록된 이메일 주소일 경우
        elif Member.objects.filter(user_email=user_email).exists():
            res_data['error'] = '이미 등록된 이메일 주소입니다.'
            return render(request, 'register.html', res_data)
        else:
            #입력받은 사용자 정보를 객체를 만들어서 저장
            member = Member(
                user_email = user_email,
                #비밀번호 형태로 바꾸어서 저장
                user_pw = make_password(user_pw)
            )
            member.save()
        return redirect('/')
        # return render(request, 'register.html', res_data)


def mypage(request):
    user_id = request.session.get('user')
    if not user_id:
        return redirect('/board/login/')
    else:
        member = Member.objects.get(id=user_id)
        return render(request, 'mypage.html', {'member':member})

def mypage_update(request):
    return render(request, 'mypage_update.html')


def home(request):
    '''
    user_id = request.session.get('user')
    if user_id:
        member = Member.objects.get(pk=user_id)
        return HttpResponse(member.user_email)
    return HttpResponse('Home!')
    '''
    return render(request, 'index.html')

def guide(request):
    return render(request, 'guide.html')

def aboutus(request):
    return render(request, 'aboutus.html')

def design(request):
    if request.method == 'POST':
        type = request.POST.get('type')
        brand = request.POST.get('Brands')
        cat_type = ['Hatchback', 'Sedan', 'Sports car', 'SUV', 'Van']
        cat_brand = ['AUDI', 'Bentley', 'Benz', 'BMW', 'Chervolet', 'Chrysler',
                     'Ferrari', 'Ford', 'Hyundai', 'Kia', 'Lamborghini', 'Landrover',
                     'Mini', 'Nissan', 'Porsche', 'Ssangyong', 'Toyota', 'Volkswagen']
        res = Cars.objects.filter(type=type, brand=brand)

    return render(request, 'design.html')

def login(request):
    '''
    if request.method == 'GET':
        return render(request, 'login.html')
    elif request.method == 'POST':
        user_email = request.POST.get('email')
        user_pw = request.POST.get('password')

        res_data = {}
        if not (user_email and user_pw):
            res_data['error'] = '모든 값을 입력하세요.'
        else:
            #데이터베이스에서 입력된 이메일의 사용자 정보를 가져온다.
            member = Member.objects.get(user_email=user_email)

            #비밀번호 검증
            if check_password(user_pw, member.user_pw):
                request.session['user'] = member.id
                return redirect('/')
            else:
                res_data['error'] = '비밀번호가 틀렸습니다.'
        return render(request, 'login.html', res_data)
        '''
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            # session_code 검증
            request.session['user'] = form.user_id
            return redirect('/')
    else:
        form = LoginForm()
        # 빈 클래스 인스턴스 생성
    return render(request, 'login.html', {'form' : form})


def logout(request):
    if request.session.get('user'):
        del(request.session['user'])
    return redirect('/')


def board_list(request):
    all_boards = Board.objects.all().order_by('-id')
    page = int(request.GET.get('p', 1))
    #페이지 명을 'p'라는 변수로 받고 없다면 1페이지로
    pagenator = Paginator(all_boards, 5) #all_boards 의 내용을 한 페이지당 오브젝트 2개씩
    boards = pagenator.get_page(page)
    return render(request, 'board_list.html', {'boards' : boards})


def board_write(request):
    #로그인 하지 않은 접속자인지 확인
    if not request.session.get('user'):
        return redirect('/board/login/')

    if request.method == 'POST':
        form = BoardForm(request.POST, request.FILES)
        if form.is_valid():
            user_id = request.session.get('user')
            member = Member.objects.get(pk=user_id)

            board = Board()
            board.title = form.cleaned_data['title']
            board.contents = form.cleaned_data['contents']
            board.image = form.cleaned_data['image']
            #검증 성공 시 cleaned_data 제공
            #실패시 form.error에 오류 저장

            board.writer = member
            board.save()
            return redirect('/board/list/')
    else:
        form = BoardForm()
    return render(request, 'board_write.html', {'form' : form})


def rescale(image, width):
    img = pil.open(image)

    src_width, src_height = img.size
    if src_width <= width:
        return image
    else:
        src_ratio = float(src_height) / float(src_width)
        dst_height = round(src_ratio * width)

        img = img.resize((width, dst_height), pil.BILINEAR)
        # img.save(image.name, 'PNG')
        # image.file = img

        # 이게 없으면 attribute error 발생
        # image.file.name = image.name
        # return image
        return img


def board_detail(request, pk):
    try:
        board = Board.objects.get(pk=pk)
    except Board.DoesNotExist:
        raise Http404('게시글을 찾을 수 없습니다.')
    return render(request, 'board_detail.html', {'board':board})

def board_update(request, pk):
    user_id = request.session.get('user')
    #로그인하지 않았다면
    if not user_id:
        return redirect('/board/login/')

    # 기존의 작성글 객체를 찾는다.
    board = get_object_or_404(Board, id=pk)

    if board.writer.id != user_id:
        return redirect('/board/list/')
    else:
        if request.method == 'GET':
            form = BoardUpdate(instance=board)
            return render(request, 'board_update.html', {'form':form})

        elif request.method == 'POST':
            form = BoardUpdate(request.POST, request.FILES)
            if form.is_valid():
                user_id = request.session.get('user')
                member = Member.objects.get(pk=user_id)

                board = Board.objects.get(pk=pk)
                board.title = form.cleaned_data['title']
                board.contents = form.cleaned_data['contents']
                if form.cleaned_data['image']:
                    board.image = form.cleaned_data['image']
                else:
                    board.image = board.image
                # 검증 성공 시 cleaned_data 제공
                # 실패시 form.error에 오류 저장

                board.writer = member
                board.save()
                return redirect('/board/detail/' + str(pk))

        return render(request, 'board_update.html', {'form': form})


def board_delete(request, pk):
    if not request.session.get('user'):
        return redirect('/board/login/')
    board = Board.objects.get(pk=pk)
    board.delete()
    return redirect('/board/list/')

def comment_create_board(request, board_id):
    board = get_object_or_404(Board, pk=board_id)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            user_id = request.session.get('user')
            comment.author = Member.objects.get(pk=user_id)
            comment.board = board
            comment.save()
            return redirect('/board/detail/'+str(board_id))
    else:
        form = CommentForm()
    context = {'form': form}
    return render(request, 'comment_form.html', context)


def comment_modify_board(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)

    user_id = request.session.get('user')
    x_man = Member.objects.get(pk=user_id)

    if x_man != comment.author:
        messages.error(request, '댓글수정권한이 없습니다')
        return redirect('/board/detail/'+str(comment.board.id))


    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            comment = form.save(commit=False)
            user_id = request.session.get('user')
            comment.author = Member.objects.get(pk=user_id)
            comment.save()
            return redirect('/board/detail/'+str(comment.board.id))
    else:
        form = CommentForm(instance=comment)
    context = {'form': form}
    return render(request, 'comment_form.html', context)

def comment_delete_board(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)

    user_id = request.session.get('user')
    x_man = Member.objects.get(pk=user_id)

    if x_man != comment.author:
        messages.error(request, '댓글삭제권한이 없습니다')
        print(x_man,'     ',comment.author)
        return redirect('/board/detail/'+str(comment.board.id))
    else:
        print('getetetetet')
        comment.delete()
    return redirect('/board/detail/'+str(comment.board.id))
