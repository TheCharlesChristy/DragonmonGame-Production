This Version of the app is configured to run on localhost so it cannot be played by users on different networks
This Version of the app is also without most of the comments as the comments hinder the python interpreters ability to run the werkzueg workers
The werkzueg workers are like threads that run the server so even the slightest hinderance in the operational ability can have devastating effects
To set up the app:
1: Go to CreateKeys.py
2: In Run CreateKeys.py
3: Move Generated .pem files to keys folder
4: create copies of both ca-public-key and server-public-key pem files
5: change file end from .pem to .cer
6: double click on ca-public-key.cer
7: click Install Certificate
8: in certificate import wizard select install location as local machine and press next
9: in certificate import wizard choose Trusted Root Certification Authorities as certificate location
10: finish installation steps
11: Do the same for the server certificate but install it in the Intermediate Certification authorites certificate location
12: Now choose an email address you have access to or create a new random one
13: In GameServer.py on lines 22 and 26 change 'email' for the email address you have chosen
14: Generate an app password (the method for this varies from account provider) and enter that app password into line 23
15: Now test the program! Any issues contact the developer at CharlesChristy325@gmail.com