Installation
============

1. install virtualenv
   ==================
   apt-get install python-virtualenv (debian/ubuntu)
   OR
   pip install virtualenv (others)

2. create virtualenv environment
   =============================
   cd <project-directory>
   virtualenv --system-site-packages localenv

3. use virtual environment
   =======================
   source localenv/bin/activate

4. install requirements
   ====================
   pip install -r requirements.txt

5. start application
   =================
   python LogGTK.py 
