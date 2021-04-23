# SSAC_final
SSAC mini project final


# 클론
> git clone https://github.com/tyeong2/SSAC_final.git  
> cd SSAC_final  
> pip install -r requirements.txt  
> python manage.py makemigrations  
> python manage.py migrate  
> python manage.py runserver  
(AWS에서는)  
> sh run.sh  

# makemigrations 하기 전 확인사항
community/settings.py >>> SECRET KEY 입력  
board/views.py >>> mongodb IP 확인 or 변경



# 브라우저
http://127.0.0.1:8000/

AWS
http://AWS퍼블릭IP:8000/
