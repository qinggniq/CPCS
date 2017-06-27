# CPCS
Car Parking Charge System (based on Python2.7)


## 部署：
1、  git clone 或 pscp上传
     
     1)
     git clone https://github.com/xurongchen/CPCS.git
     2)
     pscp D:\python root@1.2.3.4:/python

2、  安装venv虚拟环境

     LINUX命令：sudo apt-get install python-virtualenv\nMACOS命令：sudo easy_install virtualenv
     `WINDOWS命令：从 https://github.com/pypa/setuptools 下载脚本，文件夹下执行 easy_install virtualenv`
 
3、  进入venv虚拟环境

      `LINUX、MACOS命令：source venv/bin/activate`
      `WINDOWS命令：venv\Scripts\activate`
  
4、  安装所需的python包：

     `pip install -r requirements.txt`

5、  初始化数据库

    python manager.py shell
    >>>db.create_all()
    >>>Role.insert_roles()
    >>>Solution.set()
    
    数据库删除操作：
    >>>db.drop_all()
    
6、 启动服务：
    
    1）
    测试（本机127.0.0.1::5000）：
    python manager.py runserver
    或（对同级的IP开放，IP:5000）
    python manager.py runserver --host 0.0.0.0
    
    2）
    使用Gornicorn：
    gunicorn rocket:app -p rocket.pid -b 0.0.0.0:8000 -D
    停止服务进程：
    kill -HUP `cat rocket.pid`
    kill `cat rocket.pid`



