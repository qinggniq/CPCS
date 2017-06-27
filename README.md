# CPCS
Car Parking Charge System (based on Python2.7)


## 部署：
1、  git clone 或 pscp上传
     
     1) 
     <br>
     git clone https://github.com/xurongchen/CPCS.git 
     <br>
     2) 
     <br>
     pscp D:\python root@1.2.3.4:/python 
     <br>

2、  安装venv虚拟环境

     LINUX命令：sudo apt-get install python-virtualenv 
     <br>
     MACOS命令：sudo easy_install virtualenv 
     <br>
     WINDOWS命令：从 https://github.com/pypa/setuptools 下载脚本，文件夹下执行 easy_install virtualenv 
     <br>
 
3、  进入venv虚拟环境

      `LINUX、MACOS命令：source venv/bin/activate` 
      <br>
      `WINDOWS命令：venv\Scripts\activate` 
      <br>
  
4、  安装所需的python包：

     `pip install -r requirements.txt` 

5、  初始化数据库

    python manager.py shell 
    >>>db.create_all() 
    <br>
    >>>Role.insert_roles() 
    <br>
    >>>Solution.set() 
    <br>
    
    数据库删除操作： 
    <br>
    >>>db.drop_all() 
    <br>
    
6、 启动服务：
    
    1）
    <br> 
    测试（本机127.0.0.1::5000）：
    <br>
    python manager.py runserver
    <br>
    或（对同级的IP开放，IP:5000）
    <br>
    python manager.py runserver --host 0.0.0.0
    <br>
    
    2）
    <br>
    使用Gornicorn：
    <br>
    gunicorn rocket:app -p rocket.pid -b 0.0.0.0:8000 -D
    <br>
    停止服务进程：
    <br>
    kill -HUP `cat rocket.pid`
    <br>
    kill `cat rocket.pid`
    <br>



