# MailRobot
Automatization of sending email.  

Could use multiple modes using arguments. Run program with command:  

`python main.py <argument>` where `<argument>` is name of mode.  

To add/modify mode you should at least:  
1. Define `config.ini` first. Use format:  
```
[db]  
DB_SERVER=  
DB_NAME=  
DB_USER=  
DB_PASSWORD=  
[api]  
URL=  
AUTH_KEY=  
AUTH_VALUE=  
ICO=  
[mail]  
Email=  
Pass=  
SmtpServer=  
PortServer=  
Supervisor=  
Support=  
[directories]  
temp_dir=TEMP  
tempplates_dir=tempplates  
[files]  
report_feed=frfeed_html.txt  
report_overdue_czk=CZK_BODY.txt  
report_overdue_eur=EUR_BODY.txt  
select_frfeed=select_frfeed.sql  
select_ovedue=select_overdue.sql  
```  
  
2. Edit inside code:  
- add necessary parameters into dictionary inside `config_handler.py`  
- add condition in `def main()` function  
- add new sorting function into `sort_n_group.py`  
