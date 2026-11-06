import configparser,os,sys
c=configparser.ConfigParser()
p='local.ini' if os.path.exists('local.ini') else '../../protected/shared/config.ini'
c.read(p)
t=int(c.get('app','timeout',fallback='1'))
print('timeout',t)
sys.exit(0 if t>=10 else 1)
