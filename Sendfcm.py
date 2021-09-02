import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging

cred_path = os.path.join("service-account.json")
cred = credentials.Certificate(cred_path)
default_app = firebase_admin.initialize_app(cred)

class FcmToken():
    def sendFcm(registration_tokens,title,contents):
        successToken=0
        for tokeni in registration_tokens :
	        message = messaging.Message(
	        notification = messaging.Notification(
	            title=title,
	            body=contents,
	        ),
	        token=tokeni,
	        )
        try :
            response = messaging.send(message)
            print(title)
            print(contents)
            print('FCM TOKEN:',tokeni, 'SUCCCESS:', response )                
            successToken=successToken+1
        except Exception as ex:            
            print('FCM TOKEN:',tokeni, 'ERROR:',ex)                
        return successToken
       return successToken
