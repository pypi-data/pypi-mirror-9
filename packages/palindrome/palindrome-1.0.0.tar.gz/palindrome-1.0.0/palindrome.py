def reverse(text):
    return text[::-1]
text = input("Enter a string ")
try:
    text=str(text)
except:
    print ("enter only string value")
    exit()
if text==reverse(text):
    print ("palindrome!!")
else:
    print ("not a palindrome")
    
