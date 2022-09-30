


# code = 'b8438c64c750d4be8a41e153dc242650'
# import http.client

# conn = http.client.HTTPSConnection("api.dexcom.com")

# payload = "client_secret=bjoJIHOwF4jR525s&client_id=hsOlzVkz9o18qgCxe6Gji6HEryLOUrpF&code=bd84d7958622c43a8d598ed1e1efdc98&grant_type=authorization_code&redirect_uri=http://localhost:8080/"

# headers = {
#     'content-type': "application/x-www-form-urlencoded",
#     'cache-control': "no-cache"
#     }

# conn.request("POST", "/v2/oauth2/token", payload, headers)

# res = conn.getresponse()
# data = res.read()

# print(data.decode("utf-8"))

# #https://api.dexcom.com/v2/oauth2/login?client_id=hsOlzVkz9o18qgCxe6Gji6HEryLOUrpF&redirect_uri=http://localhost:8080/&response_type=code&scope=offline_access

import http.client
access_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6ImZGT0JuMDZOcmZvamdxTEdJOXBXNUJaM2J6NCIsImtpZCI6ImZGT0JuMDZOcmZvamdxTEdJOXBXNUJaM2J6NCJ9.eyJpc3MiOiJodHRwczovL3VhbTEuZGV4Y29tLmNvbS9pZGVudGl0eSIsImF1ZCI6Imh0dHBzOi8vdWFtMS5kZXhjb20uY29tL2lkZW50aXR5L3Jlc291cmNlcyIsImV4cCI6MTY2NDUxNjM1NiwibmJmIjoxNjY0NTA5MTU2LCJjbGllbnRfaWQiOiJoc09selZrejlvMThxZ0N4ZTZHamk2SEVyeUxPVXJwRiIsInNjb3BlIjpbImNhbGlicmF0aW9uIiwiZXZlbnQiLCJvZmZsaW5lX2FjY2VzcyIsImVndiIsInN0YXRpc3RpY3MiLCJkZXZpY2UiXSwic3ViIjoiZGM3ZjVjMmItYTVmOC00NzRkLTk0NGEtZDdjMmM0ZDFhODBiIiwiYXV0aF90aW1lIjoxNjY0NTA5MTM0LCJpZHAiOiJpZHNydiIsImNvdW50cnlfY29kZSI6IlVTIiwibWlzc2luZ19maWVsZHNfY291bnQiOiIwIiwiaXNfY29uc2VudF9yZXF1aXJlZCI6ImZhbHNlIiwiY25zdCI6IjIiLCJjbnN0X2NsYXJpdHkiOiIyIiwiY25zdF90ZWNoc3VwcG9ydCI6IjIiLCJqdGkiOiIwMzk2NzNjNTI3OWRlNGFhOTZjZDk3NWFiYjc3MTU1MiIsImFtciI6WyJwYXNzd29yZCJdfQ.g4vU1tV-patjQYdppQ6a-egyZWbiFFbvNg0FzZ4klVC2QgV7hCKLgTWVTz-tMQxtyugCGDqlqaoA9hldOQMgBtmYGIEB_Dx2K4XfIG6a7w3RqXFIxjXI86Y5uBUfhyPIuDnr6NfIHpep7tqe5_Dd1YFR2nf67XIm9NdS_t_HUTsx1BmI9xiEIhe3iqa82cTEVL0XkgUrWDae1aa9FuKe_BgNbUUJHgQ_a5n0P6m5D8dVUhrV6iCdDrESS-nUtFVVHIr2cO_6wBtUqS-fnNWAH6s_3xTmJxIjeluaUbAW2jclay7Km8EtRGSH0B_tOLPXe4UNG7ntOwR9e5z8x3wdLw"

conn = http.client.HTTPSConnection("api.dexcom.com")

headers = {
    'authorization': f"Bearer {access_token}"
    }

conn.request("GET", "/v2/users/self/egvs?startDate=2022-09-29T00:00:00&endDate=2022-09-29T12:00:00", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))

##FIXME - write code to parse the information I get
#       - write code to get the current blood sugar reading
#       - 