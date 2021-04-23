from django.shortcuts import render, redirect, get_object_or_404
from .models import Member, Board, Cars, Comment
from django.contrib.auth.hashers import make_password, check_password
from django.http import HttpResponse
from .forms import LoginForm, BoardForm, BoardUpdate, MemberUpdate, CommentForm
from django.http import Http404
from django.core.paginator import Paginator
from django.contrib import messages
from django.core.files.uploadedfile import InMemoryUploadedFile
from copy import deepcopy
from io import BytesIO
from PIL import Image
import os, pymongo, gridfs, cv2, random, base64, numpy as np


# Create your views here.
def register(request):
    if request.method == 'GET':
        return render(request, 'register.html')
    elif request.method == 'POST':
        user_email = request.POST.get('email')
        user_nickname = request.POST.get('nickname')
        user_pw = request.POST.get('password')
        user_pw_confirm = request.POST.get('password-check')

        res_data = {}
        #모든 값을 입력하지 않았을 때
        if (user_email is None) or (user_pw is None) or (user_pw_confirm is None) or (user_nickname == ''):
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
        # 이미 등록된 닉네임일 경우
        elif Member.objects.filter(user_nickname=user_nickname).exists():
            res_data['error'] = '이미 등록된 닉네임 입니다.'
            return render(request, 'register.html', res_data)
        else:
            #입력받은 사용자 정보를 객체를 만들어서 저장
            member = Member(
                user_email = user_email,
                user_nickname = user_nickname,
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
    user_id = request.session.get('user')
    if not user_id:
        return redirect('/board/login/')
    else:
        member = Member.objects.get(id=user_id)
        if request.method == 'POST':
            res_data = {}
            # member = Member.objects.get(pk=pk)
            nickname = request.POST.get('nickname')
            password_origin = request.POST.get('password-origin')
            password_new = request.POST.get('password-new')
            password_check = request.POST.get('password-check')
            if not (nickname and password_origin and password_new and password_check):
                res_data['error'] = '모든 값을 입력해주세요.'
                return render(request, 'mypage_update.html', res_data)
            elif not nickname:
                res_data['error'] = '닉네임을 입력해주세요.'
                return render(request, 'mypage_update.html', res_data)
            elif Member.objects.filter(user_nickname=nickname).exists():
                res_data['error'] = '이미 사용중인 닉네임 입니다.'
                return render(request, 'mypage_update.html', res_data)
            elif not check_password(password_origin, member.user_pw):
                res_data['error'] = '기존의 비밀번호가 다릅니다.'
                return render(request, 'mypage_update.html', res_data)
            elif password_new != password_check:
                res_data['error'] = '변경한 비밀번호가 서로 다릅니다.'
                return render(request, 'mypage_update.html', res_data)
            else:
                member.user_nickname = nickname
                member.user_pw = make_password(password_new)
                member.save()
                return redirect('/board/mypage/')
        else:
            form = MemberUpdate(instance=member)
        return render(request, 'mypage_update.html', {'form':form})


def home(request):
    return render(request, 'index.html')

def guide(request):
    return render(request, 'guide.html')

def aboutus(request):
    return render(request, 'aboutus.html')

def design(request):
    if request.method == 'GET':
        return render(request, 'design.html')
    else:
        # print(request.POST)
        if 'generate' in request.POST: # 생성하기 눌렀을 때
            if not request.session.get('user'):
                return redirect('/board/login/')

            # 몽고DB 클라이언트 객체 생성
            cardb = pymongo.MongoClient('mongodb://opadak:1q2w3e@13.209.75.4:27017/')['imagedb']
            fs = gridfs.GridFS(cardb)

            # 사용자로부터 원하는 차종, 브랜드 입력 받음
            type = request.POST.get('type')
            brand = request.POST.get('Brands')
            # print([type, brand])
            # 차종이나 브랜드를 선택하지 않았을 경우
            if not (type and brand):
                fail_msg = '차종과 브랜드를 모두 선택해주세요.'
                return render(request, 'design.html', {'error': fail_msg})

            # 넘겨받은 조건에 해당하는 이미지들을 가져온다.
            img_list = list(cardb[type.lower()].find({'maker': brand.lower()}))
            # print(len(img_list))

            # 랜덤하게 5장 선택
            try:
                sample_list = random.sample(img_list, 5)
            except:
                fail_msg = '조건에 부합하는 디자인을 찾지 못했습니다.'
                return render(request, 'design.html', {'error': fail_msg})
            # 이미지 파일로 다시 변환
            res_list = []
            global tmp_list # 저장할 때 사용하도록 이미지를 임시 저장
            tmp_list = []
            tmp_list.append((type,brand))
            for doc in sample_list:
                # 읽어오기
                gOut = fs.get(doc['images'][0]['imageID'])
                img = np.frombuffer(gOut.read(), dtype=np.uint8)
                img = np.reshape(img, doc['images'][0]['shape'])
                # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

                # 이미지 형식으로 변환
                im_pil = Image.fromarray(img)
                tmp_list.append(im_pil)
                buffer = BytesIO()
                im_pil.save(buffer, format='JPEG')
                buffer64 = base64.b64encode(buffer.getvalue())
                img_uri = u'data:img/jpeg;base64,'+buffer64.decode('utf-8')

                res_list.append(img_uri)
            return render(request, 'design.html', {'images':res_list})

        elif 'save' in request.POST: # 저장하기 눌렀을 때
            if not request.session.get('user'):
                return redirect('/board/login/')
            try:
                tmp_list
            except NameError:
                fail_msg = '생성된 이미지가 없습니다.'
                return render(request, 'design.html', {'error':fail_msg})
            
            #사용자 ID값 
            user_id = request.session.get('user')
            member = Member.objects.get(id=user_id)

            selected = request.POST.getlist('selected')
            # print(selected)
            DIR_BASE = os.path.join('media','user')
            os.makedirs(DIR_BASE, exist_ok=True)
            for sel in selected:
                img = tmp_list[int(sel)+1]
                flist = os.listdir(DIR_BASE)
                try:
                    i = int(flist[-1].split('.')[0])
                    fname = str(i+1).zfill(8)+'.jpg'
                except:
                    fname = str(0).zfill(8)+'.jpg'
                SAVE_PATH = os.path.join(DIR_BASE, fname)
                img.save(SAVE_PATH, format='JPEG')

                usercar = UserCar()
                usercar.member = member
                usercar.type = tmp_list[0][0]
                usercar.brand = tmp_list[0][1]
                usercar.img_path = SAVE_PATH
                usercar.save()
            return render(request, 'design.html', {'error':'성공적으로 저장되었습니다'})

def login(request):
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
    pagenator = Paginator(all_boards, 8) #all_boards 의 내용을 한 페이지당 오브젝트 8개씩
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

def vote_board_detail(request, board_id):
    board = get_object_or_404(Board, pk=board_id)

    user_id = request.session.get('user')
    x_man = Member.objects.get(pk=user_id)

    if x_man == board.writer:
        messages.error(request, '본인이 작성한 글은 추천할수 없습니다')
    else:
        board.voter.add(x_man)
    return redirect('/board/detail/'+str(board.id))

def vote_board(request, board_id):
    board = get_object_or_404(Board, pk=board_id)

    user_id = request.session.get('user')
    x_man = Member.objects.get(pk=user_id)

    if x_man == board.writer:
        messages.error(request, '본인이 작성한 글은 추천할수 없습니다')
    else:
        board.voter.add(x_man)
    return redirect('/board/list/')
