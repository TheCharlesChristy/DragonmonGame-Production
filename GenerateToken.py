import random
import hashlib
string = "a b c d e f g h i j k l m n o p q r s t u v w x y z A B C D E F G H I J K L M N O P Q R S T U V W X Y Z 1 2 3 4 5 6 7 8 9 0 - _ = + * & ^ % $ £ ! ` ¬ # ~ < > , . ? " 
charset = string.split()

def Generate():
    CharList = []
    for i in range(128):
        CharList.append(charset[random.randint(0,81)])
    rawtoken = "".join(CharList)
    encodedtoken = rawtoken.encode()
    Token = hashlib.sha256(encodedtoken).hexdigest()
    return Token
Token = Generate()
print(type(Token))

